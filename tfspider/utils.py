import json

import botocore.session
from botocore.exceptions import ClientError
from scrapy.conf import settings


session = botocore.session.get_session()
session.set_credentials(
    access_key=settings['AWS_ACCESS_KEY'],
    secret_key=settings['AWS_SECRET_KEY']
)
client = session.create_client('s3', region_name=settings['S3_REGION'])


def load_members():
    try:
        response = client.get_object(Bucket=settings['S3_BUCKET'], Key=settings['S3_KEY'])
        members = json.loads(response['Body'].read())
    except ClientError:
        members = {}

    return members


def save_members(members):
    client.put_object(
        ACL='private',
        Bucket=settings['S3_BUCKET'],
        Key=settings['S3_KEY'],
        Body=json.dumps(members)
    )
