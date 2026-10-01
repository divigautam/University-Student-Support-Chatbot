"""Tests for authentication endpoints: /auth/register, /auth/login, /auth/me."""
import pytest


@pytest.mark.asyncio
async def test_register_valid_abes_email(client):
    """Registration with @abes.ac.in email succeeds and returns a JWT."""
    response = await client.post("/auth/register", json={
        "username": "newstudent",
        "email": "newstudent@abes.ac.in",
        "password": "securepass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_non_abes_email_rejected(client):
    """Registration with a non-@abes.ac.in email returns 400."""
    response = await client.post("/auth/register", json={
        "username": "outsider",
        "email": "outsider@gmail.com",
        "password": "password123",
    })
    assert response.status_code == 400
    assert "abes.ac.in" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client):
    """Registering twice with the same email returns 400."""
    payload = {
        "username": "dup_user1",
        "email": "duplicate@abes.ac.in",
        "password": "password123",
    }
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 200

    payload["username"] = "dup_user2"  # different username, same email
    second = await client.post("/auth/register", json=payload)
    assert second.status_code == 400


@pytest.mark.asyncio
async def test_register_duplicate_username_rejected(client):
    """Registering twice with the same username returns 400."""
    await client.post("/auth/register", json={
        "username": "samename",
        "email": "first@abes.ac.in",
        "password": "password123",
    })
    response = await client.post("/auth/register", json={
        "username": "samename",
        "email": "second@abes.ac.in",
        "password": "password123",
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_correct_credentials(client):
    """Login with correct email/password returns a JWT."""
    await client.post("/auth/register", json={
        "username": "loginuser",
        "email": "loginuser@abes.ac.in",
        "password": "mypassword",
    })
    response = await client.post("/auth/login", json={
        "email": "loginuser@abes.ac.in",
        "password": "mypassword",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Login with incorrect password returns 401."""
    await client.post("/auth/register", json={
        "username": "wrongpwuser",
        "email": "wrongpw@abes.ac.in",
        "password": "correct_password",
    })
    response = await client.post("/auth/login", json={
        "email": "wrongpw@abes.ac.in",
        "password": "wrong_password",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Login with email that doesn't exist returns 401."""
    response = await client.post("/auth/login", json={
        "email": "noone@abes.ac.in",
        "password": "doesntmatter",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_token(client, auth_headers):
    """GET /auth/me with valid Bearer token returns user info."""
    response = await client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "teststudent@abes.ac.in"
    assert data["role"] == "student"
    assert "id" in data
    assert "username" in data


@pytest.mark.asyncio
async def test_me_without_token(client):
    """GET /auth/me without token returns 401."""
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token(client):
    """GET /auth/me with garbage token returns 401."""
    response = await client.get("/auth/me", headers={
        "Authorization": "Bearer invalidtoken123"
    })
    assert response.status_code == 401
