# AI Employee Operations Assistant

An AI-powered employee assistance system that answers questions about company policies and employee information using PDF document search, semantic retrieval, and a SQLite database.

The project combines **FastAPI, Retrieval-Augmented Generation (RAG)-style document retrieval, Sentence Transformers, FAISS, and SQLite** to make company information easier to access through a simple web interface.

## Overview

Employees often need quick answers about company policies, leave, departments, managers, and other workplace information. Finding these details manually in lengthy documents can take time.

The AI Employee Operations Assistant helps solve this problem by allowing users to ask questions in natural language. The application searches the most recently modified PDF in the documents folder, retrieves relevant text, and displays a concise answer with its source filename.

It also retrieves employee-specific information from a SQLite database.

## Key Features

- **PDF upload:** Upload a company policy or handbook PDF through the web interface.
- **Latest-PDF selection:** Searches the PDF with the most recent modification time in the documents folder.
- **Semantic search:** Uses Sentence Transformers to represent document text and questions as numerical embeddings.
- **Vector similarity search:** Uses FAISS to retrieve text chunks that are semantically similar to a question.
- **Source references:** Displays the filename of the PDF used for an answer.
- **Concise answers:** Selects a relevant sentence from retrieved text and avoids displaying duplicate sentences.
- **Employee information lookup:** Retrieves employee leave balances, departments, and manager details from SQLite.
- **REST API:** Uses FastAPI to handle questions and other application requests.
- **Web interface:** Provides a simple interface for asking questions and viewing responses.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| FastAPI | Backend API and web application |
| Sentence Transformers | Converts text and questions into embeddings |
| `all-MiniLM-L6-v2` | Embedding model used for semantic search |
| FAISS | Finds similar document embeddings |
| PyPDF | Extracts text from PDF documents |
| SQLite | Stores employee information |
| HTML, CSS, JavaScript | Web interface |
| Pydantic | Validates API request data |
| Uvicorn | Runs the FastAPI application |

## How It Works

The application follows two main workflows: company-document question answering and employee information lookup.

### 1. Company document question answering

1. The user uploads a PDF through the web interface.
2. The PDF is saved in the `documents` folder.
3. The document-loading function selects the PDF with the latest modification time.
4. PyPDF extracts text from its pages.
5. The extracted text is split into smaller, overlapping chunks.
6. Sentence Transformers converts the chunks into numerical embeddings.
7. FAISS stores the embeddings in a vector index.
8. When a user asks a question, the question is converted into an embedding.
9. FAISS retrieves the closest matching chunks.
10. The application selects a relevant sentence and displays it with the source filename.

### 2. Employee information lookup

For supported employee questions, the application queries the SQLite database.

Examples include:

- How many leave days do I have?
- Which department do I work in?
- Who is my manager?

The application uses the employee ID supplied with the request to retrieve the corresponding record.

## System Architecture

```text
                  User
                   |
                   v
          Web Interface
       (HTML, CSS, JavaScript)
                   |
                   v
             FastAPI
                   |
          +--------+--------+
          |                 |
          v                 v
    Policy Questions   Employee Questions
          |                 |
          v                 v
    PDF Text Search     SQLite Database
          |
          v
   Sentence Transformer
          |
          v
        FAISS
          |
          v
   Relevant Text Chunks
          |
          v
  Concise Answer + Source
          |
          v
          User
```

## Project Structure

```text
AI-Employee-Operations-Assistant/
│
├── api.py
│   └── FastAPI application, web interface,
│       question handling, and employee tools
│
├── pdf_vector_search.py
│   └── PDF extraction, text chunking,
│       embedding creation, and semantic search
│
├── employee_database.py
│   └── Employee database setup and sample data
│
├── employee_rag_agent.py
│   └── Additional employee/RAG logic
│
├── documents/
│   └── PDF handbooks and company policies
│
├── requirements.txt
│   └── Python dependencies
│
└── README.md
    └── Project documentation
```

*The structure above describes the project files; the exact responsibilities of individual modules may vary with your current implementation.*

## Installation and Setup

Follow these steps to run the project locally.

### Prerequisites

Install the following:

- Python 3.10 or a compatible version for your dependencies
- Git (optional, for cloning the repository)
- A code editor such as Visual Studio Code

### Step 1: Clone the repository

