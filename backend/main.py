"""
AI-Powered Code Review & Documentation Agent
FastAPI Backend Application

This is the main entry point for the backend API.
"""
import os
import time
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings, DOC_STYLES
from models.schemas import (
    CodeReviewRequest, CodeReviewResponse, DocumentationRequest,
    DocumentationResponse, GitHubDiffRequest, HealthResponse,
    KnowledgeBaseUploadRequest, KnowledgeBaseStats,
    CodeIssue, FunctionDoc, ClassDoc, DefectPrediction, RAGContext,
    Severity
)
from agents.review_agent import review_agent
from services.code_parser import code_parser
from services.rag_service import rag_service
from services.doc_generator import doc_generator
from services.defect_classifier import defect_classifier
from services.github_service import github_service

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    print("🚀 Starting Code Review Agent...")
    
    # Initialize services
    try:
        if settings.GOOGLE_API_KEY:
            rag_service.initialize()
            review_agent.initialize()
            doc_generator.initialize()
            print("✅ All services initialized successfully")
        else:
            print("⚠️ GOOGLE_API_KEY not set - LLM features disabled")
    except Exception as e:
        print(f"⚠️ Service initialization warning: {e}")
    
    yield
    
    print("👋 Shutting down Code Review Agent...")

# Create FastAPI app
app = FastAPI(
    title="AI Code Review Agent",
    description="""
    🤖 AI-Powered Code Review & Documentation Agent
    
    This API provides comprehensive code review capabilities using:
    - **RAG (Retrieval-Augmented Generation)** for context-aware analysis
    - **LangChain Agents** for multi-step orchestration
    - **ML-based Defect Detection** for pre-flagging issues
    - **Automated Documentation Generation**
    
    ## Features
    - Code quality analysis and scoring
    - Security vulnerability detection
    - Style guide compliance checking
    - Automatic docstring generation
    - GitHub integration for PR reviews
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Health & Info Endpoints ==============

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API info"""
    return {
        "name": "AI Code Review Agent",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs",
        "health_url": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    """Check API health status"""
    llm_status = "connected" if settings.GOOGLE_API_KEY else "not_configured"
    
    try:
        vector_db_status = "connected" if rag_service._initialized else "not_initialized"
    except:
        vector_db_status = "error"
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        llm_status=llm_status,
        vector_db_status=vector_db_status
    )

@app.get("/config", tags=["Info"])
async def get_config():
    """Get available configuration options"""
    return {
        "supported_languages": settings.SUPPORTED_LANGUAGES,
        "documentation_styles": list(DOC_STYLES.keys()),
        "model": settings.MODEL_NAME,
        "github_enabled": github_service.is_available()
    }

# ============== Code Review Endpoints ==============

@app.post("/api/review", response_model=CodeReviewResponse, tags=["Code Review"])
async def review_code(request: CodeReviewRequest):
    """
    Perform comprehensive code review.
    
    This endpoint orchestrates the full review pipeline:
    1. AST parsing for code structure
    2. ML-based defect pre-flagging
    3. RAG retrieval for relevant standards
    4. LLM analysis with agent tools
    5. Optional documentation generation
    """
    start_time = time.time()
    
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Google API key not configured. Please set GOOGLE_API_KEY in environment."
        )
    
    if len(request.code) > settings.MAX_CODE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Code too long. Maximum {settings.MAX_CODE_LENGTH} characters allowed."
        )
    
    try:
        # Run the review agent
        result = await review_agent.review_code(
            code=request.code,
            language=request.language.value,
            doc_style=request.doc_style.value,
            check_security=request.check_security,
            generate_docs=request.generate_docs,
            context=request.context or ""
        )
        
        # Convert to response model
        issues = [
            CodeIssue(
                line=issue.get("line"),
                column=issue.get("column"),
                severity=Severity(issue.get("severity", "info")),
                category=issue.get("category", "general"),
                message=issue.get("message", ""),
                suggestion=issue.get("suggestion"),
                code_snippet=issue.get("code_snippet")
            )
            for issue in result.issues
        ]
        
        functions_documented = [
            FunctionDoc(
                name=func.get("name", ""),
                signature=func.get("signature", ""),
                docstring=func.get("docstring", ""),
                start_line=func.get("start_line")
            )
            for func in result.functions_documented
        ]
        
        classes_documented = [
            ClassDoc(
                name=cls.get("name", ""),
                docstring=cls.get("docstring", ""),
                methods=[
                    FunctionDoc(
                        name=m.get("name", ""),
                        signature=m.get("signature", ""),
                        docstring=m.get("docstring", ""),
                        start_line=m.get("start_line")
                    )
                    for m in cls.get("methods", [])
                ],
                start_line=cls.get("start_line")
            )
            for cls in result.classes_documented
        ]
        
        defect_pred = DefectPrediction(
            risk_score=result.defect_prediction["risk_score"],
            risk_level=result.defect_prediction["risk_level"],
            flagged_sections=result.defect_prediction["flagged_sections"],
            confidence=result.defect_prediction["confidence"]
        )
        
        rag_ctx = RAGContext(
            sources=[{"title": f"Source {i+1}", "type": "standard"} 
                    for i in range(result.rag_context.get("sources_used", 0))],
            relevance_scores=[]
        )
        
        return CodeReviewResponse(
            summary=result.summary,
            overall_score=result.overall_score,
            issues=issues,
            issues_count=result.issues_count,
            documentation=result.documentation,
            functions_documented=functions_documented,
            classes_documented=classes_documented,
            defect_prediction=defect_pred,
            rag_context=rag_ctx,
            language_detected=result.language,
            processing_time=time.time() - start_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review/quick", tags=["Code Review"])
async def quick_review(request: CodeReviewRequest):
    """
    Perform a quick code review without full agent orchestration.
    Faster response but less comprehensive.
    """
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(status_code=503, detail="Google API key not configured")
    
    try:
        result = review_agent.quick_review(
            code=request.code,
            language=request.language.value
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/defects", tags=["Code Review"])
async def analyze_defects(request: CodeReviewRequest):
    """
    Run defect analysis only (without full review).
    Uses ML-based classifier for fast defect detection.
    """
    result = defect_classifier.analyze(request.code, request.language.value)
    
    return {
        "risk_score": result.risk_score,
        "risk_level": result.risk_level,
        "flagged_sections": result.flagged_sections,
        "confidence": result.confidence,
        "issues_detected": result.issues_detected,
        "severity_summary": defect_classifier.get_severity_summary(result.flagged_sections)
    }

@app.post("/api/analyze/metrics", tags=["Code Review"])
async def analyze_metrics(request: CodeReviewRequest):
    """Get code metrics without full review"""
    metrics = code_parser.get_code_metrics(request.code, request.language.value)
    parse_result = code_parser.parse(request.code, request.language.value)
    
    return {
        "metrics": metrics,
        "structure": {
            "functions": [
                {"name": f.name, "line": f.start_line, "params": len(f.parameters)}
                for f in parse_result.functions
            ],
            "classes": [
                {"name": c.name, "line": c.start_line, "methods": len(c.methods)}
                for c in parse_result.classes
            ],
            "imports": parse_result.imports[:20],  # Limit imports
            "errors": parse_result.errors
        }
    }

# ============== Documentation Endpoints ==============

@app.post("/api/document", response_model=DocumentationResponse, tags=["Documentation"])
async def generate_documentation(request: DocumentationRequest):
    """
    Generate documentation for code.
    Supports multiple documentation styles (Google, NumPy, Sphinx, JSDoc).
    """
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(status_code=503, detail="Google API key not configured")
    
    try:
        # Get RAG context for better documentation
        rag_service.initialize()
        context = rag_service.get_context_for_review(
            request.code, 
            request.language.value,
            focus_areas=["documentation"]
        )
        
        result = doc_generator.generate_documentation(
            code=request.code,
            language=request.language.value,
            style=request.doc_style.value,
            context=context
        )
        
        return DocumentationResponse(
            documented_code=result.documented_code,
            functions=[
                FunctionDoc(
                    name=f.get("name", ""),
                    signature=f.get("signature", ""),
                    docstring=f.get("docstring", ""),
                    start_line=f.get("start_line")
                )
                for f in result.functions
            ],
            classes=[
                ClassDoc(
                    name=c.get("name", ""),
                    docstring=c.get("docstring", ""),
                    methods=[
                        FunctionDoc(
                            name=m.get("name", ""),
                            signature=m.get("signature", ""),
                            docstring=m.get("docstring", ""),
                            start_line=m.get("start_line")
                        )
                        for m in c.get("methods", [])
                    ],
                    start_line=c.get("start_line")
                )
                for c in result.classes
            ],
            style_used=result.style
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/document/styles", tags=["Documentation"])
async def get_documentation_styles():
    """Get available documentation styles with examples"""
    return {
        style: {
            "name": info["name"],
            "description": info["description"],
            "template_preview": info["template"][:200] + "..."
        }
        for style, info in DOC_STYLES.items()
    }

# ============== GitHub Integration Endpoints ==============

@app.post("/api/github/review-pr", tags=["GitHub"])
async def review_pull_request(request: GitHubDiffRequest):
    """
    Review a GitHub Pull Request.
    Analyzes all changed files and provides comprehensive review.
    """
    if not github_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="GitHub integration not configured. Set GITHUB_TOKEN in environment."
        )
    
    if not request.pr_number:
        raise HTTPException(status_code=400, detail="PR number is required")
    
    try:
        # Get PR diff
        diff = await github_service.get_pull_request_diff(
            request.repo_url, 
            request.pr_number
        )
        
        # Review each changed file
        file_reviews = []
        for file_change in diff.files_changed:
            if file_change["language"] in settings.SUPPORTED_LANGUAGES:
                # Parse the patch to get code
                code_parts = github_service.parse_diff_to_code(file_change["patch"])
                
                if code_parts["added"]:
                    # Analyze added code
                    defects = defect_classifier.analyze(
                        code_parts["added"],
                        file_change["language"]
                    )
                    
                    file_reviews.append({
                        "filename": file_change["filename"],
                        "language": file_change["language"],
                        "additions": file_change["additions"],
                        "deletions": file_change["deletions"],
                        "risk_level": defects.risk_level,
                        "issues": defects.flagged_sections[:5]  # Top 5 issues
                    })
        
        return {
            "repo": diff.repo,
            "pr_number": request.pr_number,
            "branch": diff.branch,
            "total_additions": diff.additions,
            "total_deletions": diff.deletions,
            "files_reviewed": len(file_reviews),
            "file_reviews": file_reviews
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/github/review-commit", tags=["GitHub"])
async def review_commit(request: GitHubDiffRequest):
    """Review a specific commit"""
    if not github_service.is_available():
        raise HTTPException(status_code=503, detail="GitHub integration not configured")
    
    if not request.commit_sha:
        raise HTTPException(status_code=400, detail="Commit SHA is required")
    
    try:
        diff = await github_service.get_commit_diff(
            request.repo_url,
            request.commit_sha
        )
        
        return {
            "repo": diff.repo,
            "commit": request.commit_sha,
            "files_changed": len(diff.files_changed),
            "additions": diff.additions,
            "deletions": diff.deletions,
            "files": [
                {
                    "filename": f["filename"],
                    "status": f["status"],
                    "language": f["language"]
                }
                for f in diff.files_changed
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== Knowledge Base Endpoints ==============

@app.post("/api/knowledge/upload", tags=["Knowledge Base"])
async def upload_to_knowledge_base(request: KnowledgeBaseUploadRequest):
    """Add a document to the RAG knowledge base"""
    try:
        rag_service.initialize()
        doc_id = rag_service.add_document(
            content=request.content,
            title=request.title,
            doc_type=request.doc_type,
            language=request.language
        )
        
        return {
            "status": "success",
            "document_id": doc_id,
            "message": f"Document '{request.title}' added to knowledge base"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/stats", response_model=KnowledgeBaseStats, tags=["Knowledge Base"])
async def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        rag_service.initialize()
        stats = rag_service.get_stats()
        
        return KnowledgeBaseStats(
            total_documents=stats.get("total_chunks", 0),
            documents_by_type=stats.get("documents_by_type", {}),
            last_updated=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/knowledge/search", tags=["Knowledge Base"])
async def search_knowledge_base(query: str, language: Optional[str] = None):
    """Search the knowledge base"""
    try:
        rag_service.initialize()
        result = rag_service.retrieve(query, language=language, k=5)
        
        return {
            "query": query,
            "results": [
                {
                    "content": doc[:500],
                    "source": source,
                    "relevance": score
                }
                for doc, source, score in zip(
                    result.documents,
                    result.sources,
                    result.relevance_scores
                )
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
