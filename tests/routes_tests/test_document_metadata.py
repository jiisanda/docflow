from uuid import UUID

import pytest

from fastapi import status

from db.repositories.documents_metadata import DocumentMetadataRepository


@pytest.mark.asyncio
async def test_get_documents_metadata(async_client):
    response = await async_client.get("/api/document_metadata/documents-metadata")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == 0


@pytest.mark.asyncio
async def test_upload_document_metadata(async_client, upload_document_metadata):
    document = upload_document_metadata()
    response = await async_client.post(
        "/api/document_metadata/upload-document-metadata",
        json=document.dict()
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == document.name
    assert response.json()["s3_url"] == document.s3_url
    assert UUID(response.json()["_id"])


@pytest.mark.asyncio
async def test_get_document_metadata(async_client, upload_document_metadata):
    document = upload_document_metadata()
    response_create = await async_client.post(
        "/api/document-metadata/documents",
        json=document.dict()
    )
    response = await async_client.get(
        f"/api/document-metadata/documents/{response_create.json()['_id']}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == document.name
    assert response.json()["s3_url"] == document.s3_url
    assert response.json()["_id"] == response_create.json()["_id"]


@pytest.mark.asyncio
async def test_delete_document_metadata(async_client, upload_document_metadata):
    document = upload_document_metadata()
    response_create = await async_client.post(
        "/api/document-metadata/documents",
        json=document.dict()
    )
    response = await async_client.delete(
        f"/api/document-metadata/documents/{response_create.json()['_id']}"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_update_document_metadata(async_client, upload_document_metadata):
    document = upload_document_metadata(name="test_update.pdf", s3_url="s3://docflow-test/test_update.pdf")
    response_create = await async_client.post(
        "/api/document-metadata/documents",
        json=document.dict()
    )

    new_name = "new_test_update.pdf"
    new_s3_url = "s3://docflow-test/new_test_update.pdf"
    response = await async_client.post(
        "/api/document-metadata/documents",
        json={
            "name": new_name,
            "s3_url": new_s3_url,
        }
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == new_name
    assert response.json()["s3_url"] == new_s3_url
    assert response.json()["_id"] == response_create.json()["_id"]


@pytest.mark.asyncio
async def test_get_document_paginated(db_session, async_client, upload_document_client):
    repository = DocumentMetadataRepository(db_session)
    for document in upload_document_client(_qty=4):
        await (repository.upload(document))

    response_page_1 = await async_client.get("/api/document-metadata/documents?limit=2&offset=2")
    assert len(response_page_1.json()) == 2

    response_page_2 = await async_client.get("/api/document-metadata/documents?limit=2&offset=2")
    assert len(response_page_2.json()) == 2

    response = await async_client.get("/api/document_metadata/documents")
    assert len(response.json()) == 4
