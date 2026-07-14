"""Cargador de documentos CSV — Production-ready."""

import pandas as pd
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Carga documentos CSV y prepara para RAG."""

    def __init__(self, document_path: str):
        self.document_path = Path(document_path)
        self.documents = []
        self.qa_pairs = []
        self.metadata = {}

    def load_csv(self) -> List[Dict]:
        """Lee CSV y retorna documentos estructurados."""
        try:
            logger.info(f"📂 Cargando documento: {self.document_path}")

            if not self.document_path.exists():
                logger.error(f"❌ Archivo no encontrado: {self.document_path}")
                raise FileNotFoundError(f"Documento no encontrado: {self.document_path}")

            df = pd.read_csv(self.document_path, encoding="utf-8")
            self.documents = self._transform_to_documents(df)

            logger.info(f"✅ Cargados {len(self.documents)} documentos")
            return self.documents

        except Exception as e:
            logger.error(f"❌ Error cargando documento: {e}")
            raise

    def _transform_to_documents(self, df: pd.DataFrame) -> List[Dict]:
        """Transforma filas CSV en documentos RAG."""
        documents = []

        for idx, row in df.iterrows():
            doc = {
                "id": f"doc_{row.get('document_id', idx)}",
                "section": str(row.get("section", "unknown")),
                "subsection": str(row.get("subsection", "")),
                "content": str(row.get("content", "")),
                "page": int(row.get("page", 0)),
                "metadata": {
                    "source": "bdt_policies",
                    "section": str(row.get("section", "")),
                    "subsection": str(row.get("subsection", "")),
                    "page": int(row.get("page", 0)),
                }
            }
            if doc["content"].strip():
                documents.append(doc)

        logger.info(f"✅ Transformados {len(documents)} documentos")
        return documents

    def load_qa_examples(self, qa_path: str = "./data/qa_examples.json") -> List[Dict]:
        """Carga Q&A ejemplos para pruebas."""
        try:
            qa_path = Path(qa_path)
            if not qa_path.exists():
                logger.warning(f"⚠️ Q&A file no encontrado: {qa_path}")
                return []

            with open(qa_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.qa_pairs = data.get("qa_pairs", [])

            logger.info(f"✅ Cargados {len(self.qa_pairs)} Q&A pairs")
            return self.qa_pairs

        except Exception as e:
            logger.error(f"❌ Error cargando Q&A: {e}")
            return []

    def split_documents(self, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
        """Divide documentos en chunks con overlap."""
        chunks = []

        for doc in self.documents:
            content = doc["content"]
            words = content.split()

            # Sliding window con overlap
            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i:i + chunk_size]
                if chunk_words and len(" ".join(chunk_words)) > 50:  # Min length
                    chunks.append({
                        "id": f"{doc['id']}_chunk_{i//(chunk_size-overlap)}",
                        "content": " ".join(chunk_words),
                        "section": doc["section"],
                        "subsection": doc["subsection"],
                        "page": doc["page"],
                        "metadata": doc["metadata"],
                    })

        logger.info(f"✅ Divididos en {len(chunks)} chunks")
        return chunks
