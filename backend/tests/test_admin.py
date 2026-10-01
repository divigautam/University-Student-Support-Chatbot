"""Tests for admin endpoints: /admin/documents/*."""
import io
import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_upload_document(client, admin_headers):
    """Admin can upload a PDF document."""
    pdf_content = b"%PDF-1.4 dummy pdf content"
    files = {"file": ("test_upload.pdf", io.BytesIO(pdf_content), "application/pdf")}
    response = await client.post(
        "/admin/documents/upload", headers=admin_headers, files=files
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_upload.pdf"
    assert data["status"] == "processing"
    assert "id" in data


@pytest.mark.asyncio
async def test_upload_non_pdf_rejected(client, admin_headers):
    """Uploading a non-PDF file returns 400."""
    files = {"file": ("notes.txt", io.BytesIO(b"text content"), "text/plain")}
    response = await client.post(
        "/admin/documents/upload", headers=admin_headers, files=files
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_documents(client, admin_headers):
    """Admin can list all documents."""
    response = await client.get("/admin/documents", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_delete_document(client, admin_headers):
    """Admin can delete a document."""
    # Upload first
    files = {"file": ("to_delete.pdf", io.BytesIO(b"%PDF-1.4 data"), "application/pdf")}
    upload_res = await client.post(
        "/admin/documents/upload", headers=admin_headers, files=files
    )
    doc_id = upload_res.json()["id"]

    # Delete
    with patch("routers.admin.os.path.exists", return_value=False):
        del_res = await client.delete(
            f"/admin/documents/{doc_id}", headers=admin_headers
        )
    assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_delete_nonexistent_document(client, admin_headers):
    """Deleting a non-existent document returns 404."""
    response = await client.delete("/admin/documents/99999", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_reindex_document(client, admin_headers):
    """Admin can re-index a document."""
    # Upload first
    files = {"file": ("reindex_me.pdf", io.BytesIO(b"%PDF-1.4 data"), "application/pdf")}
    upload_res = await client.post(
        "/admin/documents/upload", headers=admin_headers, files=files
    )
    doc_id = upload_res.json()["id"]

    response = await client.post(
        f"/admin/documents/{doc_id}/reindex", headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "reindexing started"


@pytest.mark.asyncio
async def test_non_admin_cannot_list_documents(client, auth_headers):
    """Student user gets 403 when accessing admin endpoints."""
    response = await client.get("/admin/documents", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_non_admin_cannot_upload(client, auth_headers):
    """Student user gets 403 when trying to upload documents."""
    files = {"file": ("test.pdf", io.BytesIO(b"%PDF"), "application/pdf")}
    response = await client.post(
        "/admin/documents/upload", headers=auth_headers, files=files
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_cannot_access_admin(client):
    """Unauthenticated requests to admin endpoints get 401."""
    response = await client.get("/admin/documents")
    assert response.status_code == 401
