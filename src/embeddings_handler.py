"""Handler de embeddings con ChromaDB — Production-ready."""

import logging
import chromadb
from typing import List, Dict, Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingsHandler:
    """Gestiona ChromaDB y embeddings reales."""

    def __init__(
        self,
        db_path: str = "./chroma_data",
        collection_name: str = "bdt_policies",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu"
    ):
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self.db_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"📚 Inicializando ChromaDB en {self.db_path}")
        logger.info(f"🧠 Embedding model: {embedding_model}")

        # Inicializa cliente ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_path))

        # Carga modelo de embeddings
        self.embedding_model = SentenceTransformer(embedding_model, device=device)

        # Obtiene o crea colección
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"✅ ChromaDB inicializado ({self.collection.count()} docs)")

    def add_documents(self, documents: List[Dict]) -> None:
        """Añade documentos a ChromaDB con embeddings."""
        logger.info(f"📝 Añadiendo {len(documents)} documentos a ChromaDB...")

        try:
            ids = []
            embeddings = []
            metadatas = []
            documents_text = []

            for doc in documents:
                ids.append(doc["id"])
                documents_text.append(doc["content"])
                metadatas.append({
                    "section": doc.get("section", ""),
                    "subsection": doc.get("subsection", ""),
                    "page": str(doc.get("page", 0)),
                })

            # Genera embeddings (puede tomar tiempo en primera vez)
            logger.info("🔄 Generando embeddings...")
            embeddings_array = self.embedding_model.encode(
                documents_text,
                show_progress_bar=True
            ).tolist()

            # Añade a ChromaDB
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings_array,
                documents=documents_text,
                metadatas=metadatas
            )

            logger.info(f"✅ {len(documents)} documentos añadidos a ChromaDB")

        except Exception as e:
            logger.error(f"❌ Error añadiendo documentos: {e}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Búsqueda semántica en ChromaDB."""
        try:
            logger.debug(f"🔍 Buscando: '{query}' (top_k={top_k})")

            # Genera embedding de la query
            query_embedding = self.embedding_model.encode([query])[0].tolist()

            # Busca en ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            # Formatea resultados
            formatted_results = []
            if results["documents"] and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    distance = results["distances"][0][i]
                    score = 1 - (distance / 2)  # Convierte distance a similarity

                    formatted_results.append({
                        "content": doc,
                        "score": max(0, score),
                        "section": results["metadatas"][0][i].get("section", ""),
                        "subsection": results["metadatas"][0][i].get("subsection", ""),
                        "page": results["metadatas"][0][i].get("page", "0"),
                    })

            logger.debug(f"✅ {len(formatted_results)} resultados encontrados")
            return formatted_results

        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            return []

    def count(self) -> int:
        """Retorna cantidad de documentos."""
        return self.collection.count()
