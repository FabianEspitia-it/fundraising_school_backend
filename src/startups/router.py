import os
import boto3
import magic

from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from src.database import get_db
from src.startups.crud import s3_upload, SUPPORTED_IMAGES_TYPES, Session


startup_router = APIRouter()


@startup_router.post("/startup/{startup_id}", tags=["startup"])
async def upload_startup_photo(startup_id: str | None = None, startup_photo: UploadFile = File(...), db: Session = Depends(get_db)) -> JSONResponse:

    content = await startup_photo.read()
    size = len(content)

    KB = 1024
    MB = 1024 * KB
    if not 0 < size <= 1 * MB:
        raise HTTPException(
            status_code=400,
            detail="Supported file sizes is 0 - 1 MB"
        )

    supported_image_types = SUPPORTED_IMAGES_TYPES

    file_type = magic.from_buffer(buffer=content, mime=True)
    if file_type not in supported_image_types:
        raise HTTPException(
            status_code=400,
            detail=f'Unsupported file type: {file_type}. Supported file types are: {supported_image_types.keys()}'
        )
    
    await s3_upload(content= content, key= f'{startup_id}.{supported_image_types[file_type]}')
    
    aws_bucket_name = os.getenv("AWS_BUCKET")
    bucket_link: str = f'S3://{aws_bucket_name}/{startup_id}.{file_type}'
    upload_startup_photo(db, startup_id=startup_id, startup_photo=bucket_link)

    return JSONResponse(content={"bucket_link": bucket_link}, status_code=status.HTTP_201_CREATED)
