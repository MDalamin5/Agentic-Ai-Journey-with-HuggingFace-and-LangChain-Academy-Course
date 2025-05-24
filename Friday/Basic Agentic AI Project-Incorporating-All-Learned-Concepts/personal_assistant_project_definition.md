# Project Definition: LangGraph Personal AI Assistant

**Version:** 1.0
**Date:** May 24, 2025
**Project Lead:** Manus (Chief Project Engineer)
**Stakeholder:** User (Agentic AI Developer)

## 1. Introduction & Vision

This document outlines the project plan for developing a Personal AI Assistant. The primary goal of this project is **not** to create a feature-rich commercial assistant, but rather to serve as a practical learning exercise for the developer. It aims to solidify understanding and provide hands-on experience in implementing advanced agentic AI concepts using the LangGraph framework, specifically those covered in the recent LangGraph course, excluding Retrieval-Augmented Generation (RAG) components for this initial phase.

The vision is to build a functional, albeit basic, assistant capable of managing simple tasks and notes, while demonstrating a sophisticated underlying architecture incorporating state management, memory systems, human interaction, modularity, and resilience features inherent to LangGraph.

## 2. Project Objectives

*   **Develop a Core Agent:** Create a conversational agent capable of understanding and responding to user requests related to simple task and note management.
*   **Implement LangGraph Architecture:** Build the agent's logic using LangGraph, explicitly incorporating the following concepts:
    *   **State Management:** Define and manage a comprehensive `AgentState`.
    *   **Memory:** Implement both short-term (conversational) and long-term (user profile) memory.
    *   **Human-in-the-Loop (HITL):** Integrate points for user confirmation or clarification.
    *   **Time Travel:** Utilize LangGraph's checkpointer mechanism for state persistence and resumption.
    *   **Modularity (Sub-graphs):** Structure specific functionalities (e.g., task management) as distinct sub-graphs.
    *   **Multi-Agent Collaboration:** Design a simple multi-agent system (e.g., orchestrator + tool agents).
    *   **Parallel Processing (Map-Reduce):** Implement a map-reduce pattern for handling batch operations (e.g., summarizing multiple notes).
    *   **Advanced Memory Concepts:** Demonstrate representations of in-thread and cross-thread memory.
*   **Integrate External LLM:** Utilize the Groq API for accessing an open-source language model for core reasoning and generation tasks.
*   **Focus on Learning:** Prioritize the clear implementation and demonstration of each LangGraph concept over the complexity or polish of the assistant's end-user features.
*   **Exclude RAG:** Defer implementation of any RAG patterns (Corrective, Adaptive, etc.) to a potential future phase.

## 3. System Architecture Overview

The assistant will be built as a LangGraph graph application. The high-level architecture will consist of:

1.  **User Interface (UI):** A simple interface for interaction (e.g., Command Line Interface (CLI) initially, potentially expandable to Gradio/Streamlit).
2.  **Main Orchestrator Agent (LangGraph Graph):** The central graph that manages the overall flow, parses user input, maintains state, and routes tasks.
3.  **Specialized Sub-graphs/Agents:** Separate LangGraph graphs invoked by the orchestrator for specific functions:
    *   `TaskManagerAgent`: Handles creating, listing, updating, and deleting tasks.
    *   `NoteTakerAgent`: Handles creating, retrieving, and summarizing notes.
    *   (Potentially others as needed)
4.  **Memory Module:**
    *   **Short-Term:** Managed within the `AgentState` (e.g., conversation history).
    *   **Long-Term:** A persistent store (e.g., JSON file, simple DB) for user profile information (preferences, name), loaded/updated via the orchestrator.
5.  **Tool Integration Layer:** Connectors for any external tools (initially, the Groq API LLM).
6.  **Checkpointer:** LangGraph's persistence mechanism (e.g., `SqliteSaver`) connected to the main orchestrator graph.

## 4. Mapping LangGraph Concepts to Implementation

