import streamlit as st
import os
from dotenv import load_dotenv
import uuid
import json
from datetime import datetime
from pathlib import Path

# Import LangChain components
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from trustcall import create_extractor
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, List, Dict, Any, Optional

# Set page configuration
st.set_page_config(
    page_title="Memory Agent - Task mAIstro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply simple professional styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .chat-message {
        padding: 0.7rem;
        border-radius: 0.4rem;
        margin-bottom: 0.7rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #e9ecef;
    }
    .chat-message.bot {
        background-color: #d1e7dd;
    }
    .chat-message .avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        margin-right: 0.7rem;
    }
    .chat-message .message {
        flex: 1;
    }
    .memory-item {
        padding: 0.4rem;
        border-radius: 0.25rem;
        margin-bottom: 0.4rem;
    }
    .memory-item.long-term {
        background-color: #cfe2ff;  /* Light blue for long-term memory */
    }
    .memory-item.short-term {
        background-color: #e2e3e5;  /* Light gray for short-term memory */
    }
    .todo-item {
        padding: 0.4rem;
        border-radius: 0.25rem;
        margin-bottom: 0.4rem;
        background-color: #d1e7dd;
    }
    h1, h2, h3 {
        color: #0c5460;
    }
    .stButton button {
        background-color: #0c5460;
        color: white;
    }
    .memory-header {
        font-size: 0.9rem;
        font-weight: bold;
        margin-bottom: 0.3rem;
    }
    .memory-content {
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Define memory types based on notebook
class UpdateMemory(TypedDict):
    """ Decision on what memory type to update """
    update_type: Literal['user', 'todo', 'instructions']

# Define Pydantic models for memory management
class Memory(BaseModel):
    """This is the memory of user"""
    content: str = Field(description="The main content of the memory. For example: User expressed interest in learning LangGraph")
    
class ToDo(BaseModel):
    """This is a todo item"""
    task: str = Field(description="The task to be done")
    priority: str = Field(description="Priority of the task: High, Medium, or Low")
    due_date: str = Field(description="Due date for the task (if any)")
    
class MemoryCollection(BaseModel):
    """This is the list of memories about the user"""
    memories: list[Memory] = Field(description="A list of memories about the user.")

class ToDoCollection(BaseModel):
    """This is the list of todo items"""
    todos: list[ToDo] = Field(description="A list of todo items.")

class UserProfile(BaseModel):
    """This is the user profile with personal information"""
    name: Optional[str] = Field(description="User's name", default=None)
    preferences: Optional[Dict[str, Any]] = Field(description="User's preferences", default=None)
    interests: Optional[List[str]] = Field(description="User's interests", default=None)
    
# Initialize session state for storing conversations and memories
if 'chats' not in st.session_state:
    st.session_state.chats = {}

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

# Memory stores following the notebook structure
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": None,
        "preferences": {},
        "interests": []
    }

if 'long_term_memories' not in st.session_state:
    st.session_state.long_term_memories = []

if 'short_term_memories' not in st.session_state:
    st.session_state.short_term_memories = []

if 'todos' not in st.session_state:
    st.session_state.todos = []

if 'instructions' not in st.session_state:
    st.session_state.instructions = "Create ToDo items when the user mentions tasks they need to complete."

# Spy class to inspect tool calls made by Trustcall
class Spy:
    def __init__(self):
        self.called_tools = []

    def __call__(self, run):
        # Collect information about the tool calls made by the extractor
        q = [run]
        while q:
            r = q.pop()
            if r.child_runs:
                q.extend(r.child_runs)
            if r.run_type == "chat_model":
                try:
                    self.called_tools.append(
                        r.outputs["generations"][0][0]["message"]["kwargs"]["tool_calls"]
                    )
                except (KeyError, IndexError):
                    pass

