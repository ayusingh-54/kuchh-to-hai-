"""
Base Agent Class for Multi-Agent System

This module provides the foundation for all specialized agents in the system.
Each agent inherits from BaseAgent and implements specific capabilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.
    
    Each agent should inherit from this class and implement:
    - get_tools(): Return list of tools this agent can use
    - get_system_prompt(): Return system prompt for this agent
    - process_task(): Handle specific task processing logic
    """
    
    def __init__(
        self, 
        name: str,
        description: str,
        llm: Optional[ChatOpenAI] = None,
        temperature: float = 0.1
    ):
        self.name = name
        self.description = description
        self.llm = llm or ChatOpenAI(temperature=temperature)
        self.tools = self.get_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools) if self.tools else self.llm
        self.graph = self._build_graph()
        
    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Return list of tools this agent can use."""
        pass
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt that defines this agent's role and capabilities."""
        pass
        
    def _build_graph(self) -> StateGraph:
        """Build the agent's workflow graph."""
        from core.state_management import AgentState
        
        graph = StateGraph(AgentState)
        graph.add_node("agent_node", self._agent_node)
        
        if self.tools:
            tool_node = ToolNode(self.tools)
            graph.add_node("tools", tool_node)
            graph.add_edge(START, "agent_node")
            graph.add_conditional_edges("agent_node", tools_condition)
            graph.add_edge("tools", "agent_node")
        else:
            graph.add_edge(START, "agent_node")
            graph.add_edge("agent_node", END)
            
        return graph
        
    def _agent_node(self, state):
        """Core agent processing node."""
        messages = state["messages"]
        system_prompt = HumanMessage(content=self.get_system_prompt())
        
        # Add system prompt at the beginning if not already present
        if not messages or messages[0].content != self.get_system_prompt():
            messages = [system_prompt] + messages
            
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
        
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a task using this agent.
        
        Args:
            task: The task to process
            context: Additional context for the task
            
        Returns:
            Dict containing the result and any additional metadata
        """
        try:
            messages = [HumanMessage(content=task)]
            
            if context:
                context_msg = f"Context: {context}"
                messages.insert(0, HumanMessage(content=context_msg))
                
            state = {"messages": messages}
            result = await self.graph.ainvoke(state)
            
            return {
                "success": True,
                "result": result["messages"][-1].content,
                "agent": self.name,
                "metadata": {
                    "tools_used": [tool.name for tool in self.tools],
                    "context": context
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing task in {self.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
            
    def get_capabilities(self) -> Dict[str, Any]:
        """Return information about this agent's capabilities."""
        return {
            "name": self.name,
            "description": self.description,
            "tools": [tool.name for tool in self.tools],
            "system_prompt": self.get_system_prompt()
        }


class AgentRegistry:
    """Registry to manage all available agents in the system."""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        
    def register_agent(self, agent: BaseAgent):
        """Register a new agent."""
        self._agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
        
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self._agents.get(name)
        
    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self._agents.keys())
        
    def get_agent_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities of all registered agents."""
        return {
            name: agent.get_capabilities() 
            for name, agent in self._agents.items()
        }


# Global agent registry instance
agent_registry = AgentRegistry()