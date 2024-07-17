import json
import os
import subprocess
import zipfile

import boto3


def load_config(config_file):
    with open(config_file, "r") as f:
        return json.load(f)


def prepare_deployment_package(build_dir, requirements_file, source_files):
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    subprocess.check_call([f"pip", "install", "-r", requirements_file, "-t", build_dir])

    for source_file in source_files:
        subprocess.check_call(["cp", source_file, build_dir])

    zip_filename = "resource_guard.zip"
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for root, _, files in os.walk(build_dir):
            for file in files:
                filepath = os.path.join(root, file)
                zipf.write(filepath, os.path.relpath(filepath, build_dir))

    return zip_filename


def deploy_lambda_function(
    lambda_client, function_name, handler, zip_filename, timeout, environment_variables
):
    with open(zip_filename, "rb") as zip_file:
        zip_data = zip_file.read()

    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime="python3.8",
            Role=environment_variables["LAMBDA_ROLE_ARN"],
            Handler=handler,
            Code={"ZipFile": zip_data},
            Timeout=timeout,
            Environment={"Variables": environment_variables},
        )
        print(f"Created Lambda function: {function_name}")
    except lambda_client.exceptions.ResourceConflictException:
        response = lambda_client.update_function_code(FunctionName=function_name, ZipFile=zip_data)
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Handler=handler,
            Timeout=timeout,
            Environment={"Variables": environment_variables},
        )
        print(f"Updated Lambda function: {function_name}")


def add_s3_trigger(lambda_client, s3_client, function_name, bucket_name):
    notification = {
        "LambdaFunctionConfigurations": [
            {
                "LambdaFunctionArn": lambda_client.get_function(FunctionName=function_name)[
                    "Configuration"
                ]["FunctionArn"],
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {"Key": {"FilterRules": [{"Name": "suffix", "Value": "json"}]}},
            }
        ]
    }
    s3_client.put_bucket_notification_configuration(
        Bucket=bucket_name, NotificationConfiguration=notification
    )
    print(f"Added S3 trigger for function: {function_name}")


def main():
    config = load_config("config.json")

    lambda_client = boto3.client("lambda")
    s3_client = boto3.client("s3")

    build_dir = "./build"
    requirements_file = "requirements.txt"

    source_files = ["lambda_handler.py", "resource_manager.py", "config.json"]

    if "AWS" in config["csp"]:
        source_files.append("aws_resource_manager.py")
    if "GCP" in config["csp"]:
        source_files.append("gcp_resource_manager.py")
    if "Azure" in config["csp"]:
        source_files.append("azure_resource_manager.py")

    zip_filename = prepare_deployment_package(build_dir, requirements_file, source_files)

    for function in config["lambda_functions"]:
        deploy_lambda_function(
            lambda_client,
            function["name"],
            function["handler"],
            zip_filename,
            function["timeout"],
            {
                "DYNAMODB_TABLE_NAME": config["dynamodb_table_name"],
                "S3_BUCKET_NAME": config["s3_bucket_name"],
                "LAMBDA_ROLE_ARN": config["lambda_role_arn"],
            },
        )

        if function["name"] == "CompareAndReleaseResources":
            add_s3_trigger(lambda_client, s3_client, function["name"], config["s3_bucket_name"])


if __name__ == "__main__":
    main()
