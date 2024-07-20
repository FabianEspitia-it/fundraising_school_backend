import os
import boto3

from fastapi import UploadFile

from sqlalchemy.orm import Session, joinedload

import src.models as models


AWS_BUCKET = os.getenv("AWS_BUCKET")
SUPPORTED_IMAGES_TYPES = {
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/svg': 'svg'
    }


async def s3_upload(content: bytes, key: str):
    

    session = boto3.session.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key= os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token= os.getenv('AWS_SESSION_TOKEN')
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket(AWS_BUCKET)
    bucket.put_object(Key=key, Body=content)


def update_startup_photo(db: Session, startup_photo_link: str, startup_id: str) -> str:
    db.query(models.Startup).filter(models.Startup.id == startup_id).update({'photo': startup_photo_link})
