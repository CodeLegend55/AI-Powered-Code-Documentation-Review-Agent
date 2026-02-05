"""
LangChain Agent Tools
Custom tools for the code review agent
"""
from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from services.code_parser import code_parser
from services.rag_service import rag_service
from services.defect_classifier import defect_classifier
from services.doc_generator import doc_generator

class CodeParserInput(BaseModel):
    """Input schema for code parser tool"""
    code: str = Field(description="The code to parse")
    language: str = Field(description="Programming language (python, javascript, java)")

class CodeParserTool(BaseTool):
    """Tool for parsing code and extracting structure"""
    name: str = "code_parser"
    description: str = """Parses code to extract its structure including functions, classes, 
    imports, and complexity metrics. Use this to understand code structure before analysis."""
    args_schema: Type[BaseModel] = CodeParserInput
    
    def _run(self, code: str, language: str) -> str:
        result = code_parser.parse(code, language)
        
        output = f"Language: {result.language}\n"
        output += f"Complexity Score: {result.complexity_score}/100\n"
        output += f"Functions: {len(result.functions)}\n"
        output += f"Classes: {len(result.classes)}\n"
        output += f"Imports: {len(result.imports)}\n"
        
        if result.functions:
            output += "\nFunctions Found:\n"
            for func in result.functions:
                output += f"  - {func.name}({', '.join(p['name'] for p in func.parameters)})"
                output += f" -> {func.return_type or 'None'}\n"
        
        if result.classes:
            output += "\nClasses Found:\n"
            for cls in result.classes:
                output += f"  - {cls.name}"
                if cls.bases:
                    output += f" extends {', '.join(cls.bases)}"
                output += f" ({len(cls.methods)} methods)\n"
        
        if result.errors:
            output += f"\nParsing Errors: {result.errors}\n"
        
        return output

class RAGRetrievalInput(BaseModel):
    """Input schema for RAG retrieval tool"""
    query: str = Field(description="The query to search for relevant documentation")
    language: Optional[str] = Field(default=None, description="Filter by programming language")

class RAGRetrievalTool(BaseTool):
    """Tool for retrieving relevant documentation from knowledge base"""
    name: str = "knowledge_retrieval"
    description: str = """Retrieves relevant programming standards, style guides, and best practices 
    from the knowledge base. Use this to ground your code review in actual documentation."""
    args_schema: Type[BaseModel] = RAGRetrievalInput
    
    def _run(self, query: str, language: Optional[str] = None) -> str:
        # Ensure RAG is initialized
        rag_service.initialize()
        
        result = rag_service.retrieve(query, language=language, k=3)
        
        output = "Retrieved Documentation:\n\n"
        for i, (doc, source, score) in enumerate(zip(
            result.documents, result.sources, result.relevance_scores
        )):
            output += f"--- Source {i+1}: {source['title']} (relevance: {score:.2f}) ---\n"
            output += doc[:800] + "...\n\n" if len(doc) > 800 else doc + "\n\n"
        
        return output

class DefectAnalysisInput(BaseModel):
    """Input schema for defect analysis tool"""
    code: str = Field(description="The code to analyze for defects")
    language: str = Field(description="Programming language")

class DefectAnalysisTool(BaseTool):
    """Tool for analyzing code for potential defects"""
    name: str = "defect_analyzer"
    description: str = """Analyzes code for potential bugs, security issues, and anti-patterns 
    using ML-based classification. Use this to identify high-risk sections of code."""
    args_schema: Type[BaseModel] = DefectAnalysisInput
    
    def _run(self, code: str, language: str) -> str:
        result = defect_classifier.analyze(code, language)
        
        output = f"Defect Analysis Results:\n"
        output += f"Risk Score: {result.risk_score:.2f}/1.0\n"
        output += f"Risk Level: {result.risk_level.upper()}\n"
        output += f"Confidence: {result.confidence:.2f}\n\n"
        
        if result.flagged_sections:
            output += f"Flagged Sections ({len(result.flagged_sections)}):\n"
            for section in result.flagged_sections[:10]:  # Limit to 10
                output += f"  Line {section['line']}: [{section['severity'].upper()}] {section['issue']}\n"
                output += f"    Code: {section['code'][:60]}...\n" if len(section['code']) > 60 else f"    Code: {section['code']}\n"
        
        if result.issues_detected:
            output += f"\nAdditional Issues ({len(result.issues_detected)}):\n"
            for issue in result.issues_detected[:5]:
                output += f"  - {issue}\n"
        
        return output

class CodeMetricsInput(BaseModel):
    """Input schema for code metrics tool"""
    code: str = Field(description="The code to analyze")
    language: str = Field(description="Programming language")

class CodeMetricsTool(BaseTool):
    """Tool for getting code metrics"""
    name: str = "code_metrics"
    description: str = """Calculates various code metrics including line counts, 
    complexity, and function statistics. Use for quantitative code analysis."""
    args_schema: Type[BaseModel] = CodeMetricsInput
    
    def _run(self, code: str, language: str) -> str:
        metrics = code_parser.get_code_metrics(code, language)
        
        output = "Code Metrics:\n"
        output += f"  Total Lines: {metrics['total_lines']}\n"
        output += f"  Code Lines: {metrics['code_lines']}\n"
        output += f"  Blank Lines: {metrics['blank_lines']}\n"
        output += f"  Comment Lines: {metrics['comment_lines']}\n"
        output += f"  Functions: {metrics['functions_count']}\n"
        output += f"  Classes: {metrics['classes_count']}\n"
        output += f"  Imports: {metrics['imports_count']}\n"
        output += f"  Complexity Score: {metrics['complexity_score']:.1f}/100\n"
        output += f"  Avg Function Length: {metrics['avg_function_length']:.1f} lines\n"
        
        return output


def get_agent_tools():
    """Get all tools for the code review agent"""
    return [
        CodeParserTool(),
        RAGRetrievalTool(),
        DefectAnalysisTool(),
        CodeMetricsTool(),
    ]
