# AI Employee Operations Assistant

An AI-powered internal employee assistant that combines Retrieval-Augmented Generation (RAG), semantic search, SQLite, employee tools, and FastAPI to answer employee questions using company documents and structured employee data.

## Project Overview

This project demonstrates how an AI assistant can work with two different types of information:

1. Company policies stored in PDF documents
2. Employee-specific information stored in a SQLite database

The assistant routes questions to the appropriate source and returns grounded answers.

## Architecture

Browser UI
    |
    v
FastAPI
    |
    v
Employee Agent
   / \
  /   \
SQLite  RAG
        |
        v
   PDF Documents
        |
        v
  Sentence Embeddings
        |
        v
      FAISS
        |
        v
 Semantic Search

## Key Features

- Employee leave balance lookup
- Employee department lookup
- Employee manager lookup
- PDF-based company policy search
- Semantic search using embeddings
- FAISS vector similarity search
- SQLite employee database
- FastAPI backend
- Browser-based interface
- Grounded responses from available company documents
- Safe response when information is not available

## Technologies Used

- Python
- FastAPI
- Uvicorn
- Sentence Transformers
- FAISS
- SQLite
- PyPDF
- HTML/CSS/JavaScript

## What is RAG?

RAG stands for Retrieval-Augmented Generation.

Instead of asking an AI model to answer from memory, the system first searches relevant company documents and uses the retrieved information to answer the question.

Basic flow:

PDF documents
    |
    v
Text extraction
    |
    v
Chunking
    |
    v
Embeddings
    |
    v
FAISS vector search
    |
    v
Relevant document sections
    |
    v
Answer

## How the Project Works

### 1. Employee Questions

Questions about personal employee information are handled using the SQLite database.

Examples:

- How many leave days do I have?
- Which department do I work in?
- Who is my manager?

### 2. Company Policy Questions

Questions about company policies are searched against the available PDF documents.

Examples:

- What is the annual leave policy?
- What are the working hours?
- How often should passwords be changed?
- When is IT support available?

### 3. Unknown Information

If the requested information cannot be found in the available documents, the assistant does not invent an answer.

For example:

> I couldn't find this information in the available company documents.

This helps reduce unsupported answers.

## Project Structure

```text
GenAi/
│
├── api.py
├── employee_rag_agent.py
├── employee_database.py
├── pdf_vector_search.py
├── requirements.txt
├── .gitignore
│
├── documents/
│   ├── employee_handbook_sample.pdf
│   └── it_security_policy_sample.pdf
│
└── README.md