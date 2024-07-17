from resource_manager import ResourceManager


def compare_and_release_handler(event, context):
    manager = ResourceManager(
        dynamodb_table_name="ResourceClaims", s3_bucket_name="resource-target-list-bucket"
    )
    manager.compare_and_release()
