import sqlite3

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from pdf_vector_search import (
    load_documents,
    create_vector_database,
    search_documents
)


# ============================================================
# CONFIGURATION
# ============================================================

DB_NAME = "company.db"


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AI Employee Assistant",
    description="Employee assistant using SQLite, RAG and tools.",
    version="1.0"
)


# ============================================================
# LOAD RAG SYSTEM
# ============================================================

print("Loading company documents...")

documents = load_documents()

print(f"Loaded {len(documents)} document chunks.")

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Creating vector database...")

index = create_vector_database(
    documents,
    embedding_model
)

print("RAG system ready.")


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):
    employee_id: int
    question: str


# ============================================================
# DATABASE
# ============================================================

def get_employee(employee_id):

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT employee_id, name, department, manager, leave_days
        FROM employees
        WHERE employee_id = ?
        """,
        (employee_id,)
    )

    employee = cursor.fetchone()

    connection.close()

    return employee


# ============================================================
# EMPLOYEE TOOLS
# ============================================================

def get_employee_leave(employee_id):

    employee = get_employee(employee_id)

    if employee is None:
        return "Employee not found."

    return f"{employee[1]} has {employee[4]} leave days remaining."


def get_employee_department(employee_id):

    employee = get_employee(employee_id)

    if employee is None:
        return "Employee not found."

    return f"{employee[1]} works in the {employee[2]} department."


def get_employee_manager(employee_id):

    employee = get_employee(employee_id)

    if employee is None:
        return "Employee not found."

    return f"{employee[1]}'s manager is {employee[3]}."


# ============================================================
# AGENT
# ============================================================

def employee_agent(question, employee_id):

    question_lower = question.lower().strip()

    # --------------------------------------------------------
    # PERSONAL LEAVE
    # --------------------------------------------------------

    personal_leave_questions = [
        "how many leave days do i have",
        "how many leave days do i have left",
        "how much leave do i have",
        "how much leave do i have left",
        "how many vacation days do i have",
        "how much vacation do i have",
        "my remaining leave",
        "my leave balance",
        "my vacation balance"
    ]

    if any(
        phrase in question_lower
        for phrase in personal_leave_questions
    ):
        return get_employee_leave(employee_id)


    # --------------------------------------------------------
    # DEPARTMENT
    # --------------------------------------------------------

    department_questions = [
        "which department do i work in",
        "what department do i work in",
        "my department",
        "which team do i work in",
        "what team do i work in"
    ]

    if any(
        phrase in question_lower
        for phrase in department_questions
    ):
        return get_employee_department(employee_id)


    # --------------------------------------------------------
    # MANAGER
    # --------------------------------------------------------

    manager_questions = [
        "who is my manager",
        "who is my boss",
        "who do i report to",
        "who do i report to at work"
    ]

    if any(
        phrase in question_lower
        for phrase in manager_questions
    ):
        return get_employee_manager(employee_id)


    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    results = search_documents(
        question,
        documents,
        embedding_model,
        index
    )

    if not results:
        return (
            "I couldn't find this information "
            "in the available company documents."
        )


    # --------------------------------------------------------
    # BUILD RAG RESPONSE
    # --------------------------------------------------------

    answer_parts = []
    seen_text = set()

    for result in results:

        text = result["text"]
        source = result["source"]

        if text in seen_text:
            continue

        seen_text.add(text)

        answer_parts.append(
            f"{text}\nSource: {source}"
        )

    return "\n\n".join(answer_parts)


# ============================================================
# WEB UI
# ============================================================

HTML_PAGE = """
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>AI Employee Assistant</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    color: #1f2937;
}

.container {
    max-width: 850px;
    margin: 60px auto;
    padding: 20px;
}

