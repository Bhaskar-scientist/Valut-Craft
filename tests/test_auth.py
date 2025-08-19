import uuid

import pytest
from httpx import AsyncClient

from app.main import app


class TestAuthEndpoints:
    """Test authentication endpoints"""

    def test_app_import(self):
        """Test that the app can be imported and basic structure works"""
        assert app is not None
        assert hasattr(app, "routes")
        print("App imported successfully")

    @pytest.mark.asyncio
    async def test_signup_success(self, client):
        """Test successful user registration"""
        signup_data = {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "testpassword123",
            "organization_name": f"Test Corp {uuid.uuid4().hex[:8]}",
        }

        response = await client.post("/api/v1/auth/signup", json=signup_data)
        assert response.status_code == 201

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == signup_data["email"]

    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, client):
        """Test registration with duplicate email"""
        unique_id = uuid.uuid4().hex[:8]
        signup_data = {
            "email": f"duplicate_{unique_id}@example.com",
            "password": "testpassword123",
            "organization_name": f"Duplicate Corp {unique_id}",
        }

        # First registration should succeed
        response = await client.post("/api/v1/auth/signup", json=signup_data)
        assert response.status_code == 201

        # Second registration with same email should fail
        response = await client.post("/api/v1/auth/signup", json=signup_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        """Test successful user login"""
        # First create a user
        unique_id = uuid.uuid4().hex[:8]
        signup_data = {
            "email": f"login_{unique_id}@example.com",
            "password": "testpassword123",
            "organization_name": f"Login Corp {unique_id}",
        }

        await client.post("/api/v1/auth/signup", json=signup_data)

        # Then try to login
        login_data = {"email": signup_data["email"], "password": "testpassword123"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_signup_validation(self, client):
        """Test signup validation"""
        # Test with short password
        signup_data = {
            "email": f"validation_{uuid.uuid4().hex[:8]}@example.com",
            "password": "123",
            "organization_name": f"Validation Corp {uuid.uuid4().hex[:8]}",
        }

        response = await client.post("/api/v1/auth/signup", json=signup_data)
        assert response.status_code == 422  # Validation error

        # Test with invalid email
        signup_data = {
            "email": "invalid-email",
            "password": "testpassword123",
            "organization_name": f"Validation Corp {uuid.uuid4().hex[:8]}",
        }

        response = await client.post("/api/v1/auth/signup", json=signup_data)
        assert response.status_code == 422  # Validation error
