import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from .services.user_service import UserService  # Adjust import according to your actual path
from .models.user_model import User  # Adjust import according to your actual path

@pytest.mark.asyncio
@patch('your_module_path.user_service.UserService._execute_query')  # Correct the path
@patch('your_module_path.user_service.UserService.get_by_id')  # Correct the path
async def test_update_profile_picture_url_success(mock_get_by_id, mock_execute_query):
    # Mock the async session and other service functions
    session = AsyncMock()
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    new_url = "http://new-url.com/profile.jpg"
    user = User(id=user_id, profile_picture_url="")
    
    mock_execute_query.return_value = None
    mock_get_by_id.return_value = user

    updated_user = await UserService.update_profile_picture_url(session, user_id, new_url)
    
    # Assertions to ensure the correct data is updated and method behaves as expected
    assert updated_user.profile_picture_url == new_url
    mock_execute_query.assert_called_once()
    mock_get_by_id.assert_called_once_with(session, user_id)
    session.refresh.assert_called_once_with(user)

@pytest.mark.asyncio
@patch('your_module_path.user_service.UserService._execute_query')  # Correct the path
@patch('your_module_path.user_service.UserService.get_by_id')  # Correct the path
async def test_update_profile_picture_url_no_user(mock_get_by_id, mock_execute_query):
    session = AsyncMock()
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    new_url = "http://new-url.com/profile.jpg"
    
    mock_execute_query.return_value = None
    mock_get_by_id.return_value = None

    result = await UserService.update_profile_picture_url(session, user_id, new_url)
    
    assert result is None
    mock_get_by_id.assert_called_once_with(session, user_id)

@pytest.mark.asyncio
@patch('your_module_path.user_service.UserService._execute_query')  # Adjust
@patch('your_module_path.user_service.UserService.get_by_id')  # Adjust
async def test_update_profile_picture_url_failure(mock_get_by_id, mock_execute_query):
    session = AsyncMock()
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    new_url = "http://new-url.com/profile.jpg"
    
    mock_execute_query.side_effect = SQLAlchemyError("DB update failed")
    mock_get_by_id.return_value = None

    with pytest.raises(SQLAlchemyError):
        await UserService.update_profile_picture_url(session, user_id, new_url)
    
    mock_execute_query.assert_called_once()
    mock_get_by_id.assert_not_called()  # get_by_id should not be called because the update fails
