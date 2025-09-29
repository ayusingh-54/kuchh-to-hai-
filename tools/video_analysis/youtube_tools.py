"""
YouTube Tools for Video Analysis Agent

This module provides tools for interacting with YouTube and processing video content:
- Video metadata extraction
- Transcript retrieval and processing
- Content analysis
- Key moment identification
"""

import os
import re
import requests
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

# YouTube API configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


@tool
def get_video_info(video_url: str) -> Dict[str, Any]:
    """
    Get comprehensive information about a YouTube video.
    
    Args:
        video_url: YouTube video URL
        
    Returns:
        Dict with video metadata or error message
    """
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return {"error": "Invalid YouTube URL format"}
        
        # Mock video information (replace with real API call when configured)
        video_info = {
            "video_id": video_id,
            "title": "Sample Video Title: How to Build AI Agents",
            "description": "This video explains how to build advanced AI agents using modern frameworks...",
            "channel_title": "AI Development Channel",
            "channel_id": "UC_mock_channel_123",
            "published_at": "2024-01-15T10:00:00Z",
            "duration": "PT15M32S",  # ISO 8601 duration format
            "duration_seconds": 932,
            "view_count": 125430,
            "like_count": 3420,
            "comment_count": 89,
            "category_id": "28",  # Science & Technology
            "tags": ["AI", "Machine Learning", "Programming", "Tutorial"],
            "language": "en",
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            "note": "This is mock video data. Configure YouTube Data API v3 for real video information."
        }
        
        logger.info(f"Retrieved video info for ID: {video_id}")
        return video_info
        
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        return {"error": f"Failed to get video info: {str(e)}"}


@tool
def get_video_transcript(video_url: str, language: str = "en") -> Dict[str, Any]:
    """
    Get transcript/captions for a YouTube video.
    
    Args:
        video_url: YouTube video URL
        language: Language code for transcript (default: en)
        
    Returns:
        Dict with transcript data or error message
    """
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return {"error": "Invalid YouTube URL format"}
        
        # Mock transcript data (replace with real transcript extraction)
        transcript_data = {
            "video_id": video_id,
            "language": language,
            "transcript_available": True,
            "transcript": [
                {
                    "start_time": 0.0,
                    "duration": 3.5,
                    "text": "Welcome to this comprehensive tutorial on building AI agents."
                },
                {
                    "start_time": 3.5,
                    "duration": 4.2,
                    "text": "In this video, we'll cover the fundamentals of agent architecture."
                },
                {
                    "start_time": 7.7,
                    "duration": 5.1,
                    "text": "We'll start by understanding what makes an agent intelligent and autonomous."
                },
                {
                    "start_time": 12.8,
                    "duration": 4.8,
                    "text": "Then we'll dive into practical implementation using modern frameworks."
                },
                {
                    "start_time": 17.6,
                    "duration": 3.9,
                    "text": "By the end, you'll have a working multi-agent system."
                }
            ],
            "full_text": "Welcome to this comprehensive tutorial on building AI agents. In this video, we'll cover the fundamentals of agent architecture. We'll start by understanding what makes an agent intelligent and autonomous. Then we'll dive into practical implementation using modern frameworks. By the end, you'll have a working multi-agent system.",
            "word_count": 45,
            "note": "This is mock transcript data. Use youtube-transcript-api or YouTube Data API for real transcripts."
        }
        
        logger.info(f"Retrieved transcript for video ID: {video_id}")
        return transcript_data
        
    except Exception as e:
        logger.error(f"Error getting video transcript: {str(e)}")
        return {"error": f"Failed to get video transcript: {str(e)}"}


