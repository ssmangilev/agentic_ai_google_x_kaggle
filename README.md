BI Agentic System: Conversational Business Intelligence Assistant

This project implements a robust, multi-agent system designed to handle complex user queries, enforce security boundaries, and leverage conversational memory for continuous, context-aware interaction. Built using the Google Agent Development Kit (ADK) and Chainlit, it demonstrates advanced architectural patterns for developing reliable AI applications.

Architecture and Core Functionality

The core of the application is a Sequential Agent pipeline responsible for processing user input step-by-step:

User Input: A message is received via the Chainlit interface.

Security Guard: The input is first routed to the security_guard_agent. This agent's primary function is to perform input validation, intent classification, and content moderation, ensuring the query is safe and adheres to business rules before execution.

Decider/Executor: If the query is approved, it proceeds to the decider_agent. This agent is responsible for the main business logic: determining the necessary steps, potentially calling specialized tools (e.g., custom BI/data tools, Google Search), and generating the final, grounded response for the user.

Key Concepts Demonstrated

This submission showcases the practical application of the following key concepts learned in the course:

1. Multi-Agent System (Sequential Agents)

The system is fundamentally a Multi-Agent System structured as a Sequential Agent pipeline (main_pipeline).

Sequential Agents: The main_pipeline dictates a specific, ordered flow: security_guard_agent $\rightarrow$ decider_agent. This pattern ensures that all inputs must pass a critical security/moderation checkpoint before entering the main execution phase, promoting safety and predictable behavior.

Agents powered by an LLM: Both security_guard_agent and decider_agent are LLM-powered agents that utilize models like gemini-2.5-flash (inferred) to perform complex reasoning and task execution.

2. Sessions & Memory Management

The application implements persistent conversation history and user state management, ensuring continuity across interactions.

Sessions & State Management: The project uses the DatabaseSessionService (backed by a local SQLite database in this setup) to manage state. A unique session_id is generated for each conversation thread, ensuring user inputs and agent outputs are correctly logged and retrieved for every turn.

Long Term Memory: The Runner is explicitly configured with a dedicated memory_service (imported from utils.memory_service), enabling the agents to recall information from past, disconnected sessions, a critical feature for developing personalized and knowledgeable systems.

3. Context Engineering (Context Compaction)

To manage the size and cost of the ever-growing conversation history, the system employs an optimization technique for context window management.

Context Compaction: The EventsCompactionConfig is applied to the main App, specifically setting compaction_interval=3 and overlap_size=1. This configuration proactively summarizes (compacts) every three conversation turns, while keeping one turn of overlap to maintain continuity, dramatically reducing the token count sent to the LLM over long interactions without losing conversational flow.

Local Setup

Prerequisites

Python 3.10+

Poetry or Pip for dependency management

A Gemini API Key (set as an environment variable in a .env file)

Installation and Running

Clone the Repository:

git clone [your-repo-link]
cd bi_agentic_system


Install Dependencies:

pip install -r requirements.txt # Or use poetry install


Set Environment Variable: Create a .env file in the root directory and add your API key:

GEMINI_API_KEY="YOUR_API_KEY_HERE"


Run the Chainlit Application:

chainlit run main.py -w


Access: Open your browser to the URL provided by Chainlit (usually http://localhost:8000).