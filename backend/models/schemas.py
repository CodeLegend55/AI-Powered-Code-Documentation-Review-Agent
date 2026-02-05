"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

class DocStyle(str, Enum):
    """Supported documentation styles"""
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    JAVADOC = "javadoc"
    JSDOC = "jsdoc"

class Language(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"

class Severity(str, Enum):
    """Issue severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"

# ============== Request Models ==============

class CodeReviewRequest(BaseModel):
    """Request model for code review"""
    code: str = Field(..., description="The code to review", min_length=1)
    language: Language = Field(Language.PYTHON, description="Programming language")
    doc_style: DocStyle = Field(DocStyle.GOOGLE, description="Documentation style")
    context: Optional[str] = Field(None, description="Additional context about the code")
    check_security: bool = Field(True, description="Include security analysis")
    generate_docs: bool = Field(True, description="Generate documentation")

class GitHubDiffRequest(BaseModel):
    """Request model for GitHub diff analysis"""
    repo_url: str = Field(..., description="GitHub repository URL")
    pr_number: Optional[int] = Field(None, description="Pull request number")
    commit_sha: Optional[str] = Field(None, description="Specific commit SHA")
    branch: str = Field("main", description="Branch name")

class DocumentationRequest(BaseModel):
    """Request model for documentation generation only"""
    code: str = Field(..., description="Code to document")
    language: Language = Field(Language.PYTHON, description="Programming language")
    doc_style: DocStyle = Field(DocStyle.GOOGLE, description="Documentation style")
    include_examples: bool = Field(True, description="Include usage examples")

class KnowledgeBaseUploadRequest(BaseModel):
    """Request to add documents to knowledge base"""
    content: str = Field(..., description="Document content")
    title: str = Field(..., description="Document title")
    doc_type: str = Field("style_guide", description="Type: style_guide, api_doc, best_practice")
    language: Optional[str] = Field(None, description="Associated programming language")

# ============== Response Models ==============

class CodeIssue(BaseModel):
    """Individual code issue"""
    line: Optional[int] = Field(None, description="Line number")
    column: Optional[int] = Field(None, description="Column number")
    severity: Severity = Field(..., description="Issue severity")
    category: str = Field(..., description="Issue category (style, bug, security, performance)")
    message: str = Field(..., description="Issue description")
    suggestion: Optional[str] = Field(None, description="Suggested fix")
    code_snippet: Optional[str] = Field(None, description="Relevant code snippet")

class FunctionDoc(BaseModel):
    """Generated documentation for a function"""
    name: str = Field(..., description="Function name")
    signature: str = Field(..., description="Function signature")
    docstring: str = Field(..., description="Generated docstring")
    start_line: Optional[int] = Field(None, description="Start line in original code")

class ClassDoc(BaseModel):
    """Generated documentation for a class"""
    name: str = Field(..., description="Class name")
    docstring: str = Field(..., description="Generated class docstring")
    methods: List[FunctionDoc] = Field(default_factory=list, description="Method documentation")
    start_line: Optional[int] = Field(None, description="Start line in original code")

class DefectPrediction(BaseModel):
    """ML-based defect prediction result"""
    risk_score: float = Field(..., ge=0, le=1, description="Risk score 0-1")
    risk_level: str = Field(..., description="low, medium, high")
    flagged_sections: List[Dict[str, Any]] = Field(default_factory=list, description="High-risk sections")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")

class RAGContext(BaseModel):
    """Retrieved context from RAG"""
    sources: List[Dict[str, str]] = Field(default_factory=list, description="Retrieved document sources")
    relevance_scores: List[float] = Field(default_factory=list, description="Relevance scores")

class CodeReviewResponse(BaseModel):
    """Complete code review response"""
    # Summary
    summary: str = Field(..., description="Executive summary of the review")
    overall_score: float = Field(..., ge=0, le=100, description="Code quality score 0-100")
    
    # Issues
    issues: List[CodeIssue] = Field(default_factory=list, description="List of identified issues")
    issues_count: Dict[str, int] = Field(default_factory=dict, description="Issue counts by severity")
    
    # Documentation
    documentation: Optional[str] = Field(None, description="Generated documentation")
    functions_documented: List[FunctionDoc] = Field(default_factory=list)
    classes_documented: List[ClassDoc] = Field(default_factory=list)
    
    # ML Predictions
    defect_prediction: Optional[DefectPrediction] = Field(None, description="ML defect analysis")
    
    # RAG Context
    rag_context: Optional[RAGContext] = Field(None, description="Retrieved context used")
    
    # Metadata
    language_detected: str = Field(..., description="Detected/specified language")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)

class DocumentationResponse(BaseModel):
    """Documentation generation response"""
    documented_code: str = Field(..., description="Code with generated documentation")
    functions: List[FunctionDoc] = Field(default_factory=list)
    classes: List[ClassDoc] = Field(default_factory=list)
    style_used: str = Field(..., description="Documentation style used")

class HealthResponse(BaseModel):
    """API health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    llm_status: str = Field(..., description="LLM connection status")
    vector_db_status: str = Field(..., description="Vector DB status")

class KnowledgeBaseStats(BaseModel):
    """Knowledge base statistics"""
    total_documents: int
    documents_by_type: Dict[str, int]
    last_updated: Optional[datetime]
