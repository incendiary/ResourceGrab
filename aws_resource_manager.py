import boto3


class AWSResourceManager:
    def __init__(self):
        self.aws_regions = ["us-east-1", "us-west-1"]  # Add more regions as needed

    def claim_resources(self):
        resources = []

        for region in self.aws_regions:
            ec2 = boto3.client("ec2", region_name=region)
            elb = boto3.client("elbv2", region_name=region)

            # Claim IP addresses
            addresses = ec2.describe_addresses()
            for address in addresses["Addresses"]:
                resources.append(
                    {
                        "id": address["PublicIp"],
                        "timestamp": "2024-07-16T00:00:00Z",
                        "provider": "AWS",
                        "region": region,
                        "type": "IP",
                    }
                )

            # Claim Load Balancer names
            load_balancers = elb.describe_load_balancers()
            for lb in load_balancers["LoadBalancers"]:
                resources.append(
                    {
                        "id": lb["LoadBalancerName"],
                        "timestamp": "2024-07-16T00:00:00Z",
                        "provider": "AWS",
                        "region": region,
                        "type": "LoadBalancer",
                    }
                )

        return resources

    def release_resource(self, resource_id, resource_type):
        ec2 = boto3.client("ec2")
        elb = boto3.client("elbv2")

        if resource_type == "IP":
            ec2.release_address(PublicIp=resource_id)
        elif resource_type == "LoadBalancer":
            elb.delete_load_balancer(LoadBalancerName=resource_id)
