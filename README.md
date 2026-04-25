<p align="center">
  <img src="https://img.shields.io/badge/Amazon%20Bedrock-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white" alt="Amazon Bedrock" />
  <img src="https://img.shields.io/badge/Strands%20Agents-6C47FF?style=for-the-badge&logo=openai&logoColor=white" alt="Strands Agents" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
</p>

# 📘 RegCom Assistant — Policy & Compliance Agent

> AI-powered assistant for answering questions about **regulations, policies, and compliance** — built on **Amazon Bedrock** with RAG (Retrieval-Augmented Generation) and conversational memory.

RegCom Assistant is an intelligent chatbot that retrieves and summarizes information from an organization's regulatory and compliance knowledge base. So this AI agent provide high security and data privacy. It leverages Amazon Bedrock's foundation models combined with a vector-based Knowledge Base to deliver accurate, context-aware answers in natural Thai language.

---

## ✨ Key Highlights

| Feature | Description |
|---|---|
| 🧠 **RAG-Powered Intelligence** | Retrieves relevant regulatory documents from Amazon Bedrock Knowledge Base and synthesizes accurate answers — not just generic LLM responses |
| 💬 **Conversational Memory** | Remembers past conversations using AWS AgentCore Memory, enabling multi-turn dialogue with full context retention |
| ⚡ **Real-time Streaming** | Responses are streamed token-by-token for a responsive, ChatGPT-like experience |
| 🎨 **Modern Chat UI** | Glassmorphism design with smooth animations, typing indicators, and responsive layout built with Streamlit |
| 🔗 **Session Persistence** | Conversations persist across browser refreshes via URL-based session management and AWS-backed storage |
| 🚀 **CI/CD Pipeline** | Automated Docker image builds and deployment to Amazon ECR via GitHub Actions |
| 📄 **Source Attribution** | Every answer includes relevance scores and source document references for transparency and auditability |

---

## 🎯 Benefits

### For Organizations
- **Reduce compliance inquiries workload** — Employees can self-serve answers to common policy questions without waiting for HR or legal teams
- **Ensure consistency** — Answers are grounded in official documents, reducing the risk of misinterpretation or outdated information
- **Audit-ready responses** — Source attribution allows tracing every answer back to the original regulatory document
- **Scalable knowledge access** — Serve hundreds of users simultaneously without additional human resources

### For End Users
- **Instant answers** — Get accurate policy information in seconds instead of searching through lengthy documents
- **Natural language interaction** — Ask questions in everyday Thai language, no need to know exact document titles or section numbers
- **Conversation context** — Follow-up questions are understood in context, enabling natural multi-turn exploration of complex regulations
- **Accessible anywhere** — Web-based interface works on any device with a browser

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User (Browser)                              │
│                    Streamlit Chat Interface                          │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      chat_ui.py (Frontend)                           │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ Session Manager │  │ Chat Renderer│  │ History Loader (AWS)    │  │
│  │ (UUID-based)    │  │ (HTML/CSS)   │  │ (bedrock-agentcore)     │  │
│  └────────────────┘  └──────────────┘  └─────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     rag-comp.py (Agent Core)                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                    Strands Agent Framework                    │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │    │
│  │  │ System Prompt│  │  Tool: get_  │  │ AgentCore Memory   │  │    │
│  │  │ (Thai NLP)   │  │  data (RAG)  │  │ Session Manager    │  │    │
│  │  └─────────────┘  └──────┬───────┘  └────────┬───────────┘  │    │
│  └──────────────────────────┼───────────────────┼──────────────┘    │
└─────────────────────────────┼───────────────────┼──────────────────┘
                              │                   │
                              ▼                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        AWS Cloud Services                            │
