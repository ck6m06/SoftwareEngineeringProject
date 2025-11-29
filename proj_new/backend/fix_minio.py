import os
import json
from minio import Minio
from minio.error import S3Error

# Configuration
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'pet-adoption')
MINIO_SECURE = os.environ.get('MINIO_SECURE', 'false').lower() == 'true'

print(f"Connecting to MinIO at {MINIO_ENDPOINT}...")
print(f"Bucket: {MINIO_BUCKET}")

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def set_public_policy(bucket_name):
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
            }
        ]
    }
    try:
        client.set_bucket_policy(bucket_name, json.dumps(policy))
        print(f"✅ Successfully set public read policy for bucket '{bucket_name}'")
    except S3Error as e:
        print(f"❌ Error setting policy: {e}")

def check_minio():
    try:
        # 1. Check if bucket exists
        if not client.bucket_exists(MINIO_BUCKET):
            print(f"⚠️ Bucket '{MINIO_BUCKET}' does not exist. Creating it...")
            client.make_bucket(MINIO_BUCKET)
            print(f"✅ Bucket '{MINIO_BUCKET}' created.")
        else:
            print(f"✅ Bucket '{MINIO_BUCKET}' exists.")

        # 2. Set Public Policy
        print("Configuring bucket policy...")
        set_public_policy(MINIO_BUCKET)

        # 3. List objects to verify data
        print("\nListing objects in bucket:")
        objects = client.list_objects(MINIO_BUCKET, recursive=True)
        count = 0
        for obj in objects:
            print(f" - {obj.object_name} ({obj.size} bytes)")
            count += 1
        
        if count == 0:
            print("⚠️ Bucket is empty. No images found.")
        else:
            print(f"\n✅ Found {count} objects.")

    except S3Error as e:
        print(f"❌ MinIO Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    check_minio()
