import os
import hashlib
import streamlit as st
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* Main application */
    .main {
        padding-top: 1rem;
    }

    /* Hide Streamlit default elements */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Hero section */
    .hero {
        padding: 2rem 0 1.5rem 0;
    }

    .hero-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        background: rgba(99, 102, 241, 0.12);
        color: #6366f1;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }

    .hero-description {
        font-size: 1.1rem;
        line-height: 1.7;
        max-width: 850px;
        color: #6b7280;
    }

    /* Cards */
    .stat-card {
        padding: 1.2rem;
        border-radius: 14px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        background: rgba(128, 128, 128, 0.04);
        text-align: center;
    }

    .stat-number {
        font-size: 1.7rem;
        font-weight: 750;
    }

    .stat-label {
        font-size: 0.85rem;
        color: #6b7280;
        margin-top: 0.2rem;
    }

    /* Section headings */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.6rem;
    }

    /* Source card */
    .source-card {
        padding: 0.9rem 1rem;
        border-radius: 10px;
        border-left: 4px solid #6366f1;
        background: rgba(99, 102, 241, 0.07);
        margin-bottom: 0.6rem;
    }

    .source-page {
        font-weight: 700;
        color: #6366f1;
    }

    /* Upload section */
    .upload-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .upload-description {
        color: #6b7280;
        margin-bottom: 1rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.2);
    }

    /* Chat */
    .chat-info {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(99, 102, 241, 0.07);
        border: 1px solid rgba(99, 102, 241, 0.15);
        margin-bottom: 1rem;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        color: #8a8a8a;
        font-size: 0.8rem;
        padding: 2rem 0 1rem 0;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error(
        "GROQ_API_KEY was not found. "
        "Please add it to your .env file."
    )
    st.stop()

client = Groq(api_key=api_key)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "pages" not in st.session_state:
    st.session_state.pages = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    Clean extracted PDF text by:
    - Removing null characters
    - Removing excessive whitespace
    """

    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = " ".join(text.split())

    return text


# ============================================================
# PAGE-AWARE CHUNKING
# ============================================================

def create_page_chunks(pages, chunk_size=2000):
    """
    Split each PDF page into smaller chunks while
    remembering which page each chunk came from.
    """

    chunks = []

    for page_number, page_text in enumerate(pages, start=1):

        if not page_text:
            continue

        for i in range(0, len(page_text), chunk_size):

            chunk = page_text[i:i + chunk_size]

            if chunk.strip():

                chunks.append({
                    "page": page_number,
                    "text": chunk
                })

    return chunks


# ============================================================
# STOP WORDS
# ============================================================

STOP_WORDS = {
    "the",
    "is",
    "are",
    "was",
    "were",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "what",
    "who",
    "when",
    "where",
    "why",
    "how",
    "does",
    "do",
    "did",
    "this",
    "that",
    "these",
    "those",
    "it",
    "its"
}


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve_relevant_chunks(question, chunks, top_k=4):

    question_words = set(
        question.lower().split()
    )

    question_words = {
        word.strip(".,?!:;()[]{}")
        for word in question_words
    }

    question_words = {
        word
        for word in question_words
        if word not in STOP_WORDS and len(word) > 2
    }

    scored_chunks = []

    for chunk in chunks:

        chunk_words = set(
            chunk["text"].lower().split()
        )

        score = len(
            question_words.intersection(chunk_words)
        )

        scored_chunks.append(
            (score, chunk)
        )

    scored_chunks.sort(
        key=lambda x: x[0],
        reverse=True
    )

    relevant = [
        chunk
        for score, chunk in scored_chunks[:top_k]
        if score > 0
    ]

    return relevant


# ============================================================
# BUILD RETRIEVAL QUERY
# ============================================================

def build_retrieval_query(question):

    recent_messages = st.session_state.messages[-4:]

    history_text = ""

    for message in recent_messages:

        history_text += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )

    return f"""
Recent conversation:

{history_text}

Current question:

{question}
"""


# ============================================================
# ASK GROQ
# ============================================================

def ask_groq(question, relevant_chunks):

    context_parts = []

    for chunk in relevant_chunks:

        context_parts.append(
            f"[Page {chunk['page']}]\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    system_prompt = """
You are an AI Research Assistant.

Your job is to answer questions using ONLY
the information provided from the uploaded PDF.

Rules:

1. Do not invent information.
2. Do not use outside knowledge.
3. If the answer cannot be found in the provided
   document context, clearly say that the information
   was not found in the provided document.
4. Give clear and useful answers.
5. When possible, mention the relevant page number.
6. Never invent a page number.
7. Consider the previous conversation when answering
   follow-up questions.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Add previous conversation
    for message in st.session_state.messages:

        messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    # Add current document context
    messages.append({
        "role": "user",
        "content": f"""
Relevant information from the uploaded PDF:

{context}

Question:

{question}
"""
    })

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.2
    )

    return response.choices[0].message.content


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 📚 AI Research Assistant")

    st.caption(
        "Your personal workspace for understanding "
        "research papers and documents."
    )

    st.divider()

    if st.session_state.pages:

        st.markdown("### 📄 Current Document")

        st.success("Document loaded")

        st.caption(
            f"{len(st.session_state.pages)} pages available"
        )

        st.caption(
            f"{len(st.session_state.chunks)} searchable sections"
        )

    else:

        st.info(
            "Upload a PDF to start researching."
        )

    st.divider()

    if st.button(
        "🆕 New Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    st.markdown("### 💡 How to use")

    st.markdown(
        """
        **1. Upload a PDF**

        Add a research paper, report, article,
        or other text-based document.

        **2. Ask questions**

        Ask about concepts, findings,
        methodology, results, or conclusions.

        **3. Continue naturally**

        Ask follow-up questions without
        repeating the previous context.

        **4. Check sources**

        Review the pages used to support
        the answer.
        """
    )

    st.divider()

    st.caption(
        "AI Research Assistant • Built for intelligent document exploration"
    )


# ============================================================
# HERO
# ============================================================

st.html("""
<div class="hero">

    <div class="hero-badge">
        📚 AI-Powered Document Research
    </div>

    <div class="hero-title">
        AI Research Assistant
    </div>

    <div class="hero-description">
        Your personal AI research companion.
        Upload a research paper and ask questions
        about its content in a natural conversation.
        Get clear answers, ask follow-up questions
        without repeating yourself, explore relevant
        sections of the document, and quickly identify
        the pages supporting each answer.
    </div>

</div>
""")


# ============================================================
# DOCUMENT UPLOAD
# ============================================================

st.markdown(
    '<div class="section-title">📄 Upload your document</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="upload-description">
        Upload a PDF to begin exploring its content.
        The assistant will analyze the document and
        make its information available for conversation.
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    label_visibility="collapsed"
)


# ============================================================
# PROCESS PDF
# ============================================================

if uploaded_file:

    file_bytes = uploaded_file.getvalue()

    current_document_id = hashlib.md5(
        file_bytes
    ).hexdigest()

    # Process only when a new PDF is uploaded
    if current_document_id != st.session_state.document_id:

        st.session_state.document_id = current_document_id
        st.session_state.messages = []

        with st.spinner(
            "Reading and preparing your document..."
        ):

            reader = PdfReader(uploaded_file)

            pages = []

            for page in reader.pages:

                try:
                    text = page.extract_text()
                except Exception:
                    text = ""

                text = clean_text(text)

                pages.append(text)

            chunks = create_page_chunks(pages)

            st.session_state.pages = pages
            st.session_state.chunks = chunks

        st.success(
            f"Successfully loaded **{uploaded_file.name}**"
        )


# ============================================================
# DOCUMENT INFORMATION
# ============================================================

if st.session_state.pages:

    total_pages = len(
        st.session_state.pages
    )

    total_characters = sum(
        len(page)
        for page in st.session_state.pages
    )

    total_chunks = len(
        st.session_state.chunks
    )

    st.markdown(
        '<div class="section-title">📊 Document overview</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">
                    {total_pages}
                </div>
                <div class="stat-label">
                    Pages
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">
                    {total_characters:,}
                </div>
                <div class="stat-label">
                    Characters
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">
                    {total_chunks}
                </div>
                <div class="stat-label">
                    Searchable Sections
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        non_empty_pages = sum(
            1
            for page in st.session_state.pages
            if page.strip()
        )

        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">
                    {non_empty_pages}
                </div>
                <div class="stat-label">
                    Text Pages
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# DOCUMENT PREVIEW
# ============================================================

if st.session_state.pages:

    st.markdown(
        '<div class="section-title">👀 Document preview</div>',
        unsafe_allow_html=True
    )

    preview_text = ""

    for page_number, page_text in enumerate(
        st.session_state.pages[:2],
        start=1
    ):

        preview_text += (
            f"### Page {page_number}\n\n"
        )

        preview_text += (
            page_text[:1500]
        )

        preview_text += "\n\n---\n\n"

    with st.expander(
        "Preview extracted document content"
    ):

        st.markdown(preview_text)


# ============================================================
# CHAT AREA
# ============================================================

st.markdown(
    '<div class="section-title">💬 Research conversation</div>',
    unsafe_allow_html=True
)


if not st.session_state.pages:

    st.markdown(
        """
        <div class="chat-info">

        ### 👋 Welcome

        Upload a PDF above to start your research
        conversation.

        You can ask questions such as:

        - What is the main purpose of this paper?
        - What methodology was used?
        - What were the main findings?
        - Explain this concept in simple words.
        - What limitations did the researchers mention?
        - Where does the paper discuss the results?

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if (
            message["role"] == "assistant"
            and "sources" in message
        ):

            if message["sources"]:

                st.caption(
                    "📖 Sources: "
                    + ", ".join(
                        f"Page {page}"
                        for page in message["sources"]
                    )
                )


# ============================================================
# CHAT INPUT
# ============================================================

if st.session_state.pages:

    question = st.chat_input(
        "Ask something about your document..."
    )

    if question:

        # Display user message
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):

            st.markdown(question)

        # Retrieval query
        retrieval_query = build_retrieval_query(
            question
        )

        relevant_chunks = retrieve_relevant_chunks(
            retrieval_query,
            st.session_state.chunks,
            top_k=4
        )

        # Generate answer
        with st.chat_message("assistant"):

            with st.spinner(
                "Researching your document..."
            ):

                if not relevant_chunks:

                    answer = (
                        "I couldn't find relevant "
                        "information for that question "
                        "in the uploaded document."
                    )

                else:

                    answer = ask_groq(
                        question,
                        relevant_chunks
                    )

            st.markdown(answer)

            source_pages = sorted(
                set(
                    chunk["page"]
                    for chunk in relevant_chunks
                )
            )

            if source_pages:

                st.caption(
                    "📖 Sources: "
                    + ", ".join(
                        f"Page {page}"
                        for page in source_pages
                    )
                )

        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": source_pages
        })

        # Source viewer
        if relevant_chunks:

            with st.expander(
                "🔎 View retrieved document sections"
            ):

                for chunk in relevant_chunks:

                    st.markdown(
                        f"""
                        <div class="source-card">

                        <div class="source-page">
                        📄 Page {chunk['page']}
                        </div>

                        <div>
                        {chunk['text']}
                        </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="app-footer">
        AI Research Assistant • Built for intelligent
        document exploration
    </div>
    """,
    unsafe_allow_html=True
)