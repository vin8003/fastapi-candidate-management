import pytest
from bson import ObjectId
from fastapi import HTTPException
from fastapi_assignment.models.candidate import (
    CandidateCreate,
    CandidateInDB,
    CandidateUpdate,
)

# Test data
test_candidate = CandidateCreate(
    name="John Doe", email="john@example.com", experience=5
)

test_candidate_id = str(ObjectId())


@pytest.mark.asyncio
async def test_create_candidate_success(mock_candidate_controller, mock_collection):
    """Test successful candidate creation"""
    # Setup mock responses
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value.inserted_id = ObjectId(test_candidate_id)

    # Call the controller method
    result = await mock_candidate_controller.create_candidate(test_candidate)

    # Verify database calls
    mock_collection.find_one.assert_called_once_with({"email": test_candidate.email})
    assert mock_collection.insert_one.called

    # Verify response
    assert isinstance(result, CandidateInDB)
    assert result.email == test_candidate.email
    assert result.name == test_candidate.name
    assert not result.is_verified


@pytest.mark.asyncio
async def test_create_candidate_duplicate_email(
    mock_candidate_controller, mock_collection
):
    """Test creation with existing email"""
    # Setup mock response for existing candidate
    mock_collection.find_one.return_value = {"email": test_candidate.email}

    # Test creation with duplicate email
    with pytest.raises(HTTPException) as exc_info:
        await mock_candidate_controller.create_candidate(test_candidate)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "A candidate with this email already exists."


@pytest.mark.asyncio
async def test_get_candidate_success(mock_candidate_controller, mock_collection):
    """Test successful candidate retrieval"""
    # Setup mock response
    mock_candidate_data = {
        "_id": ObjectId(test_candidate_id),
        "name": test_candidate.name,
        "email": test_candidate.email,
        "experience": test_candidate.experience,
        "is_verified": False,
    }
    mock_collection.find_one.return_value = mock_candidate_data

    # Call the controller method
    result = await mock_candidate_controller.get_candidate(test_candidate_id)

    # Verify database call
    mock_collection.find_one.assert_called_once_with(
        {"_id": ObjectId(test_candidate_id)}
    )

    # Verify response
    assert isinstance(result, CandidateInDB)
    assert result.id == test_candidate_id
    assert result.email == test_candidate.email


@pytest.mark.asyncio
async def test_get_candidate_not_found(mock_candidate_controller, mock_collection):
    """Test retrieval of non-existent candidate"""
    # Setup mock response
    mock_collection.find_one.return_value = None

    # Test getting non-existent candidate
    with pytest.raises(HTTPException) as exc_info:
        await mock_candidate_controller.get_candidate(test_candidate_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Candidate not found"


@pytest.mark.asyncio
async def test_update_candidate_success(mock_candidate_controller, mock_collection):
    """Test successful candidate update"""
    # Setup mock responses
    update_data = CandidateUpdate(name="Updated Name")
    mock_collection.update_one.return_value.matched_count = 1
    mock_collection.find_one.return_value = {
        "_id": ObjectId(test_candidate_id),
        "name": "Updated Name",
        "email": test_candidate.email,
        "experience": test_candidate.experience,
        "is_verified": False,
    }

    # Call the controller method
    result = await mock_candidate_controller.update_candidate(
        test_candidate_id, update_data
    )

    # Verify response
    assert isinstance(result, CandidateInDB)
    assert result.name == "Updated Name"


@pytest.mark.asyncio
async def test_delete_candidate_success(mock_candidate_controller, mock_collection):
    """Test successful candidate deletion"""
    # Setup mock response
    mock_collection.delete_one.return_value.deleted_count = 1

    # Call the controller method
    result = await mock_candidate_controller.delete_candidate(test_candidate_id)

    # Verify response
    assert result["message"] == "Candidate deleted successfully"


def test_create_candidate_endpoint_integration(client, mock_collection):
    """Test the create candidate endpoint integration"""
    # Setup mock responses
    mock_collection.find_one.return_value = None
    mock_collection.insert_one.return_value.inserted_id = ObjectId(test_candidate_id)

    response = client.post(
        "/candidate",
        json={
            "name": test_candidate.name,
            "email": test_candidate.email,
            "experience": test_candidate.experience,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_candidate.email
    assert data["name"] == test_candidate.name


def test_get_candidate_endpoint_integration(client, mock_collection):
    """Test the get candidate endpoint integration"""
    # Setup mock response
    mock_collection.find_one.return_value = {
        "_id": ObjectId(test_candidate_id),
        "name": test_candidate.name,
        "email": test_candidate.email,
        "experience": test_candidate.experience,
        "is_verified": False,
    }

    response = client.get(f"/candidate/{test_candidate_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_candidate_id
    assert data["email"] == test_candidate.email
