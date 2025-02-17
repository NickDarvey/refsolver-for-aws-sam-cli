import os
import boto3

dynamodb = boto3.resource('dynamodb')
s3 = boto3.resource('s3')

table = dynamodb.Table(os.environ['TABLE_NAME'])
bucket = s3.Bucket(os.environ['BUCKET_NAME'])

def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Example Lambda Function'
    }
