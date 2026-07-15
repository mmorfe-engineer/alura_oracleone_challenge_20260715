"""Agente RAG con Mistral API — Production-ready."""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from mistralai.client import MistralClient
from mistralai.models.chat_message import ChatMessage

from .config import Config
from .document_loader import DocumentLoader
from .embeddings_handler import EmbeddingsHandler
from .prompts import get_system_prompt, get_question_template

logger = logging.getLogger(__name__)


class FinTechRAGAgent:
    """Agente RAG con integración Mistral real."""

    def __init__(self, config: Config):
        self.config = config
        self.loader = DocumentLoader(config.DOCUMENT_PATH)
        self.embeddings_handler = None
        self.mistral_client = None
        self.initialized = False

        # Inicializa cliente Mistral
        try:
            self.mistral_client = MistralClient(api_key=config.MISTRAL_API_KEY)
            logger.info("✅ Cliente Mistral inicializado")
        except Exception as e:
            logger.error(f"❌ Error inicializando Mistral: {e}")
            raise

    def initialize(self) -> bool:
        """Inicializa agente: carga docs y prepara ChromaDB."""
        try:
            logger.info("🚀 Inicializando Agente RAG...")

            # 1. Carga documentos CSV
            docs = self.loader.load_csv()
            if not docs:
                logger.error("❌ No documents loaded")
                return False

            # 2. Divide en chunks
            chunks = self.loader.split_documents(
                chunk_size=self.config.RAG_CHUNK_SIZE,
                overlap=self.config.RAG_CHUNK_OVERLAP
            )

            # 3. Inicializa ChromaDB y añade documentos
            self.embeddings_handler = EmbeddingsHandler(
                db_path=self.config.CHROMA_DB_PATH,
                embedding_model=self.config.EMBEDDINGS_MODEL,
                device=self.config.EMBEDDINGS_DEVICE
            )
            self.embeddings_handler.add_documents(chunks)

            # 4. Carga Q&A ejemplos
            self.loader.load_qa_examples()

            self.initialized = True
            logger.info("✅ Agente RAG inicializado correctamente")
            return True

        except Exception as e:
            logger.error(f"❌ Error inicializando agente: {e}")
            self.initialized = False
            return False

    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """Busca documentos relevantes."""
        if not self.initialized:
            logger.warning("⚠️ Agent no inicializado")
            return []

        return self.embeddings_handler.search(query, top_k=top_k)

    def answer_question(self, question: str) -> Dict:
        """Pipeline RAG completo: búsqueda → contexto → LLM → respuesta."""
        if not self.initialized:
            return {
                "success": False,
                "question": question,
                "answer": "Agente no inicializado.",
                "sources": [],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": "Agent not initialized",
            }

        try:
            logger.info(f"❓ Pregunta: {question}")

            # 1. RETRIEVAL: Busca documentos relevantes
            search_results = self.search_documents(question, top_k=self.config.RAG_TOP_K)

            if not search_results:
                logger.warning("❌ No relevant documents found")
                return {
                    "success": False,
                    "question": question,
                    "answer": "No encontré información sobre esa pregunta en las políticas disponibles.",
                    "sources": [],
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat(),
                }

            # 2. AUGMENTATION: Prepara contexto
            context = "\n\n".join([
                f"[Sección: {r['section']}]\n{r['content']}"
                for r in search_results
            ])

            sources = [
                f"Sección: {r['section']} | Subsección: {r['subsection']} (Score: {r['score']:.2f})"
                for r in search_results
            ]

            # 3. GENERATION: Llama Mistral
            question_prompt = get_question_template().format(
                context=context,
                question=question
            )

            logger.info("🔄 Llamando Mistral API...")

            response = self.mistral_client.chat(
                model=self.config.MISTRAL_MODEL,
                messages=[
                    ChatMessage(role="system", content=get_system_prompt()),
                    ChatMessage(role="user", content=question_prompt),
                ],
                temperature=self.config.MISTRAL_TEMPERATURE,
                max_tokens=self.config.MISTRAL_MAX_TOKENS,
            )

            answer = response.choices[0].message.content
            confidence = search_results[0]["score"]

            logger.info(f"✅ Respuesta generada (confidence: {confidence:.2f})")

            return {
                "success": True,
                "question": question,
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "top_documents": [
                    {
                        "content": r["content"][:150] + "...",
                        "score": r["score"],
                        "section": r["section"],
                    }
                    for r in search_results[:3]
                ],
            }

        except Exception as e:
            logger.error(f"❌ Error en RAG pipeline: {e}")
            return {
                "success": False,
                "question": question,
                "answer": f"Error procesando pregunta: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    def get_agent_info(self) -> Dict:
        """Retorna info del agente."""
        return {
            "name": "BDT RAG Agent",
            "version": "1.0.0",
            "status": "initialized" if self.initialized else "not_initialized",
            "documents_loaded": self.embeddings_handler.count() if self.embeddings_handler else 0,
            "model": self.config.MISTRAL_MODEL,
            "llm_type": "Mistral API (Real)",
            "vector_db": "ChromaDB (Persistent)",
            "capabilities": [
                "Responder preguntas sobre políticas BDT",
                "Búsqueda semántica con embeddings",
                "Generación con LLM Mistral",
                "Explicar límites, comisiones y servicios",
            ],
        }
