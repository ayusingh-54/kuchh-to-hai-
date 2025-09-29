"""
State Management for Multi-Agent System

This module defines the state structures used across all agents
and provides utilities for managing conversation state, memory, and context.
"""

from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, add_messages
import json
import sqlite3
from datetime import datetime


class AgentState(TypedDict):
    """
    State structure for individual agents.
    
    This extends the basic chat state with additional fields
    for multi-agent coordination and task management.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    current_agent: Optional[str]
    task_context: Dict[str, Any]
    memory: Dict[str, Any]
    workflow_status: str  # "pending", "in_progress", "completed", "failed"


class WorkflowState(TypedDict):
    """
    State structure for multi-agent workflows.
    
    Manages the overall workflow execution across multiple agents.
    """
    workflow_id: str
    agents_involved: List[str]
    current_step: int
    total_steps: int
    step_results: List[Dict[str, Any]]
    global_context: Dict[str, Any]
    status: str  # "pending", "running", "completed", "failed"


class MemoryManager:
    """
    Advanced memory management for agents.
    
    Provides different types of memory:
    - Short-term: Current conversation context
    - Long-term: Persistent information across sessions
    - Shared: Information accessible by all agents
    """
    
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize the memory database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS short_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(agent_name, thread_id, key)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(agent_name, key)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS shared_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL UNIQUE,
                    value TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
    def store_short_term(self, agent_name: str, thread_id: str, key: str, value: Any):
        """Store information in short-term memory."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO short_term_memory 
                (agent_name, thread_id, key, value) 
                VALUES (?, ?, ?, ?)
            """, (agent_name, thread_id, key, json.dumps(value)))
            
    def get_short_term(self, agent_name: str, thread_id: str, key: str) -> Any:
        """Retrieve information from short-term memory."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT value FROM short_term_memory 
                WHERE agent_name = ? AND thread_id = ? AND key = ?
            """, (agent_name, thread_id, key))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
            
    def store_long_term(self, agent_name: str, key: str, value: Any):
        """Store information in long-term memory."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO long_term_memory 
                (agent_name, key, value) 
                VALUES (?, ?, ?)
            """, (agent_name, key, json.dumps(value)))
            
    def get_long_term(self, agent_name: str, key: str) -> Any:
        """Retrieve information from long-term memory."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT value FROM long_term_memory 
                WHERE agent_name = ? AND key = ?
            """, (agent_name, key))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
            
    def store_shared(self, key: str, value: Any, created_by: str):
        """Store information in shared memory."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO shared_memory 
                (key, value, created_by) 
                VALUES (?, ?, ?)
            """, (key, json.dumps(value), created_by))
            
    def get_shared(self, key: str) -> Any:
        """Retrieve information from shared memory."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT value FROM shared_memory WHERE key = ?
            """, (key,))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
            
    def clear_short_term(self, agent_name: str, thread_id: str):
        """Clear short-term memory for specific agent and thread."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM short_term_memory 
                WHERE agent_name = ? AND thread_id = ?
            """, (agent_name, thread_id))


class StateManager:
    """
    Central state management for the multi-agent system.
    
    Coordinates state between different agents and manages
    workflow execution state.
    """
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.active_workflows: Dict[str, WorkflowState] = {}
        
    def create_agent_state(
        self, 
        messages: List[BaseMessage], 
        agent_name: str = None,
        task_context: Dict[str, Any] = None
    ) -> AgentState:
        """Create a new agent state."""
        return AgentState(
            messages=messages,
            current_agent=agent_name,
            task_context=task_context or {},
            memory={},
            workflow_status="pending"
        )
        
    def update_agent_context(
        self, 
        state: AgentState, 
        key: str, 
        value: Any
    ) -> AgentState:
        """Update the task context in agent state."""
        state["task_context"][key] = value
        return state
        
    def create_workflow_state(
        self, 
        workflow_id: str,
        agents_involved: List[str],
        total_steps: int
    ) -> WorkflowState:
        """Create a new workflow state."""
        workflow_state = WorkflowState(
            workflow_id=workflow_id,
            agents_involved=agents_involved,
            current_step=0,
            total_steps=total_steps,
            step_results=[],
            global_context={},
            status="pending"
        )
        
        self.active_workflows[workflow_id] = workflow_state
        return workflow_state
        
    def update_workflow_step(
        self, 
        workflow_id: str, 
        step_result: Dict[str, Any]
    ) -> WorkflowState:
        """Update workflow with step result."""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        workflow = self.active_workflows[workflow_id]
        workflow["step_results"].append(step_result)
        workflow["current_step"] += 1
        
        if workflow["current_step"] >= workflow["total_steps"]:
            workflow["status"] = "completed"
        else:
            workflow["status"] = "running"
            
        return workflow
        
    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get current workflow state."""
        return self.active_workflows.get(workflow_id)


# Global state manager instance
state_manager = StateManager()