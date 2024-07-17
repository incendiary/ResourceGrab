import json

import boto3
from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient


def get_secret():
    secret_name = "azure/servicePrincipal"
    region_name = "your-aws-region"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response["SecretString"]
    return json.loads(secret)


class AzureResourceManager:
    def __init__(self):
        secrets = get_secret()
        credential = ClientSecretCredential(
            tenant_id=secrets["tenant_id"],
            client_id=secrets["client_id"],
            client_secret=secrets["client_secret"],
        )
        self.azure_client = NetworkManagementClient(credential, secrets["subscription_id"])
        self.azure_resource_groups = [
            "resource-group-1",
            "resource-group-2",
        ]  # Add more resource groups as needed

    def claim_resources(self):
        resources = []

        for resource_group in self.azure_resource_groups:
            public_ips = self.azure_client.public_ip_addresses.list(resource_group)

            for ip in public_ips:
                resources.append(
                    {
                        "id": ip.ip_address,
                        "timestamp": "2024-07-16T00:00:00Z",
                        "provider": "Azure",
                        "region": resource_group,
                        "type": "IP",
                    }
                )

        return resources

    def release_resource(self, resource_id, resource_type):
        for resource_group in self.azure_resource_groups:
            if resource_type == "IP":
                self.azure_client.public_ip_addresses.begin_delete(
                    resource_group, resource_id
                ).result()
