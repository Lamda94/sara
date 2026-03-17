import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "sara"


@pytest.mark.asyncio
async def test_info(client):
    response = await client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "whisper_model" in data
    assert "speaker_embedding_dim" in data
