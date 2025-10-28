🤖 AI QA Chatbot with LangChain, LangGraph & FastAPI

A scalable and extensible AI-powered Question Answering (QA) Chatbot built using LangChain, LangGraph, and FastAPI.
It supports document ingestion, retrieval-augmented generation (RAG), vector-based search, and stateful conversation agents, accessible via both REST API and CLI interface.

🚀 Features

📄 PDF Upload & Ingestion – Extracts and chunks text from PDF documents

🧠 RAG (Retrieval-Augmented Generation) – Combines document retrieval with LLM reasoning

🗂️ Vector Database Integration – Stores embeddings using PostgreSQL with pgvector extension

⚙️ LangChain + LangGraph Agents – Handles conversational memory and reasoning graph orchestration

🌐 FastAPI Endpoints – For document management and query handling

💬 Interactive CLI Client – Chat directly with your AI assistant

🔐 Secure Configuration – Environment-based credentials management

🧩 Modular & Extensible Design – Easy to customize or extend components

🪵 Comprehensive Logging – Logs for API, vectorstore, and agent responses

🏗️ Architecture
User / CLI / Frontend
        │
        ▼
[ FastAPI Backend ] ⇄ [ PostgreSQL + pgvector ]
        │
        ▼
[ LangGraph Agent + LangChain Core + Vectorstore ]
        │
        ▼
[ OpenAI or Other LLM APIs ]

📘 Workflow

PDFs are uploaded via API and processed asynchronously

Text is extracted, chunked, and embedded using LangChain

Embeddings are stored in PostgreSQL with pgvector

LangGraph orchestrates retrieval and conversation logic

FastAPI exposes endpoints for upload, query, and management

CLI provides lightweight local testing without HTTP overhead

⚙️ Setup Instructions
🧾 Prerequisites

🐍 Python 3.10 or higher

🐘 PostgreSQL (with pgvector extension enabled)

🔑 OpenAI API key (or compatible LLM provider)

🧩 LangGraph API key (if applicable)

🧰 Installation Steps

1. Clone the repository

git clone https://github.com/yourusername/yourrepo.git
cd yourrepo


2. Create a virtual environment

python -m venv .venv
# Activate it
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows


3. Install dependencies

pip install -r requirements.txt


4. Configure environment variables

Create a file named .env in the root directory:

OPENAI_API_KEY=your_openai_api_key
LANGGRAPH_API_KEY=your_langgraph_api_key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/yourdb


5. Enable pgvector extension in PostgreSQL

CREATE EXTENSION IF NOT EXISTS vector;


6. Start FastAPI server

uvicorn main:app --reload --port 8000


7. (Optional) Launch the CLI chatbot

python agent_cli.py

🧠 Usage
🌐 API Endpoints
Method	Endpoint	Description
POST	/upload	Upload and index a PDF document
POST	/ask	Query the chatbot with a question
GET	/documents	List all uploaded documents
DELETE	/documents/{id}	Delete a document by its ID

Example Query

curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is this document about?"}'

💬 Interactive CLI

Run the CLI chatbot:

python agent_cli.py


🪵 Logging & Debugging

All API requests, responses, and agent calls are logged with timestamps

Vectorstore logs document indexing and retrieval operations

LangGraph agent traces conversation state and LLM reasoning

Adjust logging verbosity in configuration if needed

🔒 Security

.env file contains sensitive data – never commit it to Git

.gitignore excludes .env, cache, and unnecessary build files

Restrict PostgreSQL credentials and rotate API keys regularly
