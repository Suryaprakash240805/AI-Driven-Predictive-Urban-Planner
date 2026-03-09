import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        reg = await ac.post("/api/v1/auth/register", json={
            "name":"Test Citizen","email":"test@city.in",
            "password":"secret123","role":"citizen","city":"Nashik","state":"Maharashtra"
        })
        assert reg.status_code == 201

        login = await ac.post("/api/v1/auth/login", json={
            "email":"test@city.in","password":"secret123","role":"citizen"
        })
        assert login.status_code == 200
        data = login.json()
        assert "access_token" in data
        assert data["user"]["role"] == "citizen"

@pytest.mark.asyncio
async def test_login_wrong_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/auth/login", json={
            "email":"test@city.in","password":"wrongpass","role":"citizen"
        })
        assert resp.status_code == 401
