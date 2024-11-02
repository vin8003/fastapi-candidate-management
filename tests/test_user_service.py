import pytest
from bson import ObjectId
from fastapi import HTTPException
from fastapi_assignment.models.user import UserCreate
from fastapi_assignment.utils.jwt_utils import get_password_hash

# Test data
test_user = UserCreate(email="test@example.com", password="testpassword123")
test_user_hash = get_password_hash("testpassword123")
test_user_id = str(ObjectId())


@pytest.mark.asyncio
async def test_register_user_success(mock_user_service, mock_collection):
    """Test successful user registration"""
    # Setup mock responses
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value.inserted_id = ObjectId(test_user_id)

    # Call the service method
    result = await mock_user_service.register_user(test_user)

    # Verify database calls
    mock_collection.find_one.assert_called_once_with({"email": test_user.email})
    assert mock_collection.insert_one.called

    # Verify response
    assert "access_token" in result
    assert result["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_user_duplicate_email(mock_user_service, mock_collection):
    """Test registration with existing email"""
    # Setup mock response for existing user
    mock_collection.find_one.return_value = {"email": test_user.email}

    # Test registration with duplicate email
    with pytest.raises(HTTPException) as exc_info:
        await mock_user_service.register_user(test_user)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already registered"


@pytest.mark.asyncio
async def test_login_user_success(mock_user_service, mock_collection):
    """Test successful user login"""
    # Setup mock response
    mock_collection.find_one.return_value = {
        "_id": ObjectId(test_user_id),
        "email": test_user.email,
        "hashed_password": test_user_hash,
    }

    # Call the service method
    result = await mock_user_service.login_user(test_user)

    # Verify database call
    mock_collection.find_one.assert_called_once_with({"email": test_user.email})

    # Verify response
    assert "access_token" in result
    assert result["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_user_invalid_credentials(mock_user_service, mock_collection):
    """Test login with invalid credentials"""
    # Setup mock response for non-existent user
    mock_collection.find_one.return_value = None

    # Test login with invalid credentials
    with pytest.raises(HTTPException) as exc_info:
        await mock_user_service.login_user(test_user)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid credentials"


def test_register_endpoint_integration(client, mock_collection):
    """Test the register endpoint integration"""
    # Setup mock responses for the endpoint
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value.inserted_id = ObjectId(test_user_id)

    response = client.post(
        "/user/register",
        json={"email": test_user.email, "password": test_user.password},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_endpoint_integration(client, mock_collection):
    """Test the login endpoint integration"""
    # Setup mock response for the endpoint
    mock_collection.find_one.return_value = {
        "_id": ObjectId(test_user_id),
        "email": test_user.email,
        "hashed_password": test_user_hash,
    }

    response = client.post(
        "/user/login", json={"email": test_user.email, "password": test_user.password}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# Create conftest.py content
def pytest_configure(config):
    """Configure pytest options"""
    config.addinivalue_line("asyncio_mode", "strict")
    config.addinivalue_line("asyncio_default_fixture_loop_scope", "function")
