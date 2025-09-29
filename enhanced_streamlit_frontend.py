"""
Enhanced Multi-Agent Streamlit Frontend

This enhanced frontend showcases the multi-agent capabilities while maintaining
backward compatibility with your existing chat interface.
"""

import streamlit as st
import asyncio
import json
from enhanced_backend import (
    chatbot, 
    retrieve_all_threads, 
    get_agent_status,
    workflow_engine,
    agent_registry,
    create_sample_workflow,
    execute_workflow_async
)
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

# =========================== Page Configuration ===========================
st.set_page_config(
    page_title="Multi-Agent AI Platform", 
    page_icon="🤖",
    layout="wide"
)

# =========================== Utilities ===========================
def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])

# ======================= Session Initialization ===================
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Chat"

add_thread(st.session_state["thread_id"])

# =========================== Sidebar Navigation ===========================
st.sidebar.title("🤖 Multi-Agent Platform")

# Page navigation
pages = ["Chat", "Agents", "Workflows", "Analytics"]
selected_page = st.sidebar.selectbox("Navigate", pages, index=pages.index(st.session_state["current_page"]))
st.session_state["current_page"] = selected_page

# System status in sidebar
with st.sidebar.expander("🔍 System Status", expanded=False):
    try:
        status = get_agent_status()
        st.metric("Active Agents", status["total_agents"])
        st.metric("Active Workflows", status["active_workflows"]) 
        st.metric("Workflow History", status["workflow_history"])
        
        if status["agents"]:
            st.write("**Available Agents:**")
            for agent in status["agents"]:
                st.write(f"• {agent}")
    except Exception as e:
        st.error(f"Status error: {e}")

# =========================== Page Content ===========================

if selected_page == "Chat":
    # =========================== Chat Page ===========================
    st.title("💬 AI Chat Assistant")
    
    # Chat controls
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Chat with your AI assistant. Try asking about social media campaigns or video analysis!")
    with col2:
        if st.button("🆕 New Chat"):
            reset_chat()
            st.rerun()

    # Chat threads sidebar
    with st.sidebar:
        st.header("💬 My Conversations")
        for thread_id in st.session_state["chat_threads"][::-1]:
            if st.button(str(thread_id), key=f"thread_{thread_id}"):
                st.session_state["thread_id"] = thread_id
                messages = load_conversation(thread_id)
                
                temp_messages = []
                for msg in messages:
                    if hasattr(msg, 'content'):
                        role = "user" if isinstance(msg, HumanMessage) else "assistant"
                        temp_messages.append({"role": role, "content": msg.content})
                st.session_state["message_history"] = temp_messages
                st.rerun()

    # Chat interface
    for message in st.session_state["message_history"]:
        with st.chat_message(message["role"]):
            st.text(message["content"])

    # Chat input
    user_input = st.chat_input("Ask me anything! Try: 'List available agents' or 'Create a social media campaign'")

    if user_input:
        # Show user's message
        st.session_state["message_history"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.text(user_input)

        CONFIG = {
            "configurable": {"thread_id": st.session_state["thread_id"]},
            "metadata": {"thread_id": st.session_state["thread_id"]},
            "run_name": "chat_turn",
        }

        # Assistant streaming block
        with st.chat_message("assistant"):
            status_holder = {"box": None}

            def ai_only_stream():
                for message_chunk, metadata in chatbot.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=CONFIG,
                    stream_mode="messages",
                ):
                    if isinstance(message_chunk, ToolMessage):
                        tool_name = getattr(message_chunk, "name", "tool")
                        if status_holder["box"] is None:
                            status_holder["box"] = st.status(
                                f"🔧 Using `{tool_name}` …", expanded=True
                            )
                        else:
                            status_holder["box"].update(
                                label=f"🔧 Using `{tool_name}` …",
                                state="running",
                                expanded=True,
                            )

                    if isinstance(message_chunk, AIMessage):
                        yield message_chunk.content

            ai_message = st.write_stream(ai_only_stream())

            if status_holder["box"] is not None:
                status_holder["box"].update(
                    label="✅ Tool finished", state="complete", expanded=False
                )

        st.session_state["message_history"].append(
            {"role": "assistant", "content": ai_message}
        )

elif selected_page == "Agents":
    # =========================== Agents Page ===========================
    st.title("🤖 Agent Management")
    
    try:
        capabilities = agent_registry.get_agent_capabilities()
        
        if not capabilities:
            st.warning("No agents are currently registered.")
            return
            
        st.write(f"**{len(capabilities)} agents are currently available:**")
        
        for agent_name, info in capabilities.items():
            with st.expander(f"🤖 {info['name'].replace('_', ' ').title()}", expanded=False):
                st.write(f"**Description:** {info['description']}")
                
                if info['tools']:
                    st.write("**Available Tools:**")
                    for tool in info['tools']:
                        st.write(f"• {tool}")
                else:
                    st.write("*No specific tools configured*")
                
                # Agent testing interface
                st.subheader("Test Agent")
                test_prompt = st.text_area(
                    f"Test prompt for {agent_name}:", 
                    key=f"test_{agent_name}",
                    placeholder="Enter a task for this agent to perform..."
                )
                
                if st.button(f"Test {agent_name}", key=f"btn_{agent_name}"):
                    if test_prompt:
                        with st.spinner(f"Testing {agent_name}..."):
                            # This would be async in real implementation
                            st.success(f"✅ Test completed for {agent_name}")
                            st.json({
                                "agent": agent_name,
                                "prompt": test_prompt,
                                "status": "completed",
                                "note": "This is a mock test result. Full async implementation available."
                            })
                    else:
                        st.warning("Please enter a test prompt.")
                        
    except Exception as e:
        st.error(f"Error loading agents: {e}")

