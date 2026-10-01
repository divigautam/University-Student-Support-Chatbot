"""Tests for chat endpoints: /chat, /conversations, /conversations/{id}/messages."""
import pytest


@pytest.mark.asyncio
async def test_chat_creates_new_conversation(client, auth_headers):
    """POST /chat without conversation_id creates a new conversation."""
    response = await client.post("/chat", json={
        "message": "When do exams start?"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["response"]  # non-empty AI response
    assert data["message"] == "When do exams start?"
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0


@pytest.mark.asyncio
async def test_chat_continues_existing_conversation(client, auth_headers):
    """POST /chat with conversation_id adds to existing conversation."""
    res1 = await client.post("/chat", json={
        "message": "Hello"
    }, headers=auth_headers)
    conv_id = res1.json()["conversation_id"]

    res2 = await client.post("/chat", json={
        "message": "Follow-up question",
        "conversation_id": conv_id,
    }, headers=auth_headers)
    assert res2.status_code == 200
    assert res2.json()["conversation_id"] == conv_id


@pytest.mark.asyncio
async def test_chat_invalid_conversation_id(client, auth_headers):
    """POST /chat with non-existent conversation_id returns 404."""
    response = await client.post("/chat", json={
        "message": "Hello",
        "conversation_id": 99999,
    }, headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chat_without_auth(client):
    """POST /chat without Bearer token returns 401."""
    response = await client.post("/chat", json={"message": "Hello"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_conversations(client, auth_headers):
    """GET /conversations returns the user's conversations."""
    # Create a conversation first
    await client.post("/chat", json={"message": "Test"}, headers=auth_headers)

    response = await client.get("/conversations", headers=auth_headers)
    assert response.status_code == 200
    convs = response.json()
    assert isinstance(convs, list)
    assert len(convs) >= 1


@pytest.mark.asyncio
async def test_get_conversation_messages(client, auth_headers):
    """GET /conversations/{id}/messages returns messages in the conversation."""
    res = await client.post("/chat", json={"message": "Test msg"}, headers=auth_headers)
    conv_id = res.json()["conversation_id"]

    response = await client.get(f"/conversations/{conv_id}/messages", headers=auth_headers)
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) >= 2  # user message + assistant message
    roles = [m["role"] for m in messages]
    assert "user" in roles
    assert "assistant" in roles


@pytest.mark.asyncio
async def test_get_messages_nonexistent_conversation(client, auth_headers):
    """GET /conversations/{id}/messages for non-existent conv returns 404."""
    response = await client.get("/conversations/99999/messages", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation(client, auth_headers):
    """DELETE /conversations/{id} removes the conversation."""
    res = await client.post("/chat", json={"message": "To delete"}, headers=auth_headers)
    conv_id = res.json()["conversation_id"]

    del_resp = await client.delete(f"/conversations/{conv_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    # Verify it's gone
    verify = await client.get(f"/conversations/{conv_id}/messages", headers=auth_headers)
    assert verify.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_conversation(client, auth_headers):
    """DELETE /conversations/{id} for non-existent conv returns 404."""
    response = await client.delete("/conversations/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_conversations_without_auth(client):
    """GET /conversations without token returns 401."""
    response = await client.get("/conversations")
    assert response.status_code == 401
