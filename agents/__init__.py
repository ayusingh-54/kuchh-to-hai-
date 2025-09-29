"""
Agents package initialization.

This package contains all specialized agents for the multi-agent system.
"""

from .base_agent import BaseAgent, agent_registry
from .social_media_agent import SocialMediaAgent
from .video_analysis_agent import VideoAnalysisAgent

__all__ = [
    'BaseAgent',
    'agent_registry', 
    'SocialMediaAgent',
    'VideoAnalysisAgent'
]