import pytest
from pydantic import ValidationError

from schemas.documents.documents_metadata import DocumentMetadataCreate


def test_document_metadata_instance_empty():
    with pytest.raises(expected_exception=ValidationError):
        DocumentMetadataCreate()


def test_document_metadata_instance_name_empty():
    with pytest.raises(expected_exception=ValidationError):
        DocumentMetadataCreate(s3_url="s3://docflow-test/name.test")


def test_document_metadata_instance_s3_url_empty():
    with pytest.raises(expected_exception=ValidationError):
        DocumentMetadataCreate(name="name.test")


def test_document_metadata_instance_s3_url_wrong():
    with pytest.raises(expected_exception=ValidationError):
        DocumentMetadataCreate(name="name.test", s3_url="s3://docflow-test")
