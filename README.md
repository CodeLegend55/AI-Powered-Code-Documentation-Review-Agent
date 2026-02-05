# 🤖 AI-Powered Code Review & Documentation Agent

An intelligent multi-step LLM-based agent that analyzes code, provides quality feedback, and generates comprehensive documentation using RAG (Retrieval-Augmented Generation) and agentic workflows.

## 🌟 Features

- **Code Analysis**: Deep analysis of code for bugs, style violations, and best practices
- **Documentation Generation**: Automatic generation of Javadoc, Sphinx, Google-style docstrings
- **RAG-Powered Context**: Retrieves relevant standards and documentation from vector database
- **GitHub Integration**: Analyze Git diffs and pull requests
- **Defect Pre-flagging**: ML-based classifier to identify high-risk code sections
- **Multi-Language Support**: Python, JavaScript, Java, and more

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│                    Modern UI with Tailwind CSS                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│                    REST API Endpoints                            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌───────────────────┐
│  AST Parser   │   │ LangChain Agent │   │  Defect Classifier│
│  (tree-sitter)│   │   Orchestrator  │   │    (ML Model)     │
└───────────────┘   └────────┬────────┘   └───────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌───────────┐  ┌─────────────┐
        │   RAG    │  │    LLM    │  │  Doc Gen    │
        │(ChromaDB)│  │(OpenAI/   │  │  Module     │
        │          │  │ Local)    │  │             │
        └──────────┘  └───────────┘  └─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google AI Studio API Key (Free at https://aistudio.google.com/app/apikey)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

Create `.env` file:
```env
GOOGLE_API_KEY=your_google_api_key
GITHUB_TOKEN=your_github_token  # Optional
```

Start the backend:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to access the application.

## 📁 Project Structure

```
code/
├── backend/
│   ├── main.py                 # FastAPI application entry
│   ├── requirements.txt        # Python dependencies
│   ├── config.py              # Configuration settings
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── review_agent.py    # LangChain agent orchestrator
│   │   └── tools.py           # Agent tools
│   ├── services/
│   │   ├── __init__.py
│   │   ├── code_parser.py     # AST analysis
│   │   ├── rag_service.py     # RAG with ChromaDB
│   │   ├── doc_generator.py   # Documentation generation
│   │   ├── defect_classifier.py # ML defect detection
│   │   └── github_service.py  # GitHub integration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   └── data/
│       └── knowledge_base/    # Style guides & docs
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   └── styles/           # CSS styles
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🔧 Configuration

The application can be configured via environment variables or `config.py`:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI Studio API key for LLM | Required |
| `GITHUB_TOKEN` | GitHub token for repo access | Optional |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./chroma_db` |
| `MODEL_NAME` | LLM model to use | `gemini-1.5-flash` |

## 📖 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎓 Academic Information

**Project**: Senior Design Project (SDP)  
**Degree**: B.Tech Final Year  
**Focus**: Generative AI, LLM Orchestration, RAG Systems

## 📄 License

MIT License - See LICENSE file for details
