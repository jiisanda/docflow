import pytest
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.exceptions import HTTP_404
from app.db.repositories.documents.documents_metadata import DocumentMetadataRepository


@pytest.mark.asyncio
async def test_upload_document_metadata(async_client: AsyncSession, upload_document_metadata):
    document = upload_document_metadata()
    repository = DocumentMetadataRepository(async_client)

    response = await async_client.post(
        "/api/document-metadata/documents",
        json=document.dict()
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == document.name
    assert response.json()["s3_url"] == document.s3_url
    assert UUID(response.json()["_id"])


@pytest.mark.asyncio
async def test_get_documents_metadata(async_client: AsyncSession, upload_document_metadata):
    document = upload_document_metadata()
    repository = DocumentMetadataRepository(async_client)
    await repository.upload(document)

    response = await repository.doc_list()

    assert isinstance(response, list)
    assert response[0].name == document.name
    assert response[0].s3_url == document.s3_url


@pytest.mark.asyncio
async def test_get_document_metadata(async_client: AsyncSession, upload_document_metadata):
    document = upload_document_metadata()
    repository = DocumentMetadataRepository(async_client)

    document_uploaded = await repository.upload(document)
    response = await repository.get(document=document.id)

    assert document_uploaded == response


@pytest.mark.asyncio
async def test_get_document_metadata_not_found(async_client: AsyncSession):
    repository = DocumentMetadataRepository(async_client)

    with pytest.raises(expected_exception=HTTP_404()):
        await repository.get(document=uuid4())


@pytest.mark.asyncio
async def test_soft_delete_transaction(async_client: AsyncSession, upload_document_metadata):
    document = upload_document_metadata()
    repository = DocumentMetadataRepository(async_client)

    response = await repository.upload(document)

    delete_response = await repository.delete(document=response.id)

    assert delete_response is None
    with pytest.raises(expected_exception=HTTP_404()):
        await repository.get(document=response.id)
