"""Interfaz Streamlit — UI modern y responsive."""

import sys
from pathlib import Path
import streamlit as st
import logging
from datetime import datetime

# Setup
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config, setup_logging
from src.agent import FinTechRAGAgent

# Logging
setup_logging(get_config())
logger = logging.getLogger(__name__)

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="🏦 BDT Asistente IA",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# CUSTOM STYLES (PURPLE THEME)
# ============================================================================

try:
    with open("./ui/styles.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    logger.warning("⚠️ styles.css no encontrado")

# ============================================================================
# SESSION STATE
# ============================================================================

if "agent" not in st.session_state:
    try:
        config = get_config()
        agent = FinTechRAGAgent(config)
        initialized = agent.initialize()
        if not initialized:
            st.error("❌ Error inicializando agente")
        st.session_state.agent = agent
        st.session_state.messages = []
        logger.info("✅ Agente inicializado en session")
    except Exception as e:
        st.error(f"❌ Error: {e}")
        logger.error(f"Error inicializando: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class='header-purple'>
    <h1>🏦 BDT Asistente IA</h1>
    <p>Preguntas sobre políticas, comisiones y servicios — Powered by Mistral + RAG</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# LAYOUT PRINCIPAL
# ============================================================================

col_main, col_sidebar = st.columns([3, 1])

# ============================================================================
# SIDEBAR
# ============================================================================

with col_sidebar:
    st.markdown("### ℹ️ Acerca de")

    if st.session_state.agent and st.session_state.agent.initialized:
        agent_info = st.session_state.agent.get_agent_info()

        with st.expander("📊 Info del Agente"):
            st.metric("Status", "🟢 Activo")
            st.metric("LLM", agent_info["llm_type"])
            st.metric("Docs", agent_info["documents_loaded"])

    st.divider()

    with st.expander("📚 Cobertura"):
        st.markdown("""
        ✅ Límites y transacciones
        ✅ Comisiones y tarifas
        ✅ Seguridad y fraude
        ✅ Planes de suscripción
        ✅ Política de privacidad
        ✅ FAQ General
        """)

    st.divider()

    st.markdown("""
    ### ⚠️ Nota

    Respuestas basadas en
    documentación oficial.
    Contacto: soporte@bdt.com.ve
    """)

# ============================================================================
# MAIN CONTENT
# ============================================================================

with col_main:
    st.markdown("### 💬 Haz tu Pregunta")

    user_input = st.text_input(
        "Pregunta:",
        placeholder="Ej: ¿Cuál es el límite de transferencias?",
    )

    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

    with col_btn1:
        ask_button = st.button("🔍 Buscar", use_container_width=True)

    with col_btn2:
        clear_button = st.button("🔄 Limpiar", use_container_width=True)

    with col_btn3:
        refresh_button = st.button("↻ Reload", use_container_width=True)

    if clear_button:
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # Response section
    if ask_button and user_input.strip():
        if not st.session_state.agent or not st.session_state.agent.initialized:
            st.error("❌ Agente no inicializado")
        else:
            with st.spinner("⏳ Buscando en políticas..."):
                response = st.session_state.agent.answer_question(user_input)

            # Añade a historial
            st.session_state.messages.append({
                "question": user_input,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })

            # Display
            if response["success"]:
                st.markdown("""
                <div class='answer-box-success'>
                """, unsafe_allow_html=True)

                st.markdown(f"**📝 Respuesta:**\n\n{response['answer']}")

                st.markdown("</div>", unsafe_allow_html=True)

                # Metadata
                col_c, col_m, col_t = st.columns(3)
                with col_c:
                    st.metric("Confianza", f"{int(response['confidence']*100)}%")
                with col_m:
                    st.metric("Docs", len(response.get("top_documents", [])))
                with col_t:
                    st.metric("Tiempo", response['timestamp'].split('T')[1][:5])

                # Sources
                if response["sources"]:
                    with st.expander("📌 Fuentes Consultadas"):
                        for source in response["sources"]:
                            st.markdown(f"- {source}")

                # Top results
                if response.get("top_documents"):
                    with st.expander("📊 Documentos Similares"):
                        for i, doc in enumerate(response["top_documents"], 1):
                            st.markdown(f"""
                            **Resultado {i}** (Similitud: {int(doc['score']*100)}%)

                            {doc['content']}
                            """)

            else:
                st.markdown("""
                <div class='answer-box-error'>
                """, unsafe_allow_html=True)

                st.markdown(f"**❌ Error:**\n\n{response['answer']}")
                st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("### 💡 Ejemplos de Preguntas")

        examples = [
            "¿Cuál es el límite diario de transferencias?",
            "¿Cómo reporto fraude?",
            "¿Cuáles son las comisiones internacionales?",
            "¿Qué planes de suscripción existen?",
            "¿Cuánto tiempo tarda una transferencia nacional?",
            "¿Cómo recupero acceso a mi cuenta?",
        ]

        for example in examples:
            if st.button(f"📌 {example}", use_container_width=True):
                st.session_state.user_input = example
                st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("### 🏦 BDT")
    st.markdown("Banco Digital de los Trabajadores")

with col_f2:
    st.markdown("### 🎓 Alura")
    st.markdown("Oracle One Challenge 2026")

with col_f3:
    st.markdown("### 👨‍💻 Dev")
    st.markdown("Morfe Flores | v1.0.0")

st.markdown("<div style='text-align:center; color:#999; font-size:11px;'>Made with ❤️ for Alura | Powered by Mistral + ChromaDB</div>", unsafe_allow_html=True)
