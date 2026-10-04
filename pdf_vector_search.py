from pathlib import Path
import re

import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# ============================================================
# SETTINGS
# ============================================================

PROJECT_FOLDER = Path(__file__).resolve().parent
DOCUMENTS_FOLDER = PROJECT_FOLDER / "documents"

CHUNK_SIZE = 3
OVERLAP = 1

TOP_K = 5
DISTANCE_THRESHOLD = 1.15

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# LOAD PDF DOCUMENTS
# ============================================================

def load_documents():
    documents = []

    for pdf_file in DOCUMENTS_FOLDER.glob("*.pdf"):
        reader = PdfReader(pdf_file)

        full_text = ""

        for page in reader.pages:
            text = page.extract_text()

            if text:
                full_text += text + "\n"

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", full_text.strip())

        # Remove empty sentences
        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        # Create overlapping chunks
        start = 0

        while start < len(sentences):
            chunk_sentences = sentences[start:start + CHUNK_SIZE]

            if not chunk_sentences:
                break

            chunk_text = " ".join(chunk_sentences)

            documents.append({
                "text": chunk_text,
                "source": pdf_file.name
            })

            start += CHUNK_SIZE - OVERLAP

    return documents


# ============================================================
# CREATE VECTOR DATABASE
# ============================================================

def create_vector_database(documents, embedding_model):

    texts = [doc["text"] for doc in documents]

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


# ============================================================
# SEARCH DOCUMENTS
# ============================================================

def search_documents(
    question,
    documents,
    embedding_model,
    index
):

    question_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        question_embedding,
        TOP_K
    )

    results = []

    for distance, index_position in zip(
        distances[0],
        indices[0]
    ):

        if index_position == -1:
            continue

        if distance > DISTANCE_THRESHOLD:
            continue

        document = documents[index_position]

        results.append({
            "text": document["text"],
            "source": document["source"],
            "distance": float(distance)
        })

    return results


# ============================================================
# FIND MOST RELEVANT SENTENCES
# ============================================================

def rank_sentences(question, retrieved_chunks):

    question_words = set(
        re.findall(
            r"\b[a-zA-Z0-9]+\b",
            question.lower()
        )
    )

    candidates = []

    for chunk in retrieved_chunks:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            chunk["text"]
        )

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            sentence_words = set(
                re.findall(
                    r"\b[a-zA-Z0-9]+\b",
                    sentence.lower()
                )
            )

            overlap = question_words.intersection(
                sentence_words
            )

            score = len(overlap)

            # Semantic retrieval is still the main signal.
            # Lower FAISS distance = better match.
            semantic_score = 1 / (1 + chunk["distance"])

            final_score = score + semantic_score

            candidates.append({
                "sentence": sentence,
                "source": chunk["source"],
                "score": final_score,
                "distance": chunk["distance"]
            })

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return candidates


# ============================================================
# CLEAN ANSWER
# ============================================================

def generate_answer(question, retrieved_chunks):

    if not retrieved_chunks:
        return (
            "I couldn't find this information in the "
            "available documents."
        ), []

    ranked_sentences = rank_sentences(
        question,
        retrieved_chunks
    )

    if not ranked_sentences:
        return (
            "I couldn't find a clear answer in the "
            "available documents."
        ), []

    # Select the strongest sentence.
    best = ranked_sentences[0]

    answer = best["sentence"]

    # --------------------------------------------------------
    # Try to add a second supporting sentence when useful.
    # --------------------------------------------------------

    selected_sentences = [best]

    for candidate in ranked_sentences[1:]:

        if candidate["source"] != best["source"]:
            continue

        # Avoid duplicate / almost identical sentences.
        if candidate["sentence"] == best["sentence"]:
            continue

        selected_sentences.append(candidate)

        break

    if len(selected_sentences) > 1:

        answer = " ".join(
            item["sentence"]
            for item in selected_sentences
        )

    sources = list(
        dict.fromkeys(
            item["source"]
            for item in selected_sentences
        )
    )

    return answer, sources


# ============================================================
# DISPLAY SEARCH RESULTS
# ============================================================

def display_sources(retrieved_chunks):

    print("\nSources used:")

    shown_sources = set()

    for chunk in retrieved_chunks:

        source = chunk["source"]

        if source in shown_sources:
            continue

        shown_sources.add(source)

        print(f"- {source}")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("ENTERPRISE KNOWLEDGE COPILOT")
    print("=" * 60)

    print("\nLoading documents...")

    documents = load_documents()

    print(f"Loaded {len(documents)} document chunks.")

    print("\nLoading embedding model...")

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )

    print("Creating vector database...")

    index = create_vector_database(
        documents,
        embedding_model
    )

    print("\nSystem ready.")

    print("\nAsk questions about the company documents.")
    print("Type 'exit' to stop.")

    # ========================================================
    # CHAT LOOP
    # ========================================================

    while True:

        print("\n" + "-" * 60)

        question = input("Ask a question: ").strip()

        if question.lower() in [
            "exit",
            "quit",
            "bye"
        ]:
            print("\nGoodbye bro!")
            break

        if not question:
            continue

        # ----------------------------------------------------
        # RETRIEVE
        # ----------------------------------------------------

        retrieved_chunks = search_documents(
            question,
            documents,
            embedding_model,
            index
        )

        # ----------------------------------------------------
        # SHOW RETRIEVED EVIDENCE
        # ----------------------------------------------------

        print("\nRetrieved evidence:")

        if not retrieved_chunks:

            print("No sufficiently relevant information found.")

        else:

            for i, chunk in enumerate(
                retrieved_chunks,
                start=1
            ):

                print(
                    f"\n[{i}] "
                    f"{chunk['source']} "
                    f"(distance={chunk['distance']:.4f})"
                )

                print(chunk["text"])

        # ----------------------------------------------------
        # GENERATE ANSWER
        # ----------------------------------------------------

        answer, answer_sources = generate_answer(
            question,
            retrieved_chunks
        )

        # ----------------------------------------------------
        # DISPLAY ANSWER
        # ----------------------------------------------------

        print("\nAnswer:")
        print(answer)

        # ----------------------------------------------------
        # DISPLAY SOURCES
        # ----------------------------------------------------

        print("\nAnswer source(s):")

        if answer_sources:

            for source in answer_sources:
                print(f"- {source}")

        else:

            print("- No source found")


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()