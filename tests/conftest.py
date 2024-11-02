import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from fastapi_assignment.routers.candidate import CandidateController
from fastapi_assignment.routers.user import UserService
from fastapi_assignment.utils.dependencies import get_database


@pytest.fixture
def mock_collection():
    """Create a mock collection with async operations"""
    collection = AsyncMock()
    collection.find_one = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.delete_one = AsyncMock()

    # Mock cursor behavior for `find`
    mock_cursor = AsyncMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.to_list.return_value = []
    collection.find.return_value = mock_cursor
    return collection


@pytest.fixture
def mock_db(mock_collection):
    """Create a mock database with collection access"""
    db = AsyncMock()
    db.__getitem__.return_value = mock_collection
    db.candidates = mock_collection
    return db


@pytest.fixture
def mock_candidate_controller(mock_db):
    """Create a CandidateController instance with mock database"""
    return CandidateController(mock_db)


@pytest.fixture
def mock_user_service(mock_db):
    """Create a UserService instance with mock database"""
    return UserService(mock_db)


@pytest.fixture
def app(mock_db):
    """Create a test FastAPI application with mocked dependencies"""
    from fastapi import FastAPI
    from fastapi_assignment.routers.candidate import router as candidate_router
    from fastapi_assignment.routers.user import router as user_router

    app = FastAPI()
    app.include_router(candidate_router)
    app.include_router(user_router)

    async def override_get_database():
        return mock_db

    app.dependency_overrides[get_database] = override_get_database
    return app


@pytest.fixture
def client(app):
    """Create a test client"""
    return TestClient(app)
