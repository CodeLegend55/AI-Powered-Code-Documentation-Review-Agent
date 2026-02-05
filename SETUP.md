# 🚀 Quick Start Guide

## Prerequisites
- **Python 3.10+** (with pip)
- **Node.js 18+** (with npm)
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

---

## Step 1: Backend Setup

### 1.1 Navigate to backend directory
```powershell
cd backend
```

### 1.2 Create virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 1.3 Install dependencies
```powershell
pip install -r requirements.txt
```

### 1.4 Configure environment
```powershell
# Copy the example env file
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 1.5 Start the backend server
```powershell
uvicorn main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Step 2: Frontend Setup

### 2.1 Open a new terminal and navigate to frontend
```powershell
cd frontend
```

### 2.2 Install dependencies
```powershell
npm install
```

### 2.3 Start the development server
```powershell
npm run dev
```

The frontend will be available at:
- **App**: http://localhost:5173

---

## 🎉 You're Ready!

1. Open http://localhost:5173 in your browser
2. You'll see the Hero page - click "Start Reviewing Code"
3. Paste your code in the editor
4. Select the language and documentation style
5. Click "Review Code" to get AI-powered analysis

---

## Features Available

| Feature | Endpoint | Description |
|---------|----------|-------------|
| Full Code Review | POST /api/review | Complete analysis with documentation |
| Quick Review | POST /api/review/quick | Fast feedback without full analysis |
| Defect Analysis | POST /api/analyze/defects | ML-based defect detection only |
| Code Metrics | POST /api/analyze/metrics | Get code metrics and structure |
| Generate Docs | POST /api/document | Generate documentation only |
| GitHub PR Review | POST /api/github/review-pr | Review a GitHub Pull Request |
| Knowledge Base | GET/POST /api/knowledge/* | Manage RAG knowledge base |

---

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.10+)
- Ensure virtual environment is activated
- Check if port 8000 is available

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Delete `node_modules` and run `npm install` again
- Check if port 5173 is available

### "Google API key not configured" error
- Make sure `.env` file exists in `backend/` folder
- Ensure `GOOGLE_API_KEY` is set correctly (no quotes needed)
- Get your free API key at: https://aistudio.google.com/app/apikey
- Restart the backend server after changing `.env`

### CORS errors
- Both servers must be running (backend on 8000, frontend on 5173)
- Check that the backend CORS settings include the frontend URL

---

## Project Structure

```
code/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (create this)
│   ├── agents/              # LangChain agent logic
│   ├── services/            # Core services (RAG, parser, etc.)
│   └── models/              # Pydantic schemas
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React app
│   │   ├── components/      # UI components
│   │   ├── services/        # API service
│   │   └── store/           # State management
│   ├── package.json
│   └── vite.config.js
│
└── README.md                # Project documentation
```

---

## Next Steps

1. **Customize Knowledge Base**: Add your own style guides via `/api/knowledge/upload`
2. **GitHub Integration**: Add `GITHUB_TOKEN` to `.env` for PR reviews
3. **Fine-tune Settings**: Adjust `config.py` for your preferences
4. **Deploy**: See deployment guides for production setup

Happy coding! 🎉
