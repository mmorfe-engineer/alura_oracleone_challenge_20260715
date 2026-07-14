"""BDT RAG Agent — Package principal."""

__version__ = "1.0.0"
__author__ = "Morfe Flores"
__email__ = "morfefloresm@uvm.edu.ve"

from .config import get_config, setup_logging
from .agent import FinTechRAGAgent

__all__ = [
    "get_config",
    "setup_logging",
    "FinTechRAGAgent",
]
