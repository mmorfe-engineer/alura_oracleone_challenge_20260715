"""Pytest configuration."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def config():
    """Fixture para config."""
    from src.config import get_config
    return get_config()


@pytest.fixture
def agent(config):
    """Fixture para agente."""
    from src.agent import FinTechRAGAgent
    agent = FinTechRAGAgent(config)
    agent.initialize()
    return agent
