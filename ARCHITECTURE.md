# 🏗️ BDT RAG Agent - Arquitectura Técnica

**Versión:** 1.0.0  
**Fecha:** Julio 2026  
**Autor:** Morfe Flores

---

## 📋 Tabla de Contenidos

1. [Visión General](#-visión-general)
2. [Diagrama de Arquitectura](#-diagrama-de-arquitectura)
3. [Componentes Principales](#-componentes-principales)
4. [Flujo de Datos](#-flujo-de-datos)
5. [Stack Tecnológico](#-stack-tecnológico)
6. [Configuración](#-configuración)
7. [Despliegue](#-despliegue)

---

## 🎯 Visión General

El **BDT RAG Agent** es un sistema de **Retrieval-Augmented Generation (RAG)** que permite a los usuarios hacer preguntas en lenguaje natural sobre las políticas, tarifas, límites y servicios del Banco Digital de los Trabajadores (BDT).

El sistema utiliza:
- **Mistral API** como LLM para generación de respuestas
- **ChromaDB** como vector database para almacenar y buscar documentos
- **Sentence Transformers** para generar embeddings locales
- **Streamlit** como interfaz de usuario

---

## 🏗️ Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                           USUARIO                                  │
│                    (Navegador Web/Móvil)                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI (Puerto 8501)                     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  - Interfaz conversacional                                   ││
│  │  - Tema púrpura personalizado                               ││
│  │  - Gestión de estado de sesión                              ││
│  │  - Visualización de respuestas + fuentes                    ││
│  └─────────────────────────────────────────────────────────────┘│
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENTE RAG (src/agent.py)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  DocumentLoader  │  │ EmbeddingsHandler│  │ MistralClient    │  │
│  │  (CSV Processing)│  │  (ChromaDB)      │  │  (API Real)      │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼───────────────────┼───────────────────┼──────────────────┘
            │                   │                   │
            ▼                   ▼                   ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│  CSV Files           │ │  ChromaDB            │ │  Mistral API         │
│  (data/bdt_*.csv)    │ │  (chroma_data/)      │ │  (External Service)  │
│                     │ │  - Persistent        │ │  - Codestral 7B     │
│  - Secciones        │ │  - Cosine Similarity │ │  - Temperature 0.3  │
│  - Subsecciones     │ │  - Top-K Search      │ │  - Max Tokens 1024  │
│  - Contenido        │ │                     │ │                     │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

---

## 🧩 Componentes Principales

### 1. **DocumentLoader** (`src/document_loader.py`)

**Responsabilidad:** Cargar y procesar documentos CSV

**Funcionalidades:**
- Carga archivos CSV con políticas BDT
- Transforma filas en documentos estructurados
- Divide documentos en chunks con overlap (500 palabras, overlap 50)
- Carga ejemplos Q&A para pruebas

**Ejemplo de Documento:**
```python
{
    "id": "doc_BDT_003_1",
    "section": "3_TRANSACCIONES_LIMITES",
    "subsection": "3.1_LIMITES_DIARIOS",
    "content": "Límite de transacciones enviadas: USD 5,000 diarios...",
    "page": 1,
    "metadata": {"source": "bdt_policies", "section": "...", "page": 1}
}
```

### 2. **EmbeddingsHandler** (`src/embeddings_handler.py`)

**Responsabilidad:** Gestión de embeddings y vector database

**Funcionalidades:**
- Inicializa ChromaDB persistent
- Genera embeddings con Sentence Transformers (`all-MiniLM-L6-v2`)
- Almacena documentos en ChromaDB
- Realiza búsquedas semánticas (cosine similarity)
- Retorna documentos con scores de similitud

**Proceso de Búsqueda:**
1. Recibe query del usuario
2. Genera embedding de la query
3. Busca en ChromaDB los top-K documentos más similares
4. Retorna resultados con metadata y scores

### 3. **FinTechRAGAgent** (`src/agent.py`)

**Responsabilidad:** Pipeline RAG completo

**Flujo:**
1. **Initialization:**
   - Carga documentos CSV
   - Genera chunks
   - Almacena en ChromaDB con embeddings

2. **Question Processing:**
   - Recibe pregunta del usuario
   - Busca documentos relevantes (Retrieval)
   - Construye contexto con documentos
   - Genera respuesta con Mistral API (Generation)
   - Retorna respuesta con fuentes y confidence

**Ejemplo de Respuesta:**
```python
{
    "success": True,
    "question": "¿Cuál es el límite de transferencias?",
    "answer": "El límite es USD 10,000 diarios...",
    "sources": ["Sección: 3_TRANSACCIONES_LIMITES..."],
    "confidence": 0.95,
    "timestamp": "2026-07-15T10:30:00",
    "top_documents": [...]
}
```

### 4. **Streamlit UI** (`ui/streamlit_app.py`)

**Responsabilidad:** Interfaz de usuario interactiva

**Características:**
- Diseño responsive con tema púrpura
- Input de preguntas con ejemplos
- Visualización de respuestas formateadas
- Métricas de confianza y documentos consultados
- Fuentes y documentos similares expandibles
- Sidebar con información del agente

---

## 📊 Flujo de Datos

### Pipeline RAG

```
1. USER INPUT
   │
   ▼
2. EMBEDDING GENERATION  ← Sentence Transformers
   │  Query → Vector (384 dimensions)
   │
   ▼
3. RETRIEVAL  ← ChromaDB
   │  - Cosine similarity search
   │  - Top-5 documentos más relevantes
   │
   ▼
4. CONTEXT BUILDING
   │  - Combina documentos recuperados
   │  - Formatea con secciones y metadata
   │
   ▼
5. PROMPT CONSTRUCTION
   │  - System prompt (instrucciones BDT)
   │  - Question template (contexto + pregunta)
   │
   ▼
6. LLM GENERATION  ← Mistral API
   │  - Modelo: mistral-large
   │  - Temperature: 0.3
   │  - Max tokens: 1024
   │
   ▼
7. RESPONSE FORMATTING
   │  - Extrae respuesta del LLM
   │  - Añade fuentes y confidence
   │  - Formatea para UI
   │
   ▼
8. USER OUTPUT  ← Streamlit
   - Respuesta final
   - Fuentes consultadas
   - Métricas (confianza, documentos, tiempo)
```

### Ejemplo Completo

**Input:** "¿Cuál es el límite diario de transferencias?"

**Proceso:**

1. **Embedding:**
   ```
   Query: "¿Cuál es el límite diario de transferencias?"
   Vector: [0.234, -0.567, 0.890, ..., 0.123]  # 384 dimensiones
   ```

2. **Retrieval (ChromaDB):**
   ```
   Resultados:
   - Doc 1: 3_TRANSACCIONES_LIMITES/3.1 (Score: 0.94)
   - Doc 2: 3_TRANSACCIONES_LIMITES/3.2 (Score: 0.87)
   - Doc 3: 2_TERMINOS_CONDICIONES/2.4 (Score: 0.72)
   ```

3. **Context:**
   ```
   [Sección: 3_TRANSACCIONES_LIMITES]
   Límite de transacciones enviadas: USD 5,000 diarios...
   
   [Sección: 3_TRANSACCIONES_LIMITES]
   Límite de transferencias: USD 10,000 diarios...
   ```

4. **LLM Call:**
   ```
   System: Eres un asistente experto en políticas BDT...
   User: Basándote en este contexto: <CONTEXTO>...
         Pregunta del usuario: ¿Cuál es el límite diario de transferencias?
   ```

5. **Output:**
   ```
   Respuesta: "El límite de transferencias en BDT es USD 10,000 diarios..."
   Confianza: 94%
   Fuentes: [3_TRANSACCIONES_LIMITES/3.1, 3_TRANSACCIONES_LIMITES/3.2]
   ```

---

## 🛠️ Stack Tecnológico

### Capas y Tecnologías

| Capa | Tecnología | Versión | Propósito |
|------|------------|---------|-----------|
| **LLM** | Mistral API | v1 | Generación de respuestas |
| **Embeddings** | Sentence Transformers | 2.2.2 | Generación de vectors |
| **Vector DB** | ChromaDB | 0.4.10 | Almacenamiento y búsqueda |
| **RAG Framework** | Custom | 1.0.0 | Pipeline RAG |
| **UI** | Streamlit | 1.28.1 | Interfaz de usuario |
| **Deploy** | Render.com | Free | Hosting público |
| **Lenguaje** | Python | 3.11+ | Backend |
| **Testing** | Pytest | 7.4.3 | Tests unitarios |

### Dependencias Principales

```
# Core
python-dotenv==1.0.0
pydantic==2.4.2

# LLM & RAG
mistralai==0.0.11
chromadb==0.4.10

# Embeddings
sentence-transformers==2.2.2

# Data
pandas==2.1.1

# UI
streamlit==1.28.1

# Testing
pytest==7.4.3
pytest-cov==4.1.0
```

---

## ⚙️ Configuración

### Variables de Entorno

```bash
# .env
MISTRAL_API_KEY=sk_your_mistral_api_key_here
APP_ENV=development
STREAMLIT_SERVER_PORT=8501
LOG_LEVEL=INFO
DEBUG=false
DOCUMENT_PATH=./data/bdt_fintech_policies.csv
CHROMA_DB_PATH=./chroma_data
```

### Parámetros Configurables

| Parámetro | Valor Default | Descripción |
|-----------|---------------|-------------|
| `MISTRAL_MODEL` | mistral-large | Modelo de Mistral |
| `MISTRAL_TEMPERATURE` | 0.3 | Creatividad del LLM |
| `MISTRAL_MAX_TOKENS` | 1024 | Máximo tokens de respuesta |
| `RAG_TOP_K` | 5 | Documentos a recuperar |
| `RAG_CHUNK_SIZE` | 500 | Tamaño de chunks (palabras) |
| `RAG_CHUNK_OVERLAP` | 50 | Overlap entre chunks |
| `EMBEDDINGS_MODEL` | all-MiniLM-L6-v2 | Modelo de embeddings |
| `EMBEDDINGS_DEVICE` | cpu | Dispositivo (cpu/cuda) |

---

## ☁️ Despliegue

### Arquitectura de Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                        RENDER.COM                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Web Service (Free Tier)                     ││
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  ││
│  │  │  Docker         │  │  Streamlit       │  │  ChromaDB   │  ││
│  │  │  Container      │  │  Server         │  │  (Disk 1GB) │  ││
│  │  │                 │  │  (Port 8501)    │  │             │  ││
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬─────┘  ││
│  └───────────┼────────────────────┼───────────────────┼─────────┘
│              │                    │                   │
│              ▼                    ▼                   ▼
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐
│  │ GitHub           │  │ Mistral API      │  │ Persistent  │
│  │ (Repository)     │  │ (External)       │  │ Storage     │
│  └─────────────────┘  └─────────────────┘  └─────────────┘
└─────────────────────────────────────────────────────────────────┘
```

### Configuración Render.com

**Service Settings:**
- **Type:** Web Service
- **Name:** bdt-rag-agent
- **Environment:** Python 3.11
- **Plan:** Free
- **Region:** Auto

**Build Settings:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `streamlit run ui/streamlit_app.py --server.port=8501 --server.address=0.0.0.0`

**Environment Variables:**
- `MISTRAL_API_KEY` = [Tu API key de Mistral]
- `APP_ENV` = production
- `STREAMLIT_SERVER_PORT` = 8501

**Persistent Disk:**
- **Name:** chroma-db
- **Mount Path:** /app/chroma_data
- **Size:** 1 GB

### URL de Producción

```
https://bdt-rag-agent.onrender.com
```

---

## 📈 Métricas de Performance

### Tiempos de Respuesta

| Operación | Tiempo Promedio | Notas |
|-----------|-----------------|-------|
| Embedding Generation | ~0.5s | Sentence Transformers local |
| ChromaDB Search | ~0.1s | Top-5 documentos |
| Mistral API Call | ~1-1.5s | Dependiendo de carga |
| **Total (End-to-End)** | **~1.5-2.5s** | Incluye todo el pipeline |

### Recursos Utilizados

| Recurso | Local | Render Free |
|---------|-------|-------------|
| CPU | 10-20% | 20-40% |
| RAM | 500-800MB | 512-1024MB |
| Almacenamiento | ~100MB | 1GB (Disk) |

### Escalabilidad

- **ChromaDB:** Soporta miles de documentos sin degradación
- **Mistral API:** 32K tokens por minuto (Free Tier)
- **Render Free:** 750 horas/mes gratis
- **Limitación:** Duerme después de 15min de inactividad

---

## 🔒 Seguridad

### Protección de Datos

- **API Keys:** Almacenadas en variables de entorno (no en código)
- **ChromaDB:** Persistente en disco (Render Disk)
- **HTTPS:** Automático con Let's Encrypt (Render)
- **CORS:** Habilitado para múltiples orígenes

### Buenas Prácticas

1. **Nunca** exponer MISTRAL_API_KEY en el código
2. Usar `.gitignore` para archivo `.env`
3. Rotar API keys periódicamente
4. Monitorear logs de acceso

---

## 🎯 Mejoras Futuras

### Corto Plazo

- [ ] Añadir más documentos (FAQ, términos legales)
- [ ] Implementar caching de respuestas frecuentes
- [ ] Añadir soporte para múltiples idiomas
- [ ] Mejorar prompts para mayor precisión

### Largo Plazo

- [ ] Integración con PostgreSQL para metadata
- [ ] Autenticación de usuarios
- [ ] Dashboard de analytics
- [ ] API REST para integración externa
- [ ] Soporte para voz (Speech-to-Text)

---

## 📝 Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | Julio 2026 | Versión inicial - RAG funcional completo |

---

## 📚 Referencias

- [Mistral AI Documentation](https://docs.mistral.ai/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Render.com Documentation](https://render.com/docs)
- [Sentence Transformers](https://www.sbert.net/)

---

**Desarrollado con ❤️ para Oracle One Alura Challenge**  
**v1.0.0 | Julio 2026**
