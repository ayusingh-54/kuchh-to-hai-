"""
Twitter Tools for Social Media Agent

This module provides tools for interacting with Twitter API:
- Posting tweets
- Getting analytics
- Replying to tweets
- Managing engagement
"""

import os
import requests
from typing import Dict, Any, Optional
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

# Twitter API configuration
TWITTER_API_BASE = "https://api.twitter.com"
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")


def get_twitter_headers() -> Dict[str, str]:
    """Get headers for Twitter API requests."""
    return {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }


@tool
def post_tweet(content: str, reply_to_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Post a tweet to Twitter.
    
    Args:
        content: The tweet content (max 280 characters)
        reply_to_id: Optional tweet ID to reply to
        
    Returns:
        Dict with tweet information or error message
    """
    try:
        # Validate content length
        if len(content) > 280:
            return {"error": f"Tweet too long: {len(content)} characters. Max 280 allowed."}
        
        # For now, return a mock response since we need proper Twitter API setup
        # In production, this would make actual API calls
        tweet_data = {
            "success": True,
            "tweet_id": "mock_tweet_123456789",
            "content": content,
            "character_count": len(content),
            "created_at": "2024-01-01T12:00:00Z",
            "reply_to": reply_to_id,
            "note": "This is a mock response. Configure Twitter API credentials for actual posting."
        }
        
        logger.info(f"Mock tweet posted: {content[:50]}...")
        return tweet_data
        
    except Exception as e:
        logger.error(f"Error posting tweet: {str(e)}")
        return {"error": f"Failed to post tweet: {str(e)}"}


@tool
def get_tweet_analytics(tweet_id: str, metrics: str = "public_metrics") -> Dict[str, Any]:
    """
    Get analytics for a specific tweet.
    
    Args:
        tweet_id: The ID of the tweet to analyze
        metrics: Type of metrics to retrieve (public_metrics, organic_metrics)
        
    Returns:
        Dict with tweet analytics or error message
    """
    try:
        # Mock analytics data
        analytics_data = {
            "tweet_id": tweet_id,
            "metrics": {
                "retweet_count": 15,
                "like_count": 42,
                "reply_count": 8,
                "quote_count": 3,
                "impression_count": 1250,
                "url_link_clicks": 23,
                "user_profile_clicks": 12
            },
            "engagement_rate": 5.6,  # (likes + retweets + replies + quotes) / impressions * 100
            "note": "This is mock analytics data. Configure Twitter API for real metrics."
        }
        
        return analytics_data
        
    except Exception as e:
        logger.error(f"Error getting tweet analytics: {str(e)}")
        return {"error": f"Failed to get analytics: {str(e)}"}


@tool
def reply_to_tweet(tweet_id: str, reply_content: str) -> Dict[str, Any]:
    """
    Reply to a specific tweet.
    
    Args:
        tweet_id: The ID of the tweet to reply to
        reply_content: The reply content (max 280 characters)
        
    Returns:
        Dict with reply information or error message
    """
    try:
        if len(reply_content) > 280:
            return {"error": f"Reply too long: {len(reply_content)} characters. Max 280 allowed."}
        
        # Mock reply response
        reply_data = {
            "success": True,
            "reply_id": "mock_reply_987654321",
            "original_tweet_id": tweet_id,
            "content": reply_content,
            "character_count": len(reply_content),
            "created_at": "2024-01-01T12:05:00Z",
            "note": "This is a mock response. Configure Twitter API credentials for actual replies."
        }
        
        logger.info(f"Mock reply posted to tweet {tweet_id}")
        return reply_data
        
    except Exception as e:
        logger.error(f"Error posting reply: {str(e)}")
        return {"error": f"Failed to post reply: {str(e)}"}


@tool
def search_tweets(query: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Search for tweets based on a query.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-100)
        
    Returns:
        Dict with search results or error message
    """
    try:
        if max_results > 100:
            max_results = 100
        elif max_results < 1:
            max_results = 1
            
        # Mock search results
        search_results = {
            "query": query,
            "result_count": min(max_results, 5),  # Mock returning 5 results
            "tweets": [
                {
                    "id": f"mock_tweet_{i}",
                    "text": f"Mock tweet {i} containing '{query}'",
                    "author_id": f"user_{i}",
                    "author_username": f"user{i}",
                    "created_at": "2024-01-01T12:00:00Z",
                    "public_metrics": {
                        "retweet_count": i * 2,
                        "like_count": i * 5,
                        "reply_count": i,
                        "quote_count": 1
                    }
                }
                for i in range(1, min(max_results + 1, 6))
            ],
            "note": "This is mock search data. Configure Twitter API for real search results."
        }
        
        return search_results
        
    except Exception as e:
        logger.error(f"Error searching tweets: {str(e)}")
        return {"error": f"Failed to search tweets: {str(e)}"}


@tool
def get_user_timeline(username: str, count: int = 10) -> Dict[str, Any]:
    """
    Get recent tweets from a specific user.
    
    Args:
        username: Twitter username (without @)
        count: Number of tweets to retrieve (1-200)
        
    Returns:
        Dict with user timeline or error message
    """
    try:
        if count > 200:
            count = 200
        elif count < 1:
            count = 1
            
        # Mock user timeline
        timeline_data = {
            "username": username,
            "user_id": f"mock_user_{username}",
            "tweet_count": min(count, 3),  # Mock returning 3 tweets
            "tweets": [
                {
                    "id": f"mock_tweet_{username}_{i}",
                    "text": f"Mock tweet {i} from @{username}",
                    "created_at": f"2024-01-0{i}T12:00:00Z",
                    "public_metrics": {
                        "retweet_count": i * 3,
                        "like_count": i * 7,
                        "reply_count": i * 2,
                        "quote_count": 1
                    }
                }
                for i in range(1, min(count + 1, 4))
            ],
            "note": f"This is mock timeline data for @{username}. Configure Twitter API for real user timelines."
        }
        
        return timeline_data
        
    except Exception as e:
        logger.error(f"Error getting user timeline: {str(e)}")
        return {"error": f"Failed to get user timeline: {str(e)}"}


# Real Twitter API implementation example (commented out for now)
"""
def post_tweet_real(content: str, reply_to_id: Optional[str] = None) -> Dict[str, Any]:
    # Real implementation would look like this:
    
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        return {"error": "Twitter API credentials not configured"}
    
    import tweepy
    
    client = tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )
    
    try:
        if reply_to_id:
            response = client.create_tweet(text=content, in_reply_to_tweet_id=reply_to_id)
        else:
            response = client.create_tweet(text=content)
            
        return {
            "success": True,
            "tweet_id": response.data['id'],
            "content": content,
            "created_at": response.data.get('created_at', 'Unknown')
        }
    except Exception as e:
        return {"error": str(e)}
"""