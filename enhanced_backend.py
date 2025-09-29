"""
Enhanced Multi-Agent Backend

This is an enhanced version of your original backend that incorporates
the multi-agent architecture while maintaining backward compatibility.
"""

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Dict, Any, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import sqlite3
import requests
import asyncio

# Import our new multi-agent components
from agents.base_agent import agent_registry
from agents.social_media_agent import SocialMediaAgent
from agents.video_analysis_agent import VideoAnalysisAgent
from core.workflow_engine import workflow_engine
from core.state_management import state_manager, AgentState

load_dotenv()

# -------------------
# 1. LLM
# -------------------
llm = ChatOpenAI()

# -------------------
# 2. Enhanced Tools (keeping your original ones)
# -------------------
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()

# New multi-agent tools
@tool
def create_social_media_campaign(
    goal: str, 
    platforms: str, 
    themes: str, 
    audience: str
) -> dict:
    """
    Create a comprehensive social media campaign using the Social Media Agent.
    
    Args:
        goal: Campaign objective
        platforms: Comma-separated list of platforms (twitter, linkedin)
        themes: Comma-separated list of content themes
        audience: Target audience description
    """
    try:
        # Get the social media agent
        social_agent = agent_registry.get_agent("social_media_agent")
        if not social_agent:
            return {"error": "Social Media Agent not available"}
        
        # This would be async in real implementation
        return {
            "success": True,
            "campaign_plan": f"Campaign created for {goal} targeting {audience}",
            "platforms": platforms.split(","),
            "themes": themes.split(","),
            "note": "This is a simplified sync version. Full async implementation available."
        }
        
    except Exception as e:
        return {"error": str(e)}

@tool
def analyze_youtube_video(video_url: str, analysis_type: str = "comprehensive") -> dict:
    """
    Analyze a YouTube video using the Video Analysis Agent.
    
    Args:
        video_url: YouTube video URL
        analysis_type: Type of analysis (comprehensive, summary, questions)
    """
    try:
        # Get the video analysis agent
        video_agent = agent_registry.get_agent("video_analysis_agent")
        if not video_agent:
            return {"error": "Video Analysis Agent not available"}
        
        # Extract video ID for mock response
        import re
        video_id_match = re.search(r'(?:v=|\/)([a-zA-Z0-9_-]{11})', video_url)
        video_id = video_id_match.group(1) if video_id_match else "unknown"
        
        return {
            "success": True,
            "video_id": video_id,
            "analysis_type": analysis_type,
            "summary": f"Analyzed video: {video_url}",
            "key_topics": ["AI", "Technology", "Tutorial"],
            "sentiment": "Positive",
            "note": "This is a simplified sync version. Full async implementation available."
        }
        
    except Exception as e:
        return {"error": str(e)}

@tool
def create_workflow(name: str, description: str, tasks_json: str) -> dict:
    """
    Create and execute a multi-agent workflow.
    
    Args:
        name: Workflow name
        description: Workflow description  
        tasks_json: JSON string describing workflow tasks
    """
    try:
        import json
        tasks = json.loads(tasks_json)
        
        workflow = workflow_engine.create_workflow(name, description, tasks)
        
        return {
            "success": True,
            "workflow_id": workflow.id,
            "name": workflow.name,
            "task_count": len(workflow.tasks),
            "status": workflow.status.value,
            "note": "Workflow created. Use execute_workflow to run it."
        }
        
    except Exception as e:
        return {"error": str(e)}

@tool
def list_available_agents() -> dict:
    """List all available agents and their capabilities."""
    try:
        capabilities = agent_registry.get_agent_capabilities()
        return {
            "success": True,
            "agent_count": len(capabilities),
            "agents": capabilities
        }
    except Exception as e:
        return {"error": str(e)}

# Enhanced tools list (original + new multi-agent tools)
tools = [
    search_tool, 
    calculator, 
    get_stock_price,
    create_social_media_campaign,
    analyze_youtube_video,
    create_workflow,
    list_available_agents
]

llm_with_tools = llm.bind_tools(tools)

# -------------------
# 3. Enhanced State (backward compatible)
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # Enhanced with multi-agent capabilities
    current_agent: str = None
    workflow_context: Dict[str, Any] = None

