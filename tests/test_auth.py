import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_register_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test@1234",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data


def test_login_user(client: TestClient):
    # First register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test@1234",
            "full_name": "Test User"
        }
    )
    
    # Now login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "Test@1234"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_email(client: TestClient):
    # First register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test@1234",
            "full_name": "Test User"
        }
    )
    
    # Login with email
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "Test@1234"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent",
            "password": "wrong"
        }
    )
    assert response.status_code == 401