│                                                                      │
│  ┌─────────────────────┐  ┌──────────────────────────────────────┐  │
│  │  Amazon Bedrock      │  │  Amazon Bedrock AgentCore Memory     │  │
│  │  Knowledge Base       │  │  (Conversation History Storage)     │  │
│  │  ┌────────────────┐  │  └──────────────────────────────────────┘  │
│  │  │ Vector Search   │  │                                           │
│  │  │ (Top-5 chunks)  │  │  ┌──────────────────────────────────────┐ │
│  │  └────────────────┘  │  │  Amazon Nova Pro v1 (Foundation Model)│ │
│  │  ┌────────────────┐  │  └──────────────────────────────────────┘  │
│  │  │ S3 Documents    │  │                                           │
│  │  │ (Source of Truth)│  │  ┌──────────────────────────────────────┐│
│  │  └────────────────┘  │  │  Amazon ECR (Container Registry)      ││
│  └─────────────────────┘  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### How It Works

1. **User sends a question** via the Streamlit chat interface
2. **Strands Agent** receives the message and determines whether to invoke the `get_data` tool
3. **RAG Retrieval** — The `get_data` tool queries Amazon Bedrock Knowledge Base using vector search, retrieving the top 5 most relevant document chunks
4. **Answer Generation** — Amazon Nova Pro synthesizes a Thai-language answer grounded in the retrieved documents
5. **Streaming Response** — The answer is streamed back to the UI token-by-token in real time
6. **Memory Persistence** — The conversation is saved to AWS AgentCore Memory for future reference and multi-turn context

---

## 🧩 Core Components

### `rag-comp.py` — Agent Core
The backbone of the system. Defines the Strands Agent with:
- **`get_data` tool** — Custom RAG tool that queries Amazon Bedrock Knowledge Base via vector search, returning ranked results with relevance scores and source attribution
- **System Prompt** — Carefully crafted Thai-language instructions that guide the agent's behavior, including graceful handling of out-of-scope queries
- **Session Manager** — AgentCore Memory integration for persistent conversation history across sessions

### `chat_ui.py` — Chat Interface
A polished Streamlit-based web interface featuring:
- **Glassmorphism design** with gradient backgrounds, blur effects, and smooth animations
- **Async streaming** for real-time token-by-token response rendering
- **Session management** via URL query parameters, supporting bookmarkable conversations
- **Chat history restoration** from AWS on page refresh
- **Responsive layout** with sidebar controls for session management

### `history.py` — Conversation History Utility
A diagnostic tool for inspecting stored conversation histories:
- Retrieves conversation events from AWS AgentCore Memory
- Exports chat logs to local text files for review and debugging

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Amazon Nova Pro v1 (via Amazon Bedrock) |
| **Agent Framework** | [Strands Agents SDK](https://github.com/strands-agents/sdk-python) |
| **Knowledge Base** | Amazon Bedrock Knowledge Base (Vector Search) |
| **Memory** | Amazon Bedrock AgentCore Memory |
| **Frontend** | Streamlit + Custom CSS (Glassmorphism) |
| **Cloud** | AWS (Bedrock, S3, ECR, AgentCore) |
| **CI/CD** | GitHub Actions → Amazon ECR |
| **Language** | Python 3.14+ |
| **Package Manager** | [uv](https://github.com/astral-sh/uv) |

---

## 📁 Project Structure

```
Policy&Compliance_Agent/
├── .github/
│   └── workflows/
│       └── github-flow.yml    # CI/CD: Build & push Docker image to ECR
├── docs/                      # Documentation assets
├── logs/                      # Exported conversation history logs
├── chat_ui.py                 # Streamlit chat interface (frontend)
├── rag-comp.py                # Strands Agent + RAG tool (backend core)
├── history.py                 # Conversation history inspection utility
├── main.py                    # Entry point (scaffolding)
├── pyproject.toml             # Python project configuration
├── .env                       # Environment variables (AWS credentials)
└── .gitignore
```

---

## 📄 License

This project is developed for internal organizational use.

---

<p align="center">
  <sub>Built with ❤️ using <b>Strands Agents</b> + <b>Amazon Bedrock</b></sub>
</p>