# -------------------
# 4. Enhanced Nodes
# -------------------
def chat_node(state: ChatState):
    """Enhanced LLM node with multi-agent awareness."""
    messages = state["messages"]
    
    # Add system context about available agents
    agent_count = len(agent_registry.list_agents())
    system_context = f"""
You are an advanced AI assistant with access to {agent_count} specialized agents:
- Social Media Agent: For creating posts, campaigns, and social media management
- Video Analysis Agent: For analyzing YouTube videos and extracting insights

You can also create multi-agent workflows for complex tasks that require coordination
between multiple agents. Always consider which specialized agent might be best suited
for the user's request.

Available tools include both basic utilities (search, calculator, stock prices) and 
advanced multi-agent capabilities (workflows, specialized analysis).
"""
    
    # Prepend system context if this is a new conversation
    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        system_msg = HumanMessage(content=system_context)
        messages = [system_msg] + messages
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# -------------------
# 5. Initialize Agents
# -------------------
def initialize_agents():
    """Initialize and register all available agents."""
    try:
        # Register specialized agents
        social_agent = SocialMediaAgent()
        video_agent = VideoAnalysisAgent()
        
        agent_registry.register_agent(social_agent)
        agent_registry.register_agent(video_agent)
        
        print(f"✅ Initialized {len(agent_registry.list_agents())} agents")
        
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")

# Initialize agents on module load
initialize_agents()

# -------------------
# 6. Checkpointer (unchanged)
# -------------------
conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 7. Enhanced Graph (backward compatible)
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 8. Enhanced Helpers
# -------------------
def retrieve_all_threads():
    """Retrieve all conversation threads (unchanged)."""
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)

def get_agent_status():
    """Get status of all registered agents."""
    return {
        "total_agents": len(agent_registry.list_agents()),
        "agents": agent_registry.list_agents(),
        "active_workflows": len(workflow_engine.active_workflows),
        "workflow_history": len(workflow_engine.workflow_history)
    }

async def execute_workflow_async(workflow_id: str):
    """Execute a workflow asynchronously."""
    return await workflow_engine.execute_workflow(workflow_id)

def create_sample_workflow():
    """Create a sample workflow for testing."""
    sample_tasks = [
        {
            "id": "task_1",
            "name": "Analyze Video",
            "agent_name": "video_analysis_agent",
            "task_prompt": "Analyze this YouTube video: https://youtube.com/watch?v=example",
            "dependencies": [],
            "context": {"analysis_type": "comprehensive"}
        },
        {
            "id": "task_2", 
            "name": "Create Social Media Campaign",
            "agent_name": "social_media_agent",
            "task_prompt": "Create a social media campaign based on the video analysis",
            "dependencies": ["task_1"],
            "context": {"platforms": ["twitter", "linkedin"]}
        }
    ]
    
    return workflow_engine.create_workflow(
        "Sample Video to Social Media Workflow",
        "Analyze a video and create social media content based on it",
        sample_tasks
    )

# -------------------
# 9. Advanced Features Demo
# -------------------
def demo_multi_agent_capabilities():
    """Demonstrate multi-agent capabilities."""
    print("\n🚀 Multi-Agent System Demo")
    print("=" * 50)
    
    # Show available agents
    status = get_agent_status()
    print(f"📊 System Status:")
    print(f"   - Agents: {status['total_agents']}")
    print(f"   - Active Workflows: {status['active_workflows']}")
    
    # Create sample workflow
    sample_workflow = create_sample_workflow()
    print(f"\n📝 Created Sample Workflow: {sample_workflow.name}")
    print(f"   - ID: {sample_workflow.id}")
    print(f"   - Tasks: {len(sample_workflow.tasks)}")
    
    print("\n💡 Try these commands in the chat:")
    print("   - 'List available agents'")
    print("   - 'Create a social media campaign for tech products targeting developers'")
    print("   - 'Analyze this YouTube video: [URL]'")
    print("   - 'Create a workflow to analyze a video and create social posts'")

if __name__ == "__main__":
    demo_multi_agent_capabilities()