# AI Employee Operations Assistant

A Python-based employee assistant that answers questions about company policies using PDF document search and retrieves employee information from a SQLite database.

Built with **FastAPI, Sentence Transformers, FAISS, PyPDF, and SQLite**, this project combines semantic document search with database-backed employee lookups through a simple web interface.

## About the Project

Employees often need to find information about workplace policies, remote work, leave rules, and other company procedures. Searching through lengthy documents manually can take time.

The AI Employee Operations Assistant makes this process easier by allowing users to ask questions in natural language.

The application searches the most recently modified PDF, retrieves relevant text, and returns a concise answer with the source filename. It also supports employee information queries, such as checking leave balances, departments, and managers using a SQLite database.

The project demonstrates practical use of document processing, text embeddings, vector similarity search, API development, and database integration.

## Features

- **PDF document upload:** Upload a PDF through the web interface.
- **Latest PDF selection:** Selects the PDF with the most recent modification time for document search.
- **PDF text extraction:** Extracts readable text from PDF pages using PyPDF.
- **Text chunking:** Splits document text into smaller, overlapping chunks for retrieval.
- **Semantic search:** Uses Sentence Transformers to represent questions and document chunks as embeddings.
- **Vector search:** Uses FAISS to find relevant document chunks based on vector similarity.
- **Concise answers:** Selects a relevant sentence from the retrieved text and avoids repeated sentences.
- **Source citations:** Displays the PDF filename used to support the answer.
- **Employee information lookup:** Retrieves leave balances, departments, and manager information from SQLite.
- **FastAPI backend:** Handles user questions and PDF upload requests.
- **Interactive web interface:** Allows users to submit questions and view answers in their browser.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| FastAPI | Backend API and request handling |
| Sentence Transformers | Text embedding generation |
| `all-MiniLM-L6-v2` | Embedding model |
| FAISS | Vector similarity search |
| PyPDF | PDF text extraction |
| SQLite | Employee data storage |
| Pydantic | Request data validation |
| HTML | Web page structure |
| CSS | Web page styling |
| JavaScript | Frontend interactions |
| Uvicorn | Local application server |

## System Architecture

```text
                 User
                  |
                  v
          Web Interface
        (HTML, CSS, JS)
                  |
                  v
               FastAPI
                  |
          +-------+-------+
          |               |
          v               v
   Policy Questions   Employee Queries
          |               |
          v               v
      PDF Search       SQLite DB
          |
          v
   PDF Text Extraction
          |
          v
      Text Chunking
          |
          v
 Sentence Transformers
          |
          v
         FAISS
          |
          v
   Relevant Text Chunks
          |
          v
   Concise Answer
   + Source Filename
```

## How It Works

### 1. PDF upload and processing

1. The user uploads a PDF through the web interface.
2. The application saves the uploaded document in the `documents` folder.
3. The document-loading function selects the PDF with the latest modification time.
4. PyPDF extracts text from the PDF pages.
5. The extracted text is split into overlapping sentence chunks.
6. Sentence Transformers converts the chunks into numerical embeddings.
7. FAISS creates a vector index for similarity search.

### 2. Question answering

1. The user enters a question.
2. The application converts the question into an embedding.
3. FAISS searches for the closest document chunks.
4. The application filters results using a configured distance threshold.
5. Relevant sentences are ranked using keyword overlap and semantic similarity information.
6. The application returns a concise answer with the source PDF filename.

### 3. Employee information retrieval

For supported employee questions, the application queries the SQLite database using the supplied employee ID.

Examples include:

- Checking remaining leave days.
- Finding the employee's department.
- Identifying the employee's manager.

These employee lookups use database queries rather than PDF semantic search.

## Example Questions

### Company policy questions

- How many remote-work days are allowed per week?
- What are the working hours?
- What is the annual leave policy?
- What security rules apply when working remotely?

### Employee information questions

- How many leave days do I have?
- Which department do I work in?
- Who is my manager?

Answers depend on the contents of the selected PDF and the employee records available in the database.

