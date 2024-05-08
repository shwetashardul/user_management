import pytest
from fastapi import HTTPException, UploadFile
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.routers.user_routes import upload_profile_picture  # Adjust import according to your actual path

@pytest.mark.asyncio
@patch('path.to.get_db')  # Correct the path according to your project structure
@patch('path.to.UserService')  # Correct the path according to your project structure
@patch('path.to.minio_service')  # Correct the path according to your project structure
async def test_upload_profile_picture_success(mock_minio_service, mock_user_service, mock_get_db):
    # Mock dependencies
    db = AsyncMock(spec=AsyncSession)
    mock_get_db.return_value = db
    mock_user_service.exists_by_id.return_value = True
    mock_user_service.update_profile_picture_url.return_value = True
    mock_minio_service.upload_file.return_value = 'http://minio.url/test.jpg'
    file_mock = AsyncMock(spec=UploadFile)
    file_mock.filename = "test.jpg"
    
    # Call the endpoint function
    response = await upload_profile_picture(UUID('12345678-1234-5678-1234-567812345678'), file_mock, db)
    
    assert response == {"url": 'http://minio.url/test.jpg', "message": "Profile picture updated successfully"}
    mock_minio_service.upload_file.assert_called_once_with(file_mock)
    mock_user_service.update_profile_picture_url.assert_called_once()

@pytest.mark.asyncio
@patch('path.to.get_db')  # Adjust the path as needed
@patch('path.to.UserService')  # Adjust the path as needed
async def test_upload_profile_picture_user_not_found(mock_user_service, mock_get_db):
    db = AsyncMock(spec=AsyncSession)
    mock_get_db.return_value = db
    mock_user_service.exists_by_id.return_value = False
    
    with pytest.raises(HTTPException) as exc_info:
        await upload_profile_picture(UUID('12345678-1234-5678-1234-567812345678'), AsyncMock(spec=UploadFile), db)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"

@pytest.mark.asyncio
@patch('path.to.get_db')
@patch('path.to.UserService')
@patch('path.to.minio_service')
async def test_upload_profile_picture_update_failure(mock_minio_service, mock_user_service, mock_get_db):
    db = AsyncMock(spec=AsyncSession)
    mock_get_db.return_value = db
    mock_user_service.exists_by_id.return_value = True
    mock_user_service.update_profile_picture_url.return_value = False
    mock_minio_service.upload_file.return_value = 'http://minio.url/test.jpg'
    
    with pytest.raises(HTTPException) as exc_info:
        await upload_profile_picture(UUID('12345678-1234-5678-1234-567812345678'), AsyncMock(spec=UploadFile), db)
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Failed to update user profile"
