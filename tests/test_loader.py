"""Tests del cargador de documentos."""

import pytest
from src.document_loader import DocumentLoader


def test_load_csv(config):
    """Verifica carga de CSV."""
    loader = DocumentLoader(config.DOCUMENT_PATH)
    docs = loader.load_csv()
    assert isinstance(docs, list)
    assert len(docs) > 0


def test_split_documents(config):
    """Verifica división en chunks."""
    loader = DocumentLoader(config.DOCUMENT_PATH)
    loader.load_csv()
    chunks = loader.split_documents(chunk_size=500, overlap=50)
    assert isinstance(chunks, list)
    assert len(chunks) > 0


def test_qa_examples(config):
    """Verifica carga de Q&A."""
    loader = DocumentLoader(config.DOCUMENT_PATH)
    qa_pairs = loader.load_qa_examples()
    assert isinstance(qa_pairs, list)
