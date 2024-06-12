import boto3
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os

load_dotenv()

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('REGION_NAME')
my_bucket = os.getenv('MY_BUCKET')


# S3 Client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

# Buckets and paths
source_bucket = 'udacity-dend'
destination_bucket = my_bucket

log_data_prefix = 'log-data/'
song_data_prefix = 'song-data/'
log_json_file = 'log_json_path.json'

def copy_object(key):
    copy_source = {'Bucket': source_bucket, 'Key': key}
    destination_key = key
    s3.copy(copy_source, destination_bucket, destination_key)
    print(f'Copied {key} to {destination_bucket}/{destination_key}')

def copy_prefix(prefix):
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=source_bucket, Prefix=prefix):
        if 'Contents' in page:
            with ThreadPoolExecutor() as executor:
                executor.map(lambda obj: copy_object(obj['Key']), page['Contents'])

def main():

    copy_prefix(log_data_prefix)
    copy_prefix(song_data_prefix)
    
    copy_object(log_json_file)

if __name__ == '__main__':
    main()
