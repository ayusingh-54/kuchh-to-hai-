"""
Social Media Agent

Specialized agent for handling social media tasks including:
- Twitter posting and engagement
- LinkedIn content creation
- Social media analytics
- Content scheduling
"""

from typing import List
from langchain_core.tools import BaseTool
from agents.base_agent import BaseAgent
from tools.social_media.twitter_tools import (
    post_tweet, 
    get_tweet_analytics,
    reply_to_tweet
)
from tools.social_media.linkedin_tools import (
    post_linkedin_update,
    get_linkedin_analytics
)


class SocialMediaAgent(BaseAgent):
    """
    Agent specialized in social media management and automation.
    
    Capabilities:
    - Create and schedule social media posts
    - Engage with content (likes, comments, shares)
    - Analyze social media performance
    - Generate content ideas
    - Manage multiple social media accounts
    """
    
    def __init__(self):
        super().__init__(
            name="social_media_agent",
            description="Handles all social media related tasks including posting, engagement, and analytics",
            temperature=0.3  # More creative for content generation
        )
        
    def get_tools(self) -> List[BaseTool]:
        """Return social media specific tools."""
        return [
            post_tweet,
            get_tweet_analytics,
            reply_to_tweet,
            post_linkedin_update,
            get_linkedin_analytics
        ]
        
    def get_system_prompt(self) -> str:
        """Return system prompt for social media agent."""
        return """You are a Social Media Management Agent specialized in creating engaging content and managing social media presence.

Your capabilities include:
- Creating compelling social media posts for Twitter and LinkedIn
- Engaging with content through comments and replies
- Analyzing social media performance and metrics
- Scheduling posts for optimal engagement
- Generating hashtags and optimizing content for reach
- Managing multiple social media accounts

Guidelines:
- Always consider the platform's character limits and best practices
- Create engaging, authentic content that resonates with the target audience
- Use appropriate hashtags and mentions
- Maintain a consistent brand voice across platforms
- Be mindful of timing and frequency of posts
- Analyze performance data to improve future content

When creating content:
- Make it relevant and timely
- Include call-to-actions when appropriate
- Use emojis and formatting to enhance readability
- Consider trending topics and hashtags
- Ensure compliance with platform policies

For analytics and reporting:
- Provide clear insights and recommendations
- Track key metrics like engagement, reach, and conversions
- Identify best-performing content types and timing
- Suggest improvements based on data"""

    async def create_social_media_campaign(
        self, 
        campaign_goal: str,
        platforms: List[str],
        content_themes: List[str],
        target_audience: str
    ) -> dict:
        """
        Create a comprehensive social media campaign.
        
        Args:
            campaign_goal: The main objective of the campaign
            platforms: List of platforms to target (twitter, linkedin, etc.)
            content_themes: List of content themes/topics
            target_audience: Description of target audience
            
        Returns:
            Campaign plan with content suggestions and scheduling
        """
        campaign_prompt = f"""
        Create a comprehensive social media campaign with the following parameters:
        
        Goal: {campaign_goal}
        Platforms: {', '.join(platforms)}
        Content Themes: {', '.join(content_themes)}
        Target Audience: {target_audience}
        
        Please provide:
        1. Campaign strategy and approach
        2. Content calendar for the next 7 days
        3. Specific post suggestions for each platform
        4. Hashtag recommendations
        5. Engagement strategies
        6. Success metrics to track
        """
        
        return await self.process_task(campaign_prompt)
        
    async def analyze_content_performance(self, content_type: str, time_period: str) -> dict:
        """
        Analyze performance of social media content.
        
        Args:
            content_type: Type of content to analyze (posts, videos, images)
            time_period: Time period for analysis (last_week, last_month)
            
        Returns:
            Performance analysis with insights and recommendations
        """
        analysis_prompt = f"""
        Analyze the performance of {content_type} over the {time_period}.
        
        Please provide:
        1. Key performance metrics summary
        2. Best performing content and why it succeeded
        3. Underperforming content and potential reasons
        4. Audience engagement patterns
        5. Recommendations for future content
        6. Optimal posting times and frequency
        """
        
        return await self.process_task(analysis_prompt)
        
    async def generate_content_ideas(
        self, 
        industry: str, 
        content_type: str, 
        count: int = 5
    ) -> dict:
        """
        Generate creative content ideas for social media.
        
        Args:
            industry: Industry or niche for content
            content_type: Type of content (educational, promotional, entertaining)
            count: Number of ideas to generate
            
        Returns:
            List of content ideas with descriptions
        """
        ideas_prompt = f"""
        Generate {count} creative {content_type} content ideas for the {industry} industry.
        
        For each idea, provide:
        1. Content title/headline
        2. Brief description
        3. Key message or value proposition
        4. Suggested platform(s)
        5. Potential hashtags
        6. Call-to-action suggestion
        """
        
        return await self.process_task(ideas_prompt)