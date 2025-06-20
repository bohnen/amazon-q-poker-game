"""Example module for AWS Porker."""

import boto3


def hello():
    """Print a greeting message."""
    return "Hello from AWS Porker!"


def list_s3_buckets():
    """List all S3 buckets in the AWS account."""
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return buckets