@tool
def analyze_video_content(video_url: str, analysis_focus: str = "comprehensive") -> Dict[str, Any]:
    """
    Analyze video content and extract insights.
    
    Args:
        video_url: YouTube video URL
        analysis_focus: Focus area (comprehensive, technical, educational, entertainment)
        
    Returns:
        Dict with content analysis or error message
    """
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return {"error": "Invalid YouTube URL format"}
        
        # Mock content analysis
        analysis_data = {
            "video_id": video_id,
            "analysis_focus": analysis_focus,
            "content_analysis": {
                "main_topics": [
                    "AI Agent Architecture",
                    "Multi-Agent Systems",
                    "LangGraph Framework",
                    "Tool Integration",
                    "State Management"
                ],
                "key_concepts": [
                    "Agent autonomy and intelligence",
                    "Tool binding and execution",
                    "State persistence",
                    "Multi-agent coordination",
                    "Workflow orchestration"
                ],
                "difficulty_level": "Intermediate",
                "target_audience": "Developers and AI practitioners",
                "content_type": "Educational Tutorial",
                "engagement_factors": [
                    "Step-by-step explanations",
                    "Practical examples",
                    "Code demonstrations",
                    "Real-world applications"
                ]
            },
            "sentiment_analysis": {
                "overall_sentiment": "Positive",
                "educational_value": "High",
                "engagement_score": 8.5,
                "clarity_score": 9.0
            },
            "recommendations": {
                "best_quotes": [
                    "The key to building intelligent agents is understanding their decision-making process",
                    "Multi-agent systems can solve complex problems that single agents cannot handle"
                ],
                "key_timestamps": [
                    {"time": "2:15", "topic": "Agent Architecture Overview"},
                    {"time": "5:30", "topic": "Tool Integration Basics"},
                    {"time": "8:45", "topic": "State Management"},
                    {"time": "12:20", "topic": "Multi-Agent Coordination"}
                ],
                "action_items": [
                    "Set up development environment",
                    "Install required dependencies",
                    "Create your first agent",
                    "Implement tool integration"
                ]
            },
            "note": "This is mock analysis data. Integrate with AI services for real content analysis."
        }
        
        logger.info(f"Analyzed content for video ID: {video_id}")
        return analysis_data
        
    except Exception as e:
        logger.error(f"Error analyzing video content: {str(e)}")
        return {"error": f"Failed to analyze video content: {str(e)}"}


@tool
def extract_key_moments(video_url: str, moment_type: str = "highlights") -> Dict[str, Any]:
    """
    Extract key moments and timestamps from video.
    
    Args:
        video_url: YouTube video URL
        moment_type: Type of moments to extract (highlights, topics, questions, summaries)
        
    Returns:
        Dict with key moments or error message
    """
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return {"error": "Invalid YouTube URL format"}
        
        # Mock key moments extraction
        key_moments = {
            "video_id": video_id,
            "moment_type": moment_type,
            "total_moments": 8,
            "moments": [
                {
                    "timestamp": "0:00",
                    "title": "Introduction",
                    "description": "Welcome and overview of what will be covered",
                    "importance": "High",
                    "type": "Introduction"
                },
                {
                    "timestamp": "1:30",
                    "title": "What are AI Agents?",
                    "description": "Definition and core concepts of AI agents",
                    "importance": "High",
                    "type": "Concept"
                },
                {
                    "timestamp": "3:45",
                    "title": "Agent Architecture",
                    "description": "Deep dive into agent architecture components",
                    "importance": "High",
                    "type": "Technical"
                },
                {
                    "timestamp": "6:20",
                    "title": "Tool Integration",
                    "description": "How agents integrate and use external tools",
                    "importance": "Medium",
                    "type": "Implementation"
                },
                {
                    "timestamp": "9:10",
                    "title": "State Management",
                    "description": "Managing agent state and memory systems",
                    "importance": "High",
                    "type": "Technical"
                },
                {
                    "timestamp": "11:45",
                    "title": "Multi-Agent Systems",
                    "description": "Coordination between multiple agents",
                    "importance": "High",
                    "type": "Advanced"
                },
                {
                    "timestamp": "13:30",
                    "title": "Practical Example",
                    "description": "Building a complete agent system",
                    "importance": "High",
                    "type": "Demo"
                },
                {
                    "timestamp": "14:50",
                    "title": "Conclusion",
                    "description": "Summary and next steps",
                    "importance": "Medium",
                    "type": "Conclusion"
                }
            ],
            "chapter_summary": {
                "introduction": "0:00 - 1:30",
                "concepts": "1:30 - 3:45", 
                "architecture": "3:45 - 6:20",
                "implementation": "6:20 - 11:45",
                "advanced_topics": "11:45 - 13:30",
                "conclusion": "13:30 - 15:00"
            },
            "note": "This is mock key moments data. Use AI analysis services for real moment extraction."
        }
        
        logger.info(f"Extracted key moments for video ID: {video_id}")
        return key_moments
        
    except Exception as e:
        logger.error(f"Error extracting key moments: {str(e)}")
        return {"error": f"Failed to extract key moments: {str(e)}"}


