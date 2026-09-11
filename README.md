# 🤖 AI Research Assistant

An AI-powered PDF research assistant that allows users to upload a document, ask questions about its content, and have natural conversations with the document using a Large Language Model.

The application is designed to make document research faster and easier by allowing users to interact with their PDFs through a simple conversational interface.

## 🚀 Live Demo

**Live App:** 
(https://ai-research-assistant-th4nnhtvrnfrhsxvxm6zjf.streamlit.app/)
---

## ✨ Features

* 📄 **PDF Upload** — Upload research papers, reports, notes, or other PDF documents.
* 🔍 **Document Understanding** — Extracts and processes the text contained in uploaded PDFs.
* 💬 **AI-Powered Q&A** — Ask questions about the uploaded document and receive relevant answers.
* 🔄 **Multi-Turn Conversations** — Continue asking follow-up questions while maintaining conversational context.
* 🧠 **LLM-Powered Responses** — Uses Groq-powered Large Language Models to generate natural-language answers.
* 🎨 **Professional Streamlit Interface** — Clean and user-friendly interface designed for practical document research.
* 🔐 **Secure API Configuration** — API credentials are managed through environment variables and are not stored in the repository.

---

## 🧩 How It Works

The application follows a simple document-questioning workflow:

```text
User
  │
  ▼
Upload PDF
  │
  ▼
Extract PDF Text
  │
  ▼
Process & Prepare Document
  │
  ▼
User Asks a Question
  │
  ▼
Relevant Document Context
  │
  ▼
Groq LLM
  │
  ▼
AI-Generated Answer
  │
  ▼
User
```

This allows users to interact with their documents conversationally instead of manually searching through long PDF files.

---

## 🛠️ Tech Stack

| Technology        | Purpose                               |
| ----------------- | ------------------------------------- |
| **Python**        | Core application logic                |
| **Streamlit**     | Interactive web interface             |
| **Groq API**      | Large Language Model inference        |
| **PyPDF2**        | PDF text extraction                   |
| **python-dotenv** | Local environment variable management |

---

## 📂 Project Structure

```text
AI-Research-Assistant/
│
├── research_assistant.py    # Main Streamlit application
├── requirements.txt         # Python dependencies
├── .gitignore               # Ignored files and secrets
└── README.md                # Project documentation
```

---

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/hamzakhan876/AI-Research-Assistant.git
```

### 2. Move into the project directory

```bash
cd AI-Research-Assistant
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Create your environment file

Create a file named:

```text
.env
```

Add your Groq API key:

```text
GROQ_API_KEY=your_api_key_here
```

### 7. Run the application

```bash
streamlit run research_assistant.py
```

The application will then be available locally through the Streamlit development server.

---

## 🔐 Environment Variables

The application requires the following environment variable:

```text
GROQ_API_KEY
```

For local development, store it inside `.env`.

For Streamlit Cloud deployment, add it through the application's **Secrets** settings.

**Never commit your `.env` file or API key to GitHub.**

---

## ☁️ Deployment

The application can be deployed using **Streamlit Community Cloud**.

Basic deployment steps:

1. Push the project to GitHub.
2. Connect the repository to Streamlit Community Cloud.
3. Select the `main` branch.
4. Select `research_assistant.py` as the main file.
5. Add `GROQ_API_KEY` to Streamlit Secrets.
6. Deploy the application.

---

## 🎯 Use Cases

The AI Research Assistant can be useful for:

* 📚 Research papers
* 📑 Technical documentation
* 📊 Business reports
* 🎓 Academic notes
* 📖 Study material
* 📝 Long-form PDF documents
* 🔎 Quickly understanding large documents

---

## 🔮 Future Improvements

Potential improvements include:

* Semantic search using vector embeddings
* Retrieval-Augmented Generation (RAG)
* Support for multiple documents
* Source/page citations
* Conversation history
* Document summarization
* Improved chunk retrieval
* Support for additional document formats
* More advanced document indexing

---

## 👨‍💻 Author

**Hamza Ahmed Khan**

Aspiring Generative AI Engineer focused on building practical AI applications using Python, LLMs, APIs, and modern AI development tools.

### Current Focus

* Generative AI
* Large Language Models
* AI Application Development
* Agentic AI
* Python
* LLM-powered applications

---


