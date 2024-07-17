from resource_manager import ResourceManager


def claim_resources_handler(event, context):
    manager = ResourceManager(
        dynamodb_table_name="ResourceClaims", s3_bucket_name="resource-target-list-bucket"
    )
    manager.claim_resources()
