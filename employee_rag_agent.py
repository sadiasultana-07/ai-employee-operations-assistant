# ============================================================
# EMPLOYEE RAG AGENT
# ============================================================

from sentence_transformers import SentenceTransformer

from pdf_vector_search import (
    load_documents,
    create_vector_database,
    search_documents
)


# ============================================================
# EMPLOYEE DATA
# ============================================================

employees = {
    101: {
        "name": "Alex",
        "department": "Engineering",
        "manager": "Sarah",
        "leave_days": 12
    },
    102: {
        "name": "John",
        "department": "Finance",
        "manager": "Mike",
        "leave_days": 8
    }
}


# ============================================================
# EMPLOYEE TOOLS
# ============================================================

def get_employee_leave(employee_id):

    employee = employees.get(employee_id)

    if employee is None:
        return "Employee not found."

    return (
        f"{employee['name']} has "
        f"{employee['leave_days']} leave days remaining."
    )


def get_employee_department(employee_id):

    employee = employees.get(employee_id)

    if employee is None:
        return "Employee not found."

    return (
        f"{employee['name']} works in the "
        f"{employee['department']} department."
    )


def get_employee_manager(employee_id):

    employee = employees.get(employee_id)

    if employee is None:
        return "Employee not found."

    return (
        f"{employee['name']}'s manager is "
        f"{employee['manager']}."
    )


# ============================================================
# SIMPLE AGENT
# ============================================================

def employee_agent(
    question,
    employee_id,
    documents,
    embedding_model,
    index
):

    question_lower = question.lower().strip()

    # ========================================================
    # PERSONAL LEAVE BALANCE
    # ========================================================
    # Only use the employee leave tool when the user is asking
    # about THEIR remaining leave balance.
    #
    # Examples:
    # "How many leave days do I have?"
    # "How much vacation do I have left?"
    # ========================================================

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


    # ========================================================
    # DEPARTMENT
    # ========================================================

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


    # ========================================================
    # MANAGER
    # ========================================================

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


    # ========================================================
    # OTHERWISE → RAG
    # ========================================================
    # Policy/company-information questions come here.
    # This includes:
    #
    # "What is the annual leave policy?"
    # "What is the maternity leave policy?"
    # "What are the working hours?"
    # "What is the password policy?"
    # ========================================================

    results = search_documents(
        question,
        documents,
        embedding_model,
        index
    )


    # ========================================================
    # NOTHING FOUND
    # ========================================================

    if not results:

        return (
            "I couldn't find this information "
            "in the available company documents."
        )


    # ========================================================
    # RETURN RETRIEVED EVIDENCE
    # ========================================================

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
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI EMPLOYEE ASSISTANT")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD DOCUMENTS
    # --------------------------------------------------------

    print("\nLoading company documents...")

    documents = load_documents()

    print(f"Loaded {len(documents)} document chunks.")


    # --------------------------------------------------------
    # LOAD EMBEDDING MODEL
    # --------------------------------------------------------

    print("\nLoading embedding model...")

    embedding_model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )


    # --------------------------------------------------------
    # CREATE VECTOR DATABASE
    # --------------------------------------------------------

    print("\nCreating vector database...")

    index = create_vector_database(
        documents,
        embedding_model
    )

    print("Vector database ready.")


    # --------------------------------------------------------
    # EMPLOYEE
    # --------------------------------------------------------

    employee_id = 101

    print("\nLogged in employee: Alex")

    print("\nExample questions:")
    print("- How many leave days do I have?")
    print("- Which department do I work in?")
    print("- Who is my manager?")
    print("- What is the annual leave policy?")
    print("- What is the maternity leave policy?")
    print("- What are the working hours?")
    print("- What is the password policy?")
    print("- What is the IT support timing?")

    print("\nType 'exit' to stop.")


    # --------------------------------------------------------
    # CHAT LOOP
    # --------------------------------------------------------

    while True:

        question = input("\nYou: ").strip()

        if question.lower() == "exit":

            print("\nGoodbye!")
            break

        if not question:
            continue

        answer = employee_agent(
            question,
            employee_id,
            documents,
            embedding_model,
            index
        )

        print("\nAI Employee Assistant:")
        print(answer)