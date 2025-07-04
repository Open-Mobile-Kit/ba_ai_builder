"""
AI Builder - Automated Business Analysis and Documentation Generation
A multi-agent system for generating professional business and technical documents
"""

__version__ = "1.0.0"
__author__ = "AI Builder Team"
__description__ = "Automated business analysis and documentation generation system"

from .orchestrator import orchestrator
from . import core
from . import agents

__all__ = ['orchestrator', 'core', 'agents']
