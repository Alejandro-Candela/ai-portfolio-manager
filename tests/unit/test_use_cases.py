import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_use_case(client: AsyncClient) -> None:
    # Create
    resp = await client.post(
        "/api/use-cases",
        json={
            "title": "Test Use Case",
            "problem_statement": "We have a problem",
            "urgency": "medium",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "Test Use Case"
    assert data["status"] == "new"
    use_case_id = data["id"]

    # Get
    resp = await client.get(f"/api/use-cases/{use_case_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == use_case_id

    # List
    resp = await client.get("/api/use-cases")
    assert resp.status_code == 200
    ids = [uc["id"] for uc in resp.json()]
    assert use_case_id in ids

    # Patch status
    resp = await client.patch(
        f"/api/use-cases/{use_case_id}", json={"status": "evaluating"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "evaluating"


@pytest.mark.asyncio
async def test_get_nonexistent_use_case(client: AsyncClient) -> None:
    resp = await client.get("/api/use-cases/nonexistent-id")
    assert resp.status_code == 404
