"""
Workflow Engine for Multi-Agent System

This module provides orchestration capabilities for multi-agent workflows,
allowing complex tasks to be broken down and executed across multiple agents.
"""

import uuid
import asyncio
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from core.state_management import WorkflowState, state_manager
from agents.base_agent import BaseAgent, agent_registry

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """Individual task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowTask:
    """Individual task within a workflow."""
    id: str
    name: str
    agent_name: str
    task_prompt: str
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get task execution duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class Workflow:
    """Multi-agent workflow definition."""
    id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    created_at: datetime = field(default_factory=datetime.now)
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    global_context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get workflow execution duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def get_task(self, task_id: str) -> Optional[WorkflowTask]:
        """Get a task by ID."""
        return next((task for task in self.tasks if task.id == task_id), None)
    
    def get_ready_tasks(self) -> List[WorkflowTask]:
        """Get tasks that are ready to execute (dependencies satisfied)."""
        ready_tasks = []
        
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue
                
            # Check if all dependencies are completed
            dependencies_completed = all(
                self.get_task(dep_id) and self.get_task(dep_id).status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )
            
            if dependencies_completed:
                ready_tasks.append(task)
                
        return ready_tasks
    
    def get_completed_tasks(self) -> List[WorkflowTask]:
        """Get all completed tasks."""
        return [task for task in self.tasks if task.status == TaskStatus.COMPLETED]
    
    def get_failed_tasks(self) -> List[WorkflowTask]:
        """Get all failed tasks."""
        return [task for task in self.tasks if task.status == TaskStatus.FAILED]


class WorkflowEngine:
    """
    Engine for executing multi-agent workflows.
    
    Manages workflow execution, task dependencies, and agent coordination.
    """
    
    def __init__(self):
        self.active_workflows: Dict[str, Workflow] = {}
        self.workflow_history: List[Workflow] = []
        self.max_concurrent_tasks = 5
        
    def create_workflow(
        self,
        name: str,
        description: str,
        tasks: List[Dict[str, Any]]
    ) -> Workflow:
        """
        Create a new workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
            tasks: List of task definitions
            
        Returns:
            Created workflow instance
        """
        workflow_id = str(uuid.uuid4())
        
        # Create workflow tasks
        workflow_tasks = []
        for task_def in tasks:
            task = WorkflowTask(
                id=task_def.get("id", str(uuid.uuid4())),
                name=task_def["name"],
                agent_name=task_def["agent_name"],
                task_prompt=task_def["task_prompt"],
                dependencies=task_def.get("dependencies", []),
                context=task_def.get("context", {})
            )
            workflow_tasks.append(task)
        
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            tasks=workflow_tasks
        )
        
        self.active_workflows[workflow_id] = workflow
        logger.info(f"Created workflow: {name} ({workflow_id})")
        
        return workflow
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            
        Returns:
            Workflow execution results
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}
        
        try:
            workflow.status = WorkflowStatus.RUNNING
            workflow.start_time = datetime.now()
            
            logger.info(f"Starting workflow execution: {workflow.name}")
            
            # Execute tasks in dependency order
            while True:
                ready_tasks = workflow.get_ready_tasks()
                
                if not ready_tasks:
                    # Check if all tasks are completed
                    pending_tasks = [t for t in workflow.tasks if t.status == TaskStatus.PENDING]
                    if not pending_tasks:
                        break
                    
                    # Check for failed dependencies
                    failed_tasks = workflow.get_failed_tasks()
                    if failed_tasks:
                        logger.error(f"Workflow failed due to failed tasks: {[t.name for t in failed_tasks]}")
                        workflow.status = WorkflowStatus.FAILED
                        break
                    
                    # If we have pending tasks but no ready tasks, there might be a dependency issue
                    logger.warning("No ready tasks found but pending tasks exist. Checking for circular dependencies.")
                    break
                
                # Execute ready tasks (up to max concurrent limit)
                tasks_to_execute = ready_tasks[:self.max_concurrent_tasks]
                
                # Execute tasks concurrently
                await asyncio.gather(*[
                    self._execute_task(workflow, task) 
                    for task in tasks_to_execute
                ])
            
            # Determine final workflow status
            if workflow.status == WorkflowStatus.RUNNING:
                failed_tasks = workflow.get_failed_tasks()
                if failed_tasks:
                    workflow.status = WorkflowStatus.FAILED
                else:
                    completed_tasks = workflow.get_completed_tasks()
                    if len(completed_tasks) == len(workflow.tasks):
                        workflow.status = WorkflowStatus.COMPLETED
                    else:
                        workflow.status = WorkflowStatus.FAILED
            
            workflow.end_time = datetime.now()
            
            # Move to history and remove from active workflows
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            logger.info(f"Workflow completed: {workflow.name} - Status: {workflow.status.value}")
            
            return {
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "duration": workflow.duration.total_seconds() if workflow.duration else None,
                "completed_tasks": len(workflow.get_completed_tasks()),
                "total_tasks": len(workflow.tasks),
                "failed_tasks": len(workflow.get_failed_tasks()),
                "results": [
                    {
                        "task_id": task.id,
                        "task_name": task.name,
                        "status": task.status.value,
                        "result": task.result,
                        "error": task.error
                    }
                    for task in workflow.tasks
                ]
            }
            
        except Exception as e:
            logger.error(f"Workflow execution error: {str(e)}")
            workflow.status = WorkflowStatus.FAILED
            workflow.end_time = datetime.now()
            return {"error": f"Workflow execution failed: {str(e)}"}
    
    async def _execute_task(self, workflow: Workflow, task: WorkflowTask):
        """Execute an individual task."""
        try:
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()
            
            logger.info(f"Executing task: {task.name} with agent: {task.agent_name}")
            
            # Get the agent
            agent = agent_registry.get_agent(task.agent_name)
            if not agent:
                raise ValueError(f"Agent {task.agent_name} not found")
            
            # Prepare task context with results from dependent tasks
            full_context = task.context.copy()
            full_context.update(workflow.global_context)
            
            # Add results from dependency tasks
            for dep_id in task.dependencies:
                dep_task = workflow.get_task(dep_id)
                if dep_task and dep_task.result:
                    full_context[f"dependency_{dep_id}"] = dep_task.result
            
            # Execute the task
            result = await agent.process_task(task.task_prompt, full_context)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.end_time = datetime.now()
            
            # Update workflow global context with task results if specified
            if result.get("success") and "update_global_context" in task.context:
                context_updates = task.context["update_global_context"]
                for key, value_path in context_updates.items():
                    # Simple path extraction (can be enhanced for nested paths)
                    if value_path in result:
                        workflow.global_context[key] = result[value_path]
            
            logger.info(f"Task completed: {task.name}")
            
        except Exception as e:
            logger.error(f"Task execution error: {task.name} - {str(e)}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.end_time = datetime.now()
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            # Check workflow history
            workflow = next(
                (w for w in self.workflow_history if w.id == workflow_id), 
                None
            )
        
        if not workflow:
            return None
        
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "start_time": workflow.start_time.isoformat() if workflow.start_time else None,
            "end_time": workflow.end_time.isoformat() if workflow.end_time else None,
            "duration": workflow.duration.total_seconds() if workflow.duration else None,
            "total_tasks": len(workflow.tasks),
            "completed_tasks": len(workflow.get_completed_tasks()),
            "failed_tasks": len(workflow.get_failed_tasks()),
            "task_details": [
                {
                    "id": task.id,
                    "name": task.name,
                    "agent": task.agent_name,
                    "status": task.status.value,
                    "duration": task.duration.total_seconds() if task.duration else None
                }
                for task in workflow.tasks
            ]
        }
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False
        
        workflow.status = WorkflowStatus.CANCELLED
        workflow.end_time = datetime.now()
        
        # Move to history
        self.workflow_history.append(workflow)
        del self.active_workflows[workflow_id]
        
        logger.info(f"Workflow cancelled: {workflow.name}")
        return True
    
    def list_workflows(self, include_history: bool = False) -> List[Dict[str, Any]]:
        """List all workflows."""
        workflows = list(self.active_workflows.values())
        
        if include_history:
            workflows.extend(self.workflow_history)
        
        return [
            {
                "id": w.id,
                "name": w.name,
                "description": w.description,
                "status": w.status.value,
                "created_at": w.created_at.isoformat(),
                "duration": w.duration.total_seconds() if w.duration else None,
                "task_count": len(w.tasks)
            }
            for w in workflows
        ]


# Global workflow engine instance
workflow_engine = WorkflowEngine()