*   **State (`AgentState`):** A Pydantic or TypedDict object containing fields like `user_input: str`, `conversation_history: List[BaseMessage]`, `user_profile: dict`, `current_task: str`, `tool_outputs: dict`, `confirmation_needed: bool`, etc.
*   **Short-term Memory:** The `conversation_history` field within `AgentState`.
*   **Long-term Memory (Profile Schema):** The `user_profile` field in `AgentState`, loaded from/saved to a persistent JSON file at the start/end of relevant operations. This file represents the "profile schema".
*   **Human-in-the-Loop:** Conditional edges in the graph. If `confirmation_needed` is True in the state, route to a node that formats a question for the user and waits for input, rather than proceeding directly to execution.
*   **Time Travel (Checkpointer):** Instantiate `SqliteSaver.from_conn_string(":memory:")` (or a file path for persistence across runs) and pass it to the `compile()` method of the main graph. Provide mechanisms to save/load specific configurations (threads).
*   **Sub-graph:** Implement `TaskManagerAgent` and `NoteTakerAgent` as separate `Graph` instances. The main orchestrator graph will use nodes that invoke these sub-graphs (`invoke`).
*   **Multi-agent:** The Orchestrator acts as the primary agent. `TaskManagerAgent` and `NoteTakerAgent` act as specialized agents invoked by the orchestrator. The flow demonstrates routing and delegation.
*   **Map-Reduce:** Implement a node in the `NoteTakerAgent`. If the user asks to summarize multiple notes, this node retrieves the relevant notes (map input), invokes the LLM on each note individually (map function), collects the summaries, and then invokes the LLM again to synthesize a final summary (reduce function).
*   **In-thread Memory:** The `conversation_history` within a single session (LangGraph thread) represents in-thread memory.
*   **Cross-thread Memory:** The persistent `user_profile.json` file, loaded when a session starts (potentially using a specific thread ID or a default profile), represents a simple form of cross-thread memory, as it persists information across different interaction threads.

## 5. Technology Stack

*   **Core Framework:** Langchain, LangGraph
*   **Language Model:** Open-source model via Groq API
*   **Programming Language:** Python
*   **Persistence:** SQLite (for Checkpointer), JSON (for User Profile)
*   **Interface:** CLI (initially)

## 6. High-Level Implementation Steps

1.  **Setup:** Initialize project structure, install dependencies (Langchain, LangGraph, Groq client, etc.).
2.  **State Definition:** Define the `AgentState` TypedDict/Pydantic model.
3.  **Core Orchestrator Graph:** Build the basic nodes (input parsing, LLM call, output formatting) and edges for the main graph.
4.  **Checkpointer Integration:** Add `SqliteSaver` to the main graph for basic time travel.
5.  **Long-Term Memory:** Implement loading/saving of the `user_profile.json`.
6.  **Sub-graph Development (Task Manager):** Create the `TaskManagerAgent` graph with nodes for task operations.
7.  **Sub-graph Integration:** Add nodes to the orchestrator to invoke the `TaskManagerAgent`.
8.  **Sub-graph Development (Note Taker):** Create the `NoteTakerAgent` graph.
9.  **Map-Reduce Implementation:** Build the note summarization map-reduce node within `NoteTakerAgent`.
10. **Sub-graph Integration:** Add nodes to the orchestrator to invoke the `NoteTakerAgent`.
11. **Human-in-the-Loop:** Implement conditional logic and user interaction nodes.
12. **Testing & Refinement:** Test each feature individually and the end-to-end flow. Debug and refine.
13. **Documentation:** Add comments and potentially a README explaining how to run the assistant and how each concept is implemented.

## 7. Success Criteria

The project will be considered successful when:

*   A user can interact with the assistant via the CLI to perform basic task and note management.
*   All specified LangGraph concepts (State, Memory types, HITL, Time Travel, Sub-graphs, Multi-agent, Map-Reduce, Thread Memory) are demonstrably implemented and functional within the assistant's architecture.
*   The assistant utilizes the Groq API for LLM calls.
*   The agent's state can be saved and loaded using the checkpointer.
*   The code is reasonably well-structured and documented, highlighting the implementation of each concept.

## 8. Next Steps (Post-Project)

*   Implement RAG capabilities (Corrective, Adaptive).
*   Expand tool usage (e.g., simple web search, calculator).
*   Develop a more user-friendly interface (Gradio, Streamlit).
*   Enhance long-term memory persistence (e.g., vector database for notes).

