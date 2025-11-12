from minio import Minio
from config import Config
import json

client = Minio(
    Config.MINIO_ENDPOINT,
    access_key=Config.MINIO_ACCESS_KEY,
    secret_key=Config.MINIO_SECRET_KEY,
    secure=False
)

policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["s3:GetObject", "s3:PutObject"],
            "Resource": ["arn:aws:s3:::pet-adoption/*"]
        }
    ]
}

client.set_bucket_policy(Config.MINIO_BUCKET, json.dumps(policy))
print("Bucket policy updated successfully")
