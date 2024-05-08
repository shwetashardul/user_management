import pytest
from unittest.mock import AsyncMock, patch
from fastapi import UploadFile
from minio.error import S3Error
from app.services.minio_service import MinioService  # Adjust import according to your project structure

@pytest.fixture
def minio_client_mock():
    with patch('your_module.minio_service.Minio') as mock:
        yield mock()

@pytest.fixture
def upload_file_mock():
    file_mock = AsyncMock(spec=UploadFile)
    file_mock.filename = "test.jpg"
    file_mock.file = AsyncMock()
    return file_mock

@pytest.mark.asyncio
async def test_upload_file_success(minio_client_mock, upload_file_mock):
    minio_client_mock.bucket_exists.return_value = True
    minio_service = MinioService("localhost:9000", "access_key", "secret_key", False)
    url = await minio_service.upload_file(upload_file_mock, "test-bucket")
    assert "http://" in url

@pytest.mark.asyncio
async def test_upload_creates_bucket_if_not_exists(minio_client_mock, upload_file_mock):
    minio_client_mock.bucket_exists.return_value = False
    minio_client_mock.make_bucket = AsyncMock()
    minio_service = MinioService("localhost:9000", "access_key", "secret_key", False)
    await minio_service.upload_file(upload_file_mock, "test-bucket")
    minio_client_mock.make_bucket.assert_called_once_with("test-bucket")

@pytest.mark.asyncio
async def test_upload_file_raises_s3error(minio_client_mock, upload_file_mock):
    minio_client_mock.bucket_exists.return_value = True
    minio_client_mock.put_object.side_effect = S3Error("Failed")
    minio_service = MinioService("localhost:9000", "access_key", "secret_key", False)
    with pytest.raises(S3Error):
        await minio_service.upload_file(upload_file_mock, "test-bucket")

@pytest.mark.asyncio
async def test_upload_file_filename_uuid_generation(minio_client_mock, upload_file_mock):
    minio_client_mock.bucket_exists.return_value = True
    minio_service = MinioService("localhost:9000", "access_key", "secret_key", False)
    url = await minio_service.upload_file(upload_file_mock, "test-bucket")
    assert ".jpg" in url

@pytest.mark.asyncio
async def test_upload_file_handles_large_files(minio_client_mock, upload_file_mock):
    minio_client_mock.bucket_exists.return_value = True
    minio_service = MinioService("localhost:9000", "access_key", "secret_key", False)
    await minio_service.upload_file(upload_file_mock, "test-bucket")
    args, kwargs = minio_client_mock.put_object.call_args
    assert kwargs['part_size'] == 10 * 1024 * 1024

@pytest.mark.asyncio
async def test_file_url_format(minio_client_mock, upload_file_mock):
    minio_client_mock.bucket_exists.return_value = True
    minio_service = MinioService("localhost:9000", "access_key", "secret_key", False)
    url = await minio_service.upload_file(upload_file_mock, "test-bucket")
    expected_url_part = "localhost:9000/test-bucket"
    assert expected_url_part in url