.header {
    background: white;
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.header h1 {
    margin: 0 0 10px 0;
    font-size: 32px;
}

.header p {
    margin: 0;
    color: #6b7280;
}

.card {
    background: white;
    padding: 30px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

label {
    display: block;
    font-weight: bold;
    margin-bottom: 8px;
}

input,
textarea {
    width: 100%;
    padding: 13px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    font-size: 16px;
    margin-bottom: 18px;
}

textarea {
    min-height: 120px;
    resize: vertical;
}

button {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 10px;
    background: #2563eb;
    color: white;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    background: #1d4ed8;
}

button:disabled {
    background: #9ca3af;
    cursor: not-allowed;
}

.response {
    margin-top: 25px;
    padding: 20px;
    background: #f8fafc;
    border-radius: 12px;
    border-left: 5px solid #2563eb;
    white-space: pre-wrap;
    line-height: 1.6;
    display: none;
}

.status {
    margin-top: 15px;
    color: #6b7280;
    text-align: center;
}

.examples {
    margin-top: 20px;
    color: #6b7280;
    font-size: 14px;
}

.example {
    display: inline-block;
    background: #eef2ff;
    padding: 7px 10px;
    border-radius: 8px;
    margin: 4px;
    cursor: pointer;
}

.example:hover {
    background: #dbeafe;
}

.footer {
    text-align: center;
    color: #9ca3af;
    margin-top: 20px;
    font-size: 13px;
}

</style>

</head>


<body>

<div class="container">

    <div class="header">

        <h1>AI Employee Assistant</h1>

        <p>
            Ask questions about employee information and company policies.
        </p>

    </div>


    <div class="card">

        <label for="employeeId">
            Employee ID
        </label>

        <input
            id="employeeId"
            type="number"
            value="101"
        >


        <label for="question">
            Your Question
        </label>

        <textarea
            id="question"
            placeholder="Example: What are the working hours?"
        ></textarea>


        <button
            id="askButton"
            onclick="askQuestion()"
        >
            Ask AI Assistant
        </button>


        <div id="status" class="status"></div>


        <div id="response" class="response"></div>


        <div class="examples">

            <strong>Try:</strong>

            <span
                class="example"
                onclick="setQuestion('How many leave days do I have?')"
            >
                My leave balance
            </span>

            <span
                class="example"
                onclick="setQuestion('Which department do I work in?')"
            >
                My department
            </span>

            <span
                class="example"
                onclick="setQuestion('Who is my manager?')"
            >
                My manager
            </span>

            <span
                class="example"
                onclick="setQuestion('What is the annual leave policy?')"
            >
                Annual leave policy
            </span>

            <span
                class="example"
                onclick="setQuestion('What are the working hours?')"
            >
                Working hours
            </span>

            <span
                class="example"
                onclick="setQuestion('What is the maternity leave policy?')"
            >
                Unknown policy test
            </span>

        </div>

    </div>


    <div class="footer">

        AI Employee Assistant • SQLite • RAG • FastAPI

    </div>

</div>


<script>

function setQuestion(question) {

    document.getElementById("question").value = question;

}


async function askQuestion() {

    const employeeId =
        Number(document.getElementById("employeeId").value);

    const question =
        document.getElementById("question").value.trim();

    const button =
        document.getElementById("askButton");

    const status =
        document.getElementById("status");

    const responseBox =
        document.getElementById("response");


    if (!question) {

        responseBox.style.display = "block";

        responseBox.textContent =
            "Please enter a question.";

        return;
    }


    button.disabled = true;

    button.textContent = "Thinking...";

    status.textContent = "AI assistant is processing your question...";

    responseBox.style.display = "none";


    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                employee_id: employeeId,
                question: question
            })

        });


        const data = await response.json();


        responseBox.style.display = "block";


        if (data.error) {

            responseBox.textContent =
                data.error;

        } else {

            responseBox.textContent =
                data.answer;

        }


        status.textContent = "";

    }


    catch (error) {

        responseBox.style.display = "block";

        responseBox.textContent =
            "Could not connect to the AI assistant.";

        status.textContent = "";

    }


    finally {

        button.disabled = false;

        button.textContent = "Ask AI Assistant";

    }

}

</script>

</body>

</html>
"""


# ============================================================
# ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return HTML_PAGE


@app.post("/ask")
def ask_question(request: QuestionRequest):

    employee = get_employee(request.employee_id)

    if employee is None:

        return {
            "error": "Employee not found."
        }

    answer = employee_agent(
        request.question,
        request.employee_id
    )

    return {
        "employee": employee[1],
        "question": request.question,
        "answer": answer
    }