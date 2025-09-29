"""
Video Analysis Agent

Specialized agent for handling video-related tasks including:
- YouTube video analysis
- Transcript extraction and processing
- Content summarization
- Question generation from video content
- Video metadata extraction
"""

from typing import List, Dict, Any
from langchain_core.tools import BaseTool
from agents.base_agent import BaseAgent
from tools.video_analysis.youtube_tools import (
    get_video_info,
    get_video_transcript,
    analyze_video_content,
    extract_key_moments
)


class VideoAnalysisAgent(BaseAgent):
    """
    Agent specialized in video content analysis and processing.
    
    Capabilities:
    - Extract and analyze YouTube video transcripts
    - Generate summaries and key insights
    - Create questions based on video content
    - Identify important moments and timestamps
    - Extract metadata and statistics
    - Generate social media content from videos
    """
    
    def __init__(self):
        super().__init__(
            name="video_analysis_agent",
            description="Analyzes video content, extracts transcripts, and generates insights from video data",
            temperature=0.2  # More factual for analysis tasks
        )
        
    def get_tools(self) -> List[BaseTool]:
        """Return video analysis specific tools."""
        return [
            get_video_info,
            get_video_transcript,
            analyze_video_content,
            extract_key_moments
        ]
        
    def get_system_prompt(self) -> str:
        """Return system prompt for video analysis agent."""
        return """You are a Video Analysis Agent specialized in processing and analyzing video content, particularly from YouTube.

Your capabilities include:
- Extracting and analyzing video transcripts
- Generating comprehensive summaries of video content
- Identifying key moments and important timestamps
- Creating questions and discussion points from video content
- Extracting metadata, statistics, and engagement metrics
- Generating social media content based on video insights
- Creating educational content from video materials

Guidelines for video analysis:
- Always provide accurate timestamps for key moments
- Create comprehensive yet concise summaries
- Identify main topics, themes, and key takeaways
- Generate thoughtful questions that encourage engagement
- Consider the target audience when creating content
- Maintain factual accuracy and avoid speculation
- Highlight actionable insights and practical tips

When analyzing content:
- Focus on the most valuable and interesting parts
- Identify patterns, trends, and recurring themes
- Note any technical information or expert insights
- Consider the speaker's credibility and expertise
- Extract quotable moments and memorable phrases

For content generation:
- Create engaging titles and descriptions
- Generate relevant hashtags and keywords
- Suggest optimal posting times and platforms
- Provide content adaptation for different social media formats
- Consider SEO optimization for discoverability"""

    async def analyze_youtube_video(self, video_url: str, analysis_type: str = "comprehensive") -> dict:
        """
        Perform comprehensive analysis of a YouTube video.
        
        Args:
            video_url: YouTube video URL
            analysis_type: Type of analysis (comprehensive, summary, questions, social_media)
            
        Returns:
            Detailed analysis results based on the requested type
        """
        analysis_prompt = f"""
        Analyze the YouTube video at: {video_url}
        Analysis type: {analysis_type}
        
        Please provide:
        1. Video metadata and basic information
        2. Complete transcript analysis
        3. Key themes and topics covered
        4. Important timestamps and moments
        5. Summary of main points
        6. Generated questions for engagement
        7. Social media content suggestions
        8. SEO keywords and hashtags
        """
        
        return await self.process_task(analysis_prompt, {"video_url": video_url})
        
    async def generate_content_from_video(
        self, 
        video_url: str, 
        content_types: List[str],
        target_platforms: List[str]
    ) -> dict:
        """
        Generate various types of content from a video.
        
        Args:
            video_url: YouTube video URL
            content_types: Types of content to generate (blog_post, social_posts, quiz, summary)
            target_platforms: Platforms to optimize for (twitter, linkedin, instagram, blog)
            
        Returns:
            Generated content optimized for each platform and type
        """
        content_prompt = f"""
        Based on the video at {video_url}, generate the following content types:
        Content types: {', '.join(content_types)}
        Target platforms: {', '.join(target_platforms)}
        
        For each content type and platform combination, provide:
        1. Optimized content with appropriate length and format
        2. Relevant hashtags and keywords
        3. Suggested posting times
        4. Call-to-action recommendations
        5. Engagement strategies
        """
        
        return await self.process_task(
            content_prompt, 
            {
                "video_url": video_url,
                "content_types": content_types,
                "platforms": target_platforms
            }
        )
        
    async def create_video_summary(
        self, 
        video_url: str, 
        summary_length: str = "medium",
        focus_areas: List[str] = None
    ) -> dict:
        """
        Create a focused summary of video content.
        
        Args:
            video_url: YouTube video URL
            summary_length: Length of summary (short, medium, long)
            focus_areas: Specific areas to focus on (key_points, technical_details, actionable_tips)
            
        Returns:
            Structured summary with key insights
        """
        focus_areas = focus_areas or ["key_points", "actionable_tips"]
        
        summary_prompt = f"""
        Create a {summary_length} summary of the video at {video_url}.
        Focus areas: {', '.join(focus_areas)}
        
        Structure the summary with:
        1. Executive summary (2-3 sentences)
        2. Main topics covered with timestamps
        3. Key insights and takeaways
        4. Actionable recommendations
        5. Notable quotes or statements
        6. Conclusion and next steps
        """
        
        return await self.process_task(
            summary_prompt,
            {
                "video_url": video_url,
                "length": summary_length,
                "focus": focus_areas
            }
        )
        
    async def generate_video_questions(
        self, 
        video_url: str, 
        question_types: List[str],
        difficulty_level: str = "mixed"
    ) -> dict:
        """
        Generate questions based on video content.
        
        Args:
            video_url: YouTube video URL
            question_types: Types of questions (discussion, quiz, reflection, engagement)
            difficulty_level: Difficulty level (easy, medium, hard, mixed)
            
        Returns:
            List of generated questions with context
        """
        questions_prompt = f"""
        Based on the video at {video_url}, generate questions of the following types:
        Question types: {', '.join(question_types)}
        Difficulty level: {difficulty_level}
        
        For each question type, provide:
        1. 5-10 well-crafted questions
        2. Context or reference to video content
        3. Expected answer depth/type
        4. Relevant timestamps if applicable
        5. Difficulty rating
        6. Suggested use case (social media, classroom, discussion)
        """
        
        return await self.process_task(
            questions_prompt,
            {
                "video_url": video_url,
                "question_types": question_types,
                "difficulty": difficulty_level
            }
        )