Replace `YOUR-USERNAME` and `YOUR-REPOSITORY` with your GitHub details.

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
```

Open the project folder:

```bash
cd YOUR-REPOSITORY
```

If you already have the project on your computer, simply open its folder in VS Code.

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

If your `requirements.txt` is incomplete, make sure it includes the packages used by your implementation, such as:

```text
fastapi
uvicorn
python-multipart
pydantic
sentence-transformers
faiss-cpu
pypdf
numpy
```

Install any missing packages in your activated virtual environment.

### Step 4: Prepare the documents folder

Make sure a `documents` folder exists in the project directory. Upload a text-based PDF containing company policies or handbook information.

For testing, use fictional or non-sensitive documents. Scanned PDFs may require OCR if they do not contain extractable text.

### Step 5: Start the application

Run:

```bash
uvicorn api:app --reload
```

Open this address in your browser:

```text
http://127.0.0.1:8000
```

You can also access the FastAPI interactive documentation at:

```text
http://127.0.0.1:8000/docs
```

The first run may take longer because the embedding model may need to be downloaded. An internet connection may be required for the initial model download.

## Example Usage

### Example 1: Remote-work policy

**Question**

```text
How many remote-work days are allowed per week?
```

**Example answer**

```text
Employees may request up to two remote-work days per week,
subject to manager approval and team requirements.

Source: sample_company_handbook_for_testing.pdf
```

The answer depends on the contents of the PDF being searched.

### Example 2: Employee leave balance

**Question**

```text
How many leave days do I have?
```

The application checks the employee ID and retrieves the leave balance from SQLite.

### Example 3: Employee department

**Question**

```text
Which department do I work in?
```

The application retrieves the department associated with the employee ID.

## API Overview

The FastAPI application provides a web interface and request endpoints.

| Endpoint | Purpose |
|---|---|
| `GET /` | Opens the web interface |
| `POST /ask` | Processes a question using the employee and document-search logic |
| `POST /upload-pdf` | Uploads a PDF and rebuilds the document search index, if enabled in the current application |

To inspect the available API endpoints and request schemas, run the application and open `/docs`.

## Configuration

The document-search module uses settings such as:

| Setting | Purpose |
|---|---|
| `CHUNK_SIZE = 3` | Number of sentences in each text chunk |
| `OVERLAP = 1` | Number of overlapping sentences between adjacent chunks |
| `TOP_K = 5` | Maximum number of nearest chunks requested from FAISS |
| `DISTANCE_THRESHOLD = 1.15` | Maximum accepted FAISS distance in the current search implementation |
| `all-MiniLM-L6-v2` | Embedding model used to represent text |

The distance threshold depends on the embedding and distance metric. It should be evaluated against representative questions and documents rather than treated as a universal relevance score.

## Current Limitations

This project is a learning and portfolio project. It has some limitations:

- **Answer accuracy:** The application selects relevant text; semantic similarity does not guarantee that the selected sentence fully answers the question.
- **Latest-PDF behavior:** Only the PDF with the latest modification time is selected. This is not the same as maintaining a searchable collection of all uploaded documents.
- **PDF extraction:** Scanned PDFs and complicated layouts may not produce usable text.
- **Employee authentication:** The current employee ID input should not be treated as secure authentication.
- **Data privacy:** The application should not be used with confidential employee records without appropriate access controls and security measures.
- **LLM generation:** The current answer-selection logic is based on retrieved text and sentence ranking; it should not be described as a full generative-LLM answer system unless one is actually integrated.
- **Production readiness:** Authentication, authorization, upload validation, error handling, logging, testing, and deployment security would need further development.

## Future Improvements

Potential improvements include:

- Search across multiple documents with document-level filters.
- Improve answer relevance and handling of questions not covered by the documents.
- Add automated tests for retrieval, employee lookups, and upload handling.
- Add authentication and role-based access control.
- Improve PDF validation and error handling.
- Add a conversation history and feedback mechanism.
- Add a configurable local language model for grounded answer generation.
- Containerize the application with Docker.
- Deploy the application to a secure hosting environment.

These are planned improvements, not features claimed to be complete.

## Learning Outcomes

Building this project provides practical experience with:

- Building REST APIs with FastAPI.
- Extracting and processing PDF text.
- Text chunking and embedding generation.
- Semantic similarity search using FAISS.
- Integrating a relational database with Python.
- Connecting backend logic to a web interface.
- Displaying source references for retrieved information.
- Understanding the limitations of retrieval-based question answering.

## Contributing

Suggestions and improvements are welcome. To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Test the updated application.
5. Submit a pull request describing the changes.

## License

Choose a license before publishing the project for reuse. For example, an MIT License is a common option for open-source projects, but only add it if you want to release your code under those terms.

---

**Built with Python, FastAPI, FAISS, Sentence Transformers, and SQLite.**
