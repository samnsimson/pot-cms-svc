from io import BytesIO
from typing import Optional
from config import config
from botocore.exceptions import ClientError
from fastapi import UploadFile
from exceptions import InternalServerError

import boto3


class S3Service:
    def __init__(self):
        self.s3 = boto3.client('s3', aws_access_key_id=config.AWS_ACCESS_KEY, aws_secret_access_key=config.AWS_SECRET_KEY, region_name=config.AWS_REGION)
        self.bucket_name = config.S3_BUCKET_NAME

    async def upload_file(self, file_key: str, file: UploadFile, metadata: Optional[dict] = None) -> bool:
        try:
            file_contents = await file.read()
            self.s3.upload_fileobj(BytesIO(file_contents), self.bucket_name, file_key, ExtraArgs={'Metadata': metadata or {}, 'ContentType': file.content_type})
            return True
        except ClientError as e:
            raise InternalServerError(detail=f"S3 upload failed: {str(e)}")

    async def delete_file(self, file_key: str) -> bool:
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError as e:
            raise InternalServerError(detail=f"S3 delete failed: {str(e)}")

    def generate_presigned_url(self, file_key: str, expires_in: int = 3600) -> Optional[str]:
        try: return self.s3.generate_presigned_url('get_object', Params={'Bucket': self.bucket_name, 'Key': file_key}, ExpiresIn=expires_in)
        except ClientError: return None
