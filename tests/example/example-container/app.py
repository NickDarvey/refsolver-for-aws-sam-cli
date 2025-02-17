import os
import boto3
from flask import Flask

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb')
s3 = boto3.resource('s3')

table = dynamodb.Table(os.environ['TABLE_NAME'])
bucket = s3.Bucket(os.environ['BUCKET_NAME'])

@app.route('/')
def hello():
    return 'Example Container Service'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