# Function to extract tool info
def extract_tool_info(tool_calls, schema_name="Memory"):
    """Extract information from tool calls for both patches and new memories."""
    changes = []
    
    if not isinstance(tool_calls, list):
        return f"No {schema_name} updates to report."
    
    for call_item in tool_calls:
        if isinstance(call_item, list):
            for call in call_item:
                if call.get('name') == schema_name:
                    changes.append({
                        'type': 'new',
                        'value': call.get('args', {})
                    })
                elif call.get('name') == 'PatchDoc':
                    changes.append({
                        'type': 'update',
                        'doc_id': call.get('args', {}).get('json_doc_id'),
                        'planned_edits': call.get('args', {}).get('planned_edits'),
                        'value': call.get('args', {}).get('patches', [{}])[0].get('value')
                    })
    
    result_parts = []
    for change in changes:
        if change['type'] == 'update':
            result_parts.append(
                f"Document {change['doc_id']} updated:\n"
                f"Plan: {change['planned_edits']}\n"
                f"Added content: {change['value']}"
            )
        else:
            result_parts.append(
                f"New {schema_name} created:\n"
                f"Content: {change['value']}"
            )
    
    return "\n\n".join(result_parts) if result_parts else f"No {schema_name} updates to report."

# Initialize LLM and extractors
@st.cache_resource
def initialize_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.warning("GROQ_API_KEY not found in environment variables. Using placeholder for demo.")
        groq_api_key = "demo_key"
    
    model = ChatGroq(
        model_name="meta-llama/llama-4-scout-17b-16e-instruct", 
        groq_api_key=groq_api_key
    )
    return model

def initialize_extractors(model):
    # Initialize spies
    memory_spy = Spy()
    todo_spy = Spy()
    profile_spy = Spy()
    
    # Create memory extractor
    memory_extractor = create_extractor(
        model,
        tools=[Memory],
        tool_choice="Memory",
        enable_inserts=True,
    )
    memory_extractor_with_spy = memory_extractor.with_listeners(on_end=memory_spy)
    
    # Create todo extractor
    todo_extractor = create_extractor(
        model,
        tools=[ToDo],
        tool_choice="ToDo",
        enable_inserts=True,
    )
    todo_extractor_with_spy = todo_extractor.with_listeners(on_end=todo_spy)
    
    # Create profile extractor
    profile_extractor = create_extractor(
        model,
        tools=[UserProfile],
        tool_choice="UserProfile",
        enable_inserts=True,
    )
    profile_extractor_with_spy = profile_extractor.with_listeners(on_end=profile_spy)
    
    return memory_extractor_with_spy, todo_extractor_with_spy, profile_extractor_with_spy, memory_spy, todo_spy, profile_spy

# Function to create a new chat
def create_new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "messages": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "title": f"New Chat {len(st.session_state.chats) + 1}"
    }
    st.session_state.current_chat_id = chat_id
    return chat_id

# Function to update user profile
def update_user_profile(profile_result):
    if profile_result["responses"]:
        for profile in profile_result["responses"]:
            if profile.name:
                st.session_state.user_profile["name"] = profile.name
            if profile.preferences:
                st.session_state.user_profile["preferences"].update(profile.preferences)
            if profile.interests:
                for interest in profile.interests:
                    if interest not in st.session_state.user_profile["interests"]:
                        st.session_state.user_profile["interests"].append(interest)

