import json

import boto3


class ResourceManager:
    def __init__(self, dynamodb_table_name, s3_bucket_name):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(dynamodb_table_name)
        self.s3 = boto3.client("s3")
        self.s3_bucket_name = s3_bucket_name

    def load_target_list(self):
        file_key = "target_list.json"
        target_list_obj = self.s3.get_object(Bucket=self.s3_bucket_name, Key=file_key)
        target_list = json.loads(target_list_obj["Body"].read().decode("utf-8"))
        return target_list["targets"]

    def compare_and_release(self):
        targets = self.load_target_list()

        response = self.table.scan()
        claimed_resources = response.get("Items", [])

        for resource in claimed_resources:
            if not any(
                t["resource_id"] == resource["ResourceID"]
                and t["provider"] == resource["Provider"]
                and t["type"] == resource["Type"]
                for t in targets
            ):
                self.release_resource(
                    resource["ResourceID"], resource["Provider"], resource["Type"]
                )
                self.table.update_item(
                    Key={"ResourceID": resource["ResourceID"]},
                    UpdateExpression="set Status=:s",
                    ExpressionAttributeValues={":s": "released"},
                )

    def release_resource(self, resource_id, provider, resource_type):
        if provider == "AWS":
            from aws_resource_manager import AWSResourceManager

            aws_manager = AWSResourceManager()
            aws_manager.release_resource(resource_id, resource_type)
        elif provider == "GCP":
            from gcp_resource_manager import GCPResourceManager

            gcp_manager = GCPResourceManager()
            gcp_manager.release_resource(resource_id, resource_type)
        elif provider == "Azure":
            from azure_resource_manager import AzureResourceManager

            azure_manager = AzureResourceManager()
            azure_manager.release_resource(resource_id, resource_type)
