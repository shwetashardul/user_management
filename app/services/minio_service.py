from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import uuid

class MinioService:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = False):
        """
        Initializes the Minio client.
        """
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    async def upload_file(self, file: UploadFile, bucket_name: str = "user-profiles") -> str:
        """
        Uploads a file to a specified Minio bucket and returns the URL.

        :param file: FastAPI UploadFile received from a client.
        :param bucket_name: The name of the bucket where the file will be stored.
        :return: URL to the uploaded file.
        """
        try:
            # Ensure the bucket exists.
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' created.")

            # Generate a unique filename using UUID.
            file_extension = file.filename.split('.')[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            
            # Upload the file to Minio
            self.client.put_object(
                bucket_name, 
                file_name, 
                file.file, 
                length=-1,  # Length set to -1 for stream to be read until EOF.
                part_size=10 * 1024 * 1024  # Part size for multipart upload (10MB).
            )

            # URL construction for directly accessing the file (replace with actual logic for your setup)
            file_url = f"http://{self.client._endpoint_url.split('//')[1]}/{bucket_name}/{file_name}"
            return file_url
        except S3Error as e:
            print(f"An error occurred while uploading to Minio: {e}")
            raise e