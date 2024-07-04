# services/aws_s3_service.py
import boto3
import os

from botocore.exceptions import NoCredentialsError


S3_BUCKET = "vikas-shadow-bucket"
S3_REGION = "eu-north-1"
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')

s3_client = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
)

def upload_image(file_name, object_name=None):
    try:
        response = s3_client.upload_file(file_name, S3_BUCKET, object_name or file_name)
        return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{object_name or file_name}"
    except NoCredentialsError:
        return "Credentials not available"
