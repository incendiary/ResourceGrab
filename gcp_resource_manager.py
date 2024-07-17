import json

import boto3
from google.oauth2 import service_account
from googleapiclient import discovery


def get_gcp_credentials():
    secret_name = "gcp/serviceAccount"
    region_name = "your-aws-region"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response["SecretString"]
    return json.loads(secret)


class GCPResourceManager:
    def __init__(self):
        secrets = get_gcp_credentials()
        credentials = service_account.Credentials.from_service_account_info(secrets)
        self.gcp_service = discovery.build("compute", "v1", credentials=credentials)
        self.gcp_regions = ["us-central1", "europe-west1"]  # Add more regions as needed

    def claim_resources(self):
        resources = []
        project = "your-gcp-project-id"

        for region in self.gcp_regions:
            addresses = self.gcp_service.addresses().list(project=project, region=region).execute()

            for address in addresses.get("items", []):
                resources.append(
                    {
                        "id": address["address"],
                        "timestamp": "2024-07-16T00:00:00Z",
                        "provider": "GCP",
                        "region": region,
                        "type": "IP",
                    }
                )

        return resources

    def release_resource(self, resource_id, resource_type):
        project = "your-gcp-project-id"
        for region in self.gcp_regions:
            try:
                if resource_type == "IP":
                    self.gcp_service.addresses().delete(
                        project=project, region=region, address=resource_id
                    ).execute()
            except Exception as e:
                print(f"Error releasing resource {resource_id}: {e}")
