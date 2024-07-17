# Resource Grab

Resource Guard is a serverless application that manages and releases resources across AWS, Azure, and GCP. It is designed to run on AWS Lambda and utilizes AWS Secrets Manager for secure credential storage.

## Project Structure

```
ResourceGuard/
├── azure_resource_manager.py
├── aws_resource_manager.py
├── gcp_resource_manager.py
├── lambda_handler.py
├── resource_manager.py
├── config.json
├── deploy_lambdas.py
├── requirements.txt
└── build/
```

## Requirements

### AWS
- **IAM Role for Lambda**: Create an IAM role with the necessary permissions for Lambda execution, and attach policies for DynamoDB, S3, and Secrets Manager access.
- **AWS CLI**: Ensure the AWS CLI is configured with appropriate credentials.

### Azure
- **Service Principal**: Create a service principal with appropriate permissions.
- **Azure SDKs**: Install `azure-identity` and `azure-mgmt-network`.

### GCP
- **Service Account**: Create a service account with appropriate permissions.
- **GCP SDKs**: Install `google-api-python-client` and `google-auth`.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/ResourceGuard.git
   cd ResourceGuard
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required Python packages:
   ```sh
   pip install -r requirements.txt
   ```

## Setting Up Authentication

### AWS

1. **Create IAM Role for Lambda**:
   - Create a role with the necessary permissions for Lambda execution.
   - Attach policies for DynamoDB, S3, and Secrets Manager access.

2. **Configure AWS CLI**:
   ```sh
   aws configure
   ```

### Azure

1. **Create a Service Principal**:
   ```sh
   az ad sp create-for-rbac --name "ResourceGuardSP" --role Contributor --scopes /subscriptions/your-subscription-id
   ```

2. **Store Service Principal Credentials in AWS Secrets Manager**:
   - Go to AWS Secrets Manager and create a new secret.
   - Store the Azure service principal credentials in the following format:
     ```json
     {
       "client_id": "your-appId",
       "client_secret": "your-password",
       "tenant_id": "your-tenant",
       "subscription_id": "your-subscription-id"
     }
     ```

### GCP

1. **Create a Service Account**:
   ```sh
   gcloud iam service-accounts create resource-guard --display-name "Resource Guard Service Account"
   ```

2. **Grant Required Roles**:
   ```sh
   gcloud projects add-iam-policy-binding your-project-id --member "serviceAccount:resource-guard@your-project-id.iam.gserviceaccount.com" --role "roles/editor"
   ```

3. **Generate and Store Service Account Key**:
   ```sh
   gcloud iam service-accounts keys create key.json --iam-account resource-guard@your-project-id.iam.gserviceaccount.com
   ```

4. **Store Service Account Key in AWS Secrets Manager**:
   - Go to AWS Secrets Manager and create a new secret.
   - Store the GCP service account key in the following format:
     ```json
     {
       "type": "service_account",
       "project_id": "your-project-id",
       "private_key_id": "your-private-key-id",
       "private_key": "your-private-key",
       "client_email": "resource-guard@your-project-id.iam.gserviceaccount.com",
       "client_id": "your-client-id",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/resource-guard%40your-project-id.iam.gserviceaccount.com"
     }
     ```

## Deploying the Lambda Functions

1. Run the deployment script:
   ```sh
   python deploy_lambdas.py
   ```

## Handling Credentials

### AWS
AWS Lambda functions automatically have access to other AWS services if assigned the appropriate IAM role. The role must have policies attached for accessing DynamoDB, S3, and Secrets Manager.

### Azure
Azure credentials are handled using a service principal. The service principal credentials are stored in AWS Secrets Manager and retrieved within the Lambda function for authentication.

### GCP
GCP credentials are managed using a service account. The service account key is stored in AWS Secrets Manager and retrieved within the Lambda function for authentication.

## Configuration Files

### `config.json`
```json
{
  "lambda_role_arn": "arn:aws:iam::your-account-id:role/your-lambda-execution-role",
  "s3_bucket_name": "resource-target-list-bucket",
  "dynamodb_table_name": "ResourceClaims",
  "lambda_functions": [
    {
      "name": "ClaimResources",
      "handler": "lambda_handler.claim_resources_handler",
      "filename": "resource_guard.zip",
      "timeout": 300
    },
    {
      "name": "CompareAndReleaseResources",
      "handler": "lambda_handler.compare_and_release_handler",
      "filename": "resource_guard.zip",
      "timeout": 300
    }
  ]
}
```

### `target_list.json`
```json
{
  "targets": [
    {
      "resource_id": "54.235.55.101",
      "region": "us-east-1",
      "provider": "AWS",
      "type": "IP"
    },
    {
      "resource_id": "my-load-balancer",
      "region": "us-west-1",
      "provider": "AWS",
      "type": "LoadBalancer"
    },
    {
      "resource_id": "35.203.128.91",
      "region": "us-central1",
      "provider": "GCP",
      "type": "IP"
    },
    {
      "resource_id": "23.102.135.246",
      "region": "resource-group-1",
      "provider": "Azure",
      "type": "IP"
    },
    {
      "resource_id": "15.223.49.81",
      "region": "ca-central-1",
      "provider": "AWS",
      "type": "IP"
    },
    {
      "resource_id": "my-gcp-load-balancer",
      "region": "europe-west1",
      "provider": "GCP",
      "type": "LoadBalancer"
    },
    {
      "resource_id": "52.187.34.11",
      "region": "resource-group-2",
      "provider": "Azure",
      "type": "IP"
    }
  ]
}
```

### Explanation

- **`resource_id`**: The unique identifier of the resource.
- **`region`**: The region or resource group where the resource is located.
- **`provider`**: The cloud service provider (e.g., AWS, GCP, Azure).
- **`type`**: The type of the resource (e.g., IP, LoadBalancer).
