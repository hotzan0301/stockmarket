import boto3

S3BUCKET = 'YOUR_S3_BUCKET_NAME'
SUMMARYCSVFILES = ['YOUR_CSV_FILES']

def removeCsvFiles():
    s3 = boto3.client('s3')
    for file in SUMMARYCSVFILES:
        s3.delete_object(Bucket=S3BUCKET, Key=file)