import pytest
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from db.errors import EntityDoesNotExist
from db.repositories.document_metadata import DocumentMetadataRepository
from schemas.document_metadata import DocumentMetadataPatch

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
    await repository.upload_document_metadata(document)

    response = await repository.list()

    assert isinstance(response, list)
    assert response[0].name == document.name
    assert response[0].s3_url == document.s3_url


@pytest.mark.asyncio
async def test_get_document_metadata(async_client: AsyncSession, upload_document_metadata):
    document = upload_document_metadata()
    repository = DocumentMetadataRepository(async_client)

    document_uploaded = await repository.upload_document_metadata(document)
    response = await repository.get_document_metadata(document_id=document.id)

    assert document_uploaded == response


@pytest.mark.asyncio
async def test_get_document_metadata_not_found(async_client: AsyncSession):
    repository = DocumentMetadataRepository(async_client)

    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get_document_metadata(document_id=uuid4())


@pytest.mark.asyncio
async def test_soft_delete_transaction(async_client: AsyncSession, upload_document_metadata):
    document = upload_document_metadata()
    repository = DocumentMetadataRepository(async_client)

    response = await repository.upload_document_metadata(document)

    delete_response = await repository.delete_document_metadata(document_id=response.id)

    assert delete_response is None
    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get_document_metadata(document_id=response.id)