# Function to update memories
def update_memories(memory_result, is_long_term=False):
    if memory_result["responses"]:
        for memory in memory_result["responses"]:
            memory_content = memory.content
            if is_long_term:
                if memory_content not in [m["content"] for m in st.session_state.long_term_memories]:
                    st.session_state.long_term_memories.append({"content": memory_content, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")})
            else:
                if memory_content not in [m["content"] for m in st.session_state.short_term_memories]:
                    st.session_state.short_term_memories.append({"content": memory_content, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")})

# Function to update todos
def update_todos(todo_result):
    if todo_result["responses"]:
        for todo in todo_result["responses"]:
            todo_dict = {
                "task": todo.task,
                "priority": todo.priority,
                "due_date": todo.due_date,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            if todo_dict not in st.session_state.todos:
                st.session_state.todos.append(todo_dict)

# Function to process user message and generate response
def process_message(user_message, chat_id, model, memory_extractor, todo_extractor, profile_extractor, memory_spy, todo_spy, profile_spy):
    if not chat_id or chat_id not in st.session_state.chats:
        chat_id = create_new_chat()
    
    # Add user message to chat history
    st.session_state.chats[chat_id]["messages"].append({"role": "user", "content": user_message})
    
    # Prepare conversation history for the model
    conversation = []
    for msg in st.session_state.chats[chat_id]["messages"]:
        if msg["role"] == "user":
            conversation.append(HumanMessage(content=msg["content"]))
        else:
            conversation.append(AIMessage(content=msg["content"]))
    
    # Add user profile information to the context
    system_prompt = f"""You are Task mAIstro, an AI assistant that helps manage ToDo lists and remembers important information.
    
    User Profile:
    Name: {st.session_state.user_profile['name'] if st.session_state.user_profile['name'] else 'Unknown'}
    Interests: {', '.join(st.session_state.user_profile['interests']) if st.session_state.user_profile['interests'] else 'Unknown'}
    
    Instructions for creating ToDo items:
    {st.session_state.instructions}
    
    Remember all important information about the user across conversations.
    """
    
    # Add long-term memories to the context
    if st.session_state.long_term_memories:
        system_prompt += "\n\nLong-term Memories:\n"
        for memory in st.session_state.long_term_memories:
            system_prompt += f"- {memory['content']}\n"
    
    conversation_with_context = [SystemMessage(content=system_prompt)] + conversation
    
    # Generate AI response
    ai_response = model.invoke(conversation_with_context)
    
    # Add AI response to chat history
    st.session_state.chats[chat_id]["messages"].append({"role": "assistant", "content": ai_response.content})
    
    # Update chat title if it's the first message
    if len(st.session_state.chats[chat_id]["messages"]) == 2:
        # Generate a title based on the first message
        title_prompt = f"Generate a very short title (3-5 words) for a conversation that starts with: '{user_message}'"
        title_response = model.invoke([HumanMessage(content=title_prompt)])
        st.session_state.chats[chat_id]["title"] = title_response.content.strip()
    
    # Extract user profile information
    profile_instruction = "Extract any user profile information from the conversation:"
    profile_result = profile_extractor.invoke({
        "messages": [SystemMessage(content=profile_instruction)] + conversation
    })
    update_user_profile(profile_result)
    
    # Extract long-term memories
    memory_instruction = "Extract important long-term memories from the conversation:"
    memory_result = memory_extractor.invoke({
        "messages": [SystemMessage(content=memory_instruction)] + conversation
    })
    update_memories(memory_result, is_long_term=True)
    
    # Extract short-term memories (conversation context)
    short_term_instruction = "Extract short-term conversation context from the recent messages:"
    short_term_result = memory_extractor.invoke({
        "messages": [SystemMessage(content=short_term_instruction)] + conversation[-2:]  # Just the last exchange
    })
    update_memories(short_term_result, is_long_term=False)
    
    # Extract todos
    todo_instruction = "Extract any todo items from the conversation:"
    todo_result = todo_extractor.invoke({
        "messages": [SystemMessage(content=todo_instruction)] + conversation
    })
    update_todos(todo_result)
    
    return ai_response.content

# Main application layout
def main():
    # Initialize model and extractors
    model = initialize_llm()
    memory_extractor, todo_extractor, profile_extractor, memory_spy, todo_spy, profile_spy = initialize_extractors(model)
    
    # Sidebar - Chat management and memory display
    with st.sidebar:
        st.title("Task mAIstro 🧠")
        
        # Create new chat button
        if st.button("New Chat", key="new_chat"):
            create_new_chat()
            st.rerun()
        
        # Chat selection
        st.subheader("Your Chats")
        for chat_id, chat_data in st.session_state.chats.items():
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                if st.button(chat_data["title"], key=f"select_{chat_id}"):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{chat_id}"):
                    if st.session_state.current_chat_id == chat_id:
                        st.session_state.current_chat_id = None
                    del st.session_state.chats[chat_id]
                    st.rerun()
        
        st.divider()
        
        # User profile display
        st.subheader("User Profile")
        if st.session_state.user_profile["name"]:
            st.write(f"Name: {st.session_state.user_profile['name']}")
        if st.session_state.user_profile["interests"]:
            st.write(f"Interests: {', '.join(st.session_state.user_profile['interests'])}")
        else:
            st.info("No user profile information yet.")
        
        st.divider()
        
        # Memory display
        st.subheader("Memories")
        
        # Long-term memories
        st.markdown('<div class="memory-header">Long-term Memories:</div>', unsafe_allow_html=True)
        if st.session_state.long_term_memories:
            for memory in st.session_state.long_term_memories:
                st.markdown(f'<div class="memory-item long-term"><div class="memory-content">{memory["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.info("No long-term memories stored yet.")
        
        # Short-term memories
        st.markdown('<div class="memory-header">Short-term Memories:</div>', unsafe_allow_html=True)
        if st.session_state.short_term_memories:
            for memory in st.session_state.short_term_memories:
                st.markdown(f'<div class="memory-item short-term"><div class="memory-content">{memory["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.info("No short-term memories stored yet.")
        
        st.divider()
        
        # ToDo list
        st.subheader("ToDo List")
        if st.session_state.todos:
            for i, todo in enumerate(st.session_state.todos):
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    priority_color = {
                        "High": "red",
                        "Medium": "orange",
                        "Low": "green"
                    }.get(todo["priority"], "black")
                    
                    st.markdown(f'''
                    <div class="todo-item">
                        <div class="memory-content">
                            <strong>{todo["task"]}</strong><br>
                            Priority: <span style="color:{priority_color}">{todo["priority"]}</span>
                            {f'<br>Due: {todo["due_date"]}' if todo["due_date"] else ''}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                with col2:
                    if st.button("✓", key=f"complete_{i}"):
                        st.session_state.todos.pop(i)
                        st.rerun()
        else:
            st.info("No todos yet.")
    
    # Main chat area
    if not st.session_state.current_chat_id:
        # Welcome screen
        st.title("Welcome to Task mAIstro! 👋")
        st.markdown("""
        Task mAIstro is your intelligent ToDo list manager with long-term memory.
        
        ### Features:
        - Chat naturally about your tasks and plans
        - Automatically extracts ToDo items from your conversations
        - Remembers important information across multiple chat sessions
        - Maintains both long-term and short-term memory
        
        Get started by clicking the "New Chat" button in the sidebar!
        """)
    else:
        # Chat interface
        chat_data = st.session_state.chats[st.session_state.current_chat_id]
        st.title(chat_data["title"])
        
        # Display chat messages
        for message in chat_data["messages"]:
            if message["role"] == "user":
                st.markdown(f'''
                <div class="chat-message user">
                    <div class="avatar">👤</div>
                    <div class="message">{message["content"]}</div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="chat-message bot">
                    <div class="avatar">🤖</div>
                    <div class="message">{message["content"]}</div>
                </div>
                ''', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.chat_input("Type your message here...")
        if user_input:
            with st.spinner("Thinking..."):
                process_message(
                    user_input, 
                    st.session_state.current_chat_id,
                    model,
                    memory_extractor,
                    todo_extractor,
                    profile_extractor,
                    memory_spy,
                    todo_spy,
                    profile_spy
                )
                st.rerun()

if __name__ == "__main__":
    main()
