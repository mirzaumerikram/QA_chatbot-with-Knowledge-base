AI QA Chatbot with LangChain, LangGraph & FastAPI
Overview
This project implements a scalable and extensible AI-powered Question Answering (QA) Chatbot platform using LangChain, LangGraph, and FastAPI. It supports ingestion and indexing of PDF documents, retrieval-augmented generation (RAG) through vector databases, stateful conversational agents, and features both HTTP API endpoints and an interactive CLI interface.

Features
Upload and ingest PDF documents with text extraction and chunking.

Store document embeddings in PostgreSQL with pgvector for efficient similarity search.

Use LangChain and LangGraph to build stateful AI agents with retrieval-augmented generation.

Expose REST API via FastAPI for document upload, query handling, and document management.

Command-line interactive LangGraph chatbot client for quick testing and demos.

Comprehensive logging for inputs, agent responses, and vectorstore activity.

Secure sensitive data with .env files, excluded from Git with .gitignore.

Modular design to easily extend or replace components.

Architecture
text
User / CLI / Frontend
     |
[FastAPI Backend] <--> [PostgreSQL + pgvector]
     |
[LangGraph Agent + LangChain Core + Vectorstore]
     |
[OpenAI or other LLM APIs]
PDFs uploaded through API are processed, chunked, and embedded asynchronously.

Vectorstore stores embeddings and metadata for efficient retrieval.

LangGraph agents orchestrate conversation, document retrieval, and LLM calls.

FastAPI handles API requests and responses.

CLI provides direct agent interaction without HTTP overhead.

Setup Instructions
Prerequisites
Python 3.10 or higher

PostgreSQL database with pgvector extension installed

OpenAI API key or other LLM API keys

LangGraph API key if applicable

Installation Steps
Clone this repository:

bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
Set up Python virtual environment:

bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
Install dependencies:

bash
pip install -r requirements.txt
Configure environment variables by creating a .env file with:

text
OPENAI_API_KEY=your_openai_api_key
LANGGRAPH_API_KEY=your_langgraph_api_key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/yourdb
Enable pgvector in PostgreSQL:

sql
CREATE EXTENSION IF NOT EXISTS vector;
Start FastAPI server:

bash
uvicorn main:app --reload --port 8000
Optionally, run the LangGraph chatbot CLI for interactive experience:

bash
python agent_cli.py
Usage
API Endpoints
POST /upload — Upload and index a PDF document.

POST /ask — Query the AI chatbot with a question.

GET /documents — List uploaded documents.

DELETE /documents/{id} — Delete a document by its ID.

Interactive CLI
Launch with python agent_cli.py.

Type messages to interact with the AI agent.

Enter exit to quit.

Project Structure
text
.
├── main.py              # FastAPI backend application
├── agent_cli.py         # Terminal interactive LangGraph chatbot client
├── requirements.txt     # Python dependencies list
├── .env                 # Environment variables (ignored in Git)
├── .gitignore           # Git ignore file for sensitive/unneeded files
├── uploads/             # Directory to store uploaded PDFs
├── app/                 # Optional modules (database, models, utils, vectorstore)
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── vectorstore.py
│   ├── utils.py
│   └── auth.py
└── README.md            # This document
Logging & Debugging
All API requests, agent invocations, and key actions are logged with timestamps.

Async vectorstore operations log indexing and retrieval status.

Use log outputs to trace conversation flows and diagnose errors.

Security
.env file contains sensitive API keys and database credentials.

.env is added to .gitignore to prevent accidental commits.

Never commit .env or API keys to public repositories.

