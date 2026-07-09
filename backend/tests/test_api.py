import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_shorten_url_valid(client: AsyncClient):
    payload = {"original_url": "https://google.com"}
    response = await client.post("/api/v1/shorten", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["original_url"] == "https://google.com"
    assert "short_code" in data
    assert len(data["short_code"]) == 6

@pytest.mark.asyncio
async def test_shorten_url_invalid(client: AsyncClient):
    payload = {"original_url": "not-a-valid-url"}
    response = await client.post("/api/v1/shorten", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

@pytest.mark.asyncio
async def test_get_urls(client: AsyncClient):
    await client.post("/api/v1/shorten", json={"original_url": "https://google.com"})
    await client.post("/api/v1/shorten", json={"original_url": "https://github.com"})
    
    response = await client.get("/api/v1/urls")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

@pytest.mark.asyncio
async def test_redirect_to_url(client: AsyncClient):
    response_create = await client.post("/api/v1/shorten", json={"original_url": "https://google.com"})
    short_code = response_create.json()["short_code"]

    response = await client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://google.com"

@pytest.mark.asyncio
async def test_redirect_not_found(client: AsyncClient):
    response = await client.get("/nonexistentcode")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_url(client: AsyncClient):
    response_create = await client.post("/api/v1/shorten", json={"original_url": "https://google.com"})
    url_id = response_create.json()["id"]

    response_delete = await client.delete(f"/api/v1/urls/{url_id}")
    assert response_delete.status_code == 204

    response_get = await client.get("/api/v1/urls")
    assert all(item["id"] != url_id for item in response_get.json())

@pytest.mark.asyncio
async def test_delete_url_not_found(client: AsyncClient):
    import uuid
    response = await client.delete(f"/api/v1/urls/{uuid.uuid4()}")
    assert response.status_code == 404