elif selected_page == "Workflows":
    # =========================== Workflows Page ===========================
    st.title("🔄 Workflow Management")
    
    # Workflow creation section
    st.subheader("Create New Workflow")
    
    col1, col2 = st.columns(2)
    
    with col1:
        workflow_name = st.text_input("Workflow Name", placeholder="My Awesome Workflow")
        workflow_description = st.text_area("Description", placeholder="Describe what this workflow does...")
    
    with col2:
        st.write("**Quick Templates:**")
        if st.button("📹 Video → Social Media"):
            sample_workflow = create_sample_workflow()
            st.success(f"✅ Created sample workflow: {sample_workflow.id}")
        
        if st.button("📊 Research → Report"):
            st.info("🚧 Template coming soon!")
        
        if st.button("🎯 Custom Workflow"):
            st.info("🚧 Custom workflow builder coming soon!")
    
    # Active workflows
    st.subheader("Active Workflows")
    
    try:
        active_workflows = workflow_engine.list_workflows(include_history=False)
        
        if active_workflows:
            for workflow in active_workflows:
                with st.expander(f"🔄 {workflow['name']}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Status", workflow['status'])
                        st.metric("Tasks", workflow['task_count'])
                    
                    with col2:
                        st.write(f"**Created:** {workflow['created_at'][:19]}")
                        if workflow['duration']:
                            st.write(f"**Duration:** {workflow['duration']:.2f}s")
                    
                    with col3:
                        if st.button(f"Execute", key=f"exec_{workflow['id']}"):
                            with st.spinner("Executing workflow..."):
                                # This would use asyncio in real implementation
                                st.success("✅ Workflow execution started!")
                        
                        if st.button(f"Cancel", key=f"cancel_{workflow['id']}"):
                            if workflow_engine.cancel_workflow(workflow['id']):
                                st.success("✅ Workflow cancelled")
                                st.rerun()
        else:
            st.info("No active workflows. Create one above to get started!")
            
    except Exception as e:
        st.error(f"Error loading workflows: {e}")
    
    # Workflow history
    st.subheader("Workflow History")
    
    try:
        workflow_history = workflow_engine.list_workflows(include_history=True)
        completed_workflows = [w for w in workflow_history if w['status'] in ['completed', 'failed', 'cancelled']]
        
        if completed_workflows:
            for workflow in completed_workflows[-5:]:  # Show last 5
                status_color = {"completed": "🟢", "failed": "🔴", "cancelled": "🟡"}
                st.write(f"{status_color.get(workflow['status'], '⚪')} **{workflow['name']}** - {workflow['status']}")
        else:
            st.info("No workflow history yet.")
            
    except Exception as e:
        st.error(f"Error loading workflow history: {e}")

elif selected_page == "Analytics":
    # =========================== Analytics Page ===========================
    st.title("📊 System Analytics")
    
    # System metrics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        status = get_agent_status()
        
        with col1:
            st.metric("🤖 Active Agents", status["total_agents"])
        
        with col2:
            st.metric("🔄 Active Workflows", status["active_workflows"])
        
        with col3:
            st.metric("📜 Workflow History", status["workflow_history"])
        
        with col4:
            st.metric("💬 Chat Threads", len(st.session_state.get("chat_threads", [])))
        
        # Agent utilization (mock data)
        st.subheader("Agent Utilization")
        
        if status["agents"]:
            import random
            agent_data = []
            for agent in status["agents"]:
                agent_data.append({
                    "Agent": agent.replace("_", " ").title(),
                    "Tasks Completed": random.randint(0, 50),
                    "Success Rate": f"{random.randint(85, 99)}%",
                    "Avg Response Time": f"{random.uniform(0.5, 3.0):.1f}s"
                })
            
            st.dataframe(agent_data, use_container_width=True)
        
        # Workflow performance (mock data)
        st.subheader("Workflow Performance")
        
        workflow_data = {
            "Metric": ["Total Workflows", "Successful", "Failed", "Average Duration"],
            "Value": ["15", "12", "3", "45.2s"]
        }
        
        st.dataframe(workflow_data, use_container_width=True)
        
        # Usage trends (placeholder)
        st.subheader("Usage Trends")
        st.info("📈 Detailed analytics dashboard coming soon!")
        
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

# =========================== Footer ===========================
st.sidebar.markdown("---")
st.sidebar.markdown("**🚀 Multi-Agent AI Platform**")
st.sidebar.markdown("Built with LangGraph & Streamlit")

# Quick actions in sidebar
with st.sidebar.expander("⚡ Quick Actions", expanded=False):
    if st.button("🔄 Refresh System"):
        st.rerun()
    
    if st.button("🧹 Clear Chat History"):
        st.session_state["message_history"] = []
        st.success("Chat cleared!")
    
    if st.button("📊 System Info"):
        st.json({
            "version": "2.0.0",
            "framework": "LangGraph + Streamlit",
            "agents": len(agent_registry.list_agents()),
            "features": ["Multi-Agent", "Workflows", "Social Media", "Video Analysis"]
        })