@tool
def generate_video_summary(video_url: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
    """
    Generate a summary of the video content.
    
    Args:
        video_url: YouTube video URL
        summary_type: Type of summary (brief, comprehensive, technical, social_media)
        
    Returns:
        Dict with video summary or error message
    """
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return {"error": "Invalid YouTube URL format"}
        
        # Mock summary generation
        summary_data = {
            "video_id": video_id,
            "summary_type": summary_type,
            "summaries": {
                "brief": "A comprehensive tutorial on building AI agents using modern frameworks, covering architecture, tool integration, and multi-agent systems.",
                "comprehensive": """
                This educational video provides a thorough introduction to building AI agents. It begins with fundamental concepts of agent intelligence and autonomy, then progresses through architectural design patterns. The tutorial covers practical implementation using frameworks like LangGraph, demonstrating tool integration, state management, and inter-agent communication. Key topics include agent decision-making processes, memory systems, and workflow orchestration. The video concludes with a practical example of building a complete multi-agent system, making it valuable for developers looking to implement AI agents in their projects.
                """,
                "technical": """
                Technical deep-dive into AI agent architecture covering: 
                - Agent state management and persistence
                - Tool binding and execution patterns  
                - Multi-agent coordination protocols
                - LangGraph framework implementation
                - Memory hierarchy design (short-term, long-term, shared)
                - Workflow orchestration and task delegation
                - Error handling and recovery mechanisms
                """,
                "social_media": "🤖 Learn to build intelligent AI agents! This tutorial covers everything from basic concepts to multi-agent systems. Perfect for developers ready to dive into the future of AI automation. #AIAgents #MachineLearning #Programming"
            },
            "key_takeaways": [
                "AI agents require autonomous decision-making capabilities",
                "Tool integration is crucial for agent functionality",
                "State management enables agent memory and learning",
                "Multi-agent systems solve complex distributed problems",
                "Proper architecture design is essential for scalability"
            ],
            "recommended_audience": "Intermediate to advanced developers with Python and AI experience",
            "estimated_reading_time": {
                "brief": "30 seconds",
                "comprehensive": "2 minutes", 
                "technical": "3 minutes"
            },
            "note": "This is mock summary data. Use AI text generation services for real summaries."
        }
        
        logger.info(f"Generated summary for video ID: {video_id}")
        return summary_data
        
    except Exception as e:
        logger.error(f"Error generating video summary: {str(e)}")
        return {"error": f"Failed to generate video summary: {str(e)}"}


# Real implementation examples (commented out for now)
"""
# For real YouTube transcript extraction, you would use:
from youtube_transcript_api import YouTubeTranscriptApi

def get_real_transcript(video_id: str, language: str = "en"):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return {
            "transcript": transcript,
            "full_text": " ".join([entry['text'] for entry in transcript])
        }
    except Exception as e:
        return {"error": str(e)}

# For real YouTube API calls:
def get_real_video_info(video_id: str):
    if not YOUTUBE_API_KEY:
        return {"error": "YouTube API key not configured"}
    
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {
        'part': 'snippet,statistics,contentDetails',
        'id': video_id,
        'key': YOUTUBE_API_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            video = data['items'][0]
            return {
                "title": video['snippet']['title'],
                "description": video['snippet']['description'],
                "view_count": video['statistics'].get('viewCount', 0),
                "like_count": video['statistics'].get('likeCount', 0),
                # ... more fields
            }
    return {"error": "Failed to fetch video data"}
"""