## Example Output

**Question:**

`How many remote-work days are allowed per week?`

**Example answer:**

> Employees may request up to two remote-work days per week, subject to manager approval and team requirements.

**Source:** `sample_company_handbook_for_testing.pdf`

This example comes from the sample handbook used during testing. Answers will vary depending on the uploaded document.

## Project Structure

```text
AI-Employee-Operations-Assistant/
│
├── api.py
├── pdf_vector_search.py
├── employee_database.py
├── employee_rag_agent.py
├── requirements.txt
├── documents/
│   └── Sample PDF documents
└── README.md
```

### Main Files

**`api.py`**

Contains the FastAPI application, web interface, employee database lookup functions, question handling, and API routes.

**`pdf_vector_search.py`**

Handles PDF text extraction, sentence chunking, embedding generation, FAISS vector indexing, semantic retrieval, and sentence ranking.

**`employee_database.py`**

Contains the employee database setup code and related database functionality.

**`employee_rag_agent.py`**

Contains additional employee/RAG-related logic in the project.

**`requirements.txt`**

Lists the Python packages required to run the application.

**`documents/`**

Stores PDF documents used by the application.

## Installation and Setup

### Prerequisites

- Python installed on your computer.
- Visual Studio Code or another code editor.
- An internet connection for the initial embedding-model download, if the model is not already available locally.

### Step 1: Open the project

Open the project folder in Visual Studio Code.

### Step 2: Create a virtual environment

Run this command in the terminal:

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

### Step 3: Install dependencies

Run:

```bash
pip install -r requirements.txt
```

The project uses packages including FastAPI, Uvicorn, Sentence Transformers, FAISS, PyPDF, NumPy, Pydantic, and `python-multipart` for file uploads.

### Step 4: Start the application

Run this command from the project directory:

```bash
uvicorn api:app --reload
```

### Step 5: Open the application

Open the following address in your browser:

**http://127.0.0.1:8000**

The FastAPI interactive documentation is available at:

**http://127.0.0.1:8000/docs**

The application loads the embedding model and builds its document index when it starts. The first startup may take longer.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Opens the web interface |
| POST | `/ask` | Processes an employee or company-policy question |
| POST | `/upload-pdf` | Uploads a PDF and refreshes the document search system |

The `/ask` endpoint accepts an employee ID and a question. The `/upload-pdf` endpoint is used by the PDF upload interface.

## Current Limitations

- Only the PDF with the most recent modification time is selected for document search.
- Answers depend on the quality of the extracted PDF text and the relevance of retrieved sentences.
- Semantic similarity does not guarantee that every answer is complete or correct.
- Scanned PDFs without extractable text may not work without OCR.
- Employee ID input is not a substitute for authentication or authorization.
- The current sentence-selection logic does not use a generative large language model to write answers.
- The application needs additional security, testing, and deployment work before it should be used with sensitive employee data in production.

## Future Improvements

Possible future enhancements include:

- Supporting search across multiple PDFs.
- Improving answer relevance and handling unsupported questions.
- Adding automated tests for the API, document retrieval, and database functions.
- Implementing secure authentication and role-based access control.
- Improving PDF validation and error handling.
- Adding conversation history and user feedback.
- Integrating a local language model for grounded answer generation.
- Containerizing the application with Docker.
- Deploying the application to a secure hosting environment.

These are potential improvements, not features currently claimed as completed.

## Key Learning Outcomes

This project provides hands-on experience with:

- Developing APIs using FastAPI.
- Extracting and processing PDF documents.
- Generating text embeddings.
- Implementing semantic search using FAISS.
- Integrating SQLite with Python.
- Connecting a frontend to backend API endpoints.
- Retrieving relevant document passages and displaying source filenames.
- Understanding the limitations of retrieval-based question answering.

## License

No license has been specified for this project yet. Add a license file if you decide to publish the code under an open-source license.

---

**Built using Python, FastAPI, Sentence Transformers, FAISS, PyPDF, and SQLite.**
