"""Tests del agente RAG."""


def test_agent_initialization(agent):
    """Verifica inicialización."""
    assert agent.initialized is True
    assert agent.mistral_client is not None


def test_agent_info(agent):
    """Verifica info del agente."""
    info = agent.get_agent_info()
    assert "status" in info
    assert info["status"] == "initialized"


def test_answer_question(agent):
    """Verifica que responde preguntas."""
    response = agent.answer_question("¿Cuál es el límite de transferencias?")
    assert "answer" in response
    assert "success" in response
    assert response["question"] == "¿Cuál es el límite de transferencias?"


def test_search_documents(agent):
    """Verifica búsqueda."""
    results = agent.search_documents("limite transferencias")
    assert isinstance(results, list)
