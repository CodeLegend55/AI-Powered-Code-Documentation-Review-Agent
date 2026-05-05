# Antigen: LLM-Powered Code Review and Documentation System

An end-to-end intelligent agent capable of code review, vulnerability detection, and automated documentation generation using local LLMs (Ollama) and RAG (ChromaDB) enhanced by custom fine-tuning data (DiverseVul, CVEFixes, CodeSearchNet).

## System Architecture
*   **Frontend**: React, Vite, Monaco Editor, Framer Motion
*   **Backend**: Node.js, Express, Multer
*   **AI/RAG Layer**: Ollama (Local LLM), ChromaDB (Vector Search)
*   **ML Pipeline**: Python, Unsloth, Hugging Face TRL (For external GPU Fine-Tuning)
*   **Deployment**: Docker Compose

## Getting Started

### 1. Prerequisites
*   Docker & Docker Compose installed
*   Node.js v18+ (for local un-containerized dev)

### 2. Running the Project

#### Option A: Full-Stack Deployment (Recommended)
You can deploy the entire stack (Frontend, Backend, ChromaDB, and Ollama) using Docker Compose:
```bash
docker-compose up --build -d
```
The application will be available at `http://localhost:80`.

**Note on initial startup:** Ollama may take some time to download the embedding models (`nomic-embed-text`) dynamically. Feel free to pull it manually via `docker exec -it <ollama_container_id> ollama pull nomic-embed-text`.

#### Option B: Local Development (Without Docker)
If you prefer running the servers natively for development:

**1. Start the Backend API:**
```bash
cd backend
npm install
npm run dev
```
*The Node.js backend will run on `http://localhost:5000`.*

**2. Start the Frontend UI:**
```bash
cd frontend
npm install
npm run dev
```
*The Vite dev server will be available at `http://localhost:5173`.*

**3. External Dependencies:**
To use the AI features locally, ensure you have **Ollama** and **ChromaDB** running.

*Start ChromaDB:*
You can easily spin up a local ChromaDB instance on port `8000` using Docker:
```bash
docker run -p 8000:8000 chromadb/chroma
```
*(Alternatively, you can run it natively via Python: `pip install chromadb` -> `chroma run --path ./chroma_data`)*

*Start Ollama:*
Ensure Ollama is running in the background on port `11434` with your trained model loaded.
```bash
ollama serve
```

### 3. Machine Learning SFT Pipeline (Kaggle)
To fine-tune your own deepseek-coder/llama-3 on vulnerability datasets to make it an expert reviewer, consult the `ml-pipeline/KAGGLE_GUIDE.md`. 
Once you extract your fine-tuned `GGUF` model:
1. Import it into Ollama locally.
2. Expose it under the name `custom-code-reviewer`.

*(If you skip this, you can configure `backend/.env` to point `OLLAMA_MODEL` to any standard model like `llama3` or `deepseek-coder`)*

## Features
- **Real-time Code Analysis**: Paste code into the Monaco Editor and receive line-by-line analyses.
- **RAG Supported**: Scans contextual vulnerability databases via ChromaDB to augment Ollama prompts.
- **Glassmorphism UI**: High-end React components styled with Framer Motion.
