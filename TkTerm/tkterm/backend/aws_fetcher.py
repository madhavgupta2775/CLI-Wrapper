# aws_resource_fetcher.py
import boto3

class AWSResourceFetcher:
    def __init__(self):
        # Initialize the boto3 clients for the services you need
        self.ec2_client = boto3.client('ec2')
        self.s3_client = boto3.client('s3')
        # Add other clients as needed

    def get_instance_names(self):
        try:
            response = self.ec2_client.describe_instances()
            instance_names = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    for tag in instance.get('Tags', []):
                        if tag['Key'] == 'Name':
                            instance_names.append(tag['Value'])
            return instance_names
        except Exception as e:
            return f"Error fetching instance names: {str(e)}"

    def get_instance_ids(self):
        try:
            response = self.ec2_client.describe_instances()
            instance_ids = [instance['InstanceId'] for reservation in response['Reservations'] for instance in reservation['Instances']]
            return instance_ids
        except Exception as e:
            return f"Error fetching instance IDs: {str(e)}"

    def get_bucket_names(self):
        try:
            response = self.s3_client.list_buckets()
            bucket_names = [bucket['Name'] for bucket in response['Buckets']]
            return bucket_names
        except Exception as e:
            return f"Error fetching bucket names: {str(e)}"

    # Add more methods for other resources as needed
