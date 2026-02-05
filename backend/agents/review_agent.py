"""
Code Review Agent - Multi-step LLM Orchestration
Multi-step agent for comprehensive code review and documentation generation
"""
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from config import settings, DOC_STYLES
from services.code_parser import code_parser
from services.rag_service import rag_service
from services.defect_classifier import defect_classifier
from services.doc_generator import doc_generator

@dataclass
class ReviewResult:
    """Complete review result"""
    summary: str
    overall_score: float
    issues: List[Dict[str, Any]]
    issues_count: Dict[str, int]
    documentation: Optional[str]
    functions_documented: List[Dict[str, Any]]
    classes_documented: List[Dict[str, Any]]
    defect_prediction: Dict[str, Any]
    rag_context: Dict[str, Any]
    language: str
    processing_time: float
    agent_reasoning: str = ""

class CodeReviewAgent:
    """
    Multi-step LLM-based agent for code review and documentation.
    
    Workflow:
    1. Parse code structure (AST analysis)
    2. Run defect pre-flagging (ML classifier)
    3. Retrieve relevant standards (RAG)
    4. Analyze code and generate feedback (LLM)
    5. Generate documentation (LLM)
    """
    
    def __init__(self):
        self.llm = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the agent with LLM"""
        if self._initialized:
            return
        
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        self._initialized = True
    
    async def review_code(self, code: str, language: str, 
                          doc_style: str = "google",
                          check_security: bool = True,
                          generate_docs: bool = True,
                          context: str = "") -> ReviewResult:
        """
        Perform comprehensive code review.
        
        This is the main entry point that orchestrates the multi-step review process.
        """
        start_time = time.time()
        
        if not self._initialized:
            self.initialize()
        
        # Step 1: Parse code structure
        parse_result = code_parser.parse(code, language)
        metrics = code_parser.get_code_metrics(code, language)
        
        # Step 2: Run defect pre-flagging
        defect_result = defect_classifier.analyze(code, language)
        
        # Step 3: Retrieve relevant standards (RAG)
        rag_service.initialize()
        rag_context = rag_service.get_context_for_review(
            code, language, 
            focus_areas=["security", "performance"] if check_security else None
        )
        
        # Step 4: Generate code review using LLM
        review_prompt = self._build_review_prompt(
            code=code,
            language=language,
            metrics=metrics,
            defect_result=defect_result,
            rag_context=rag_context,
            context=context
        )
        
        # Run LLM for detailed analysis
        agent_result = await self._run_llm_analysis(review_prompt)
        
        # Step 5: Generate documentation if requested
        documentation = None
        functions_documented = []
        classes_documented = []
        
        if generate_docs:
            doc_result = doc_generator.generate_documentation(
                code, language, doc_style, rag_context
            )
            documentation = doc_result.documented_code
            functions_documented = doc_result.functions
            classes_documented = doc_result.classes
        
        # Parse issues from LLM result and defect analysis
        issues = self._extract_issues(agent_result, defect_result)
        issues_count = self._count_issues(issues)
        
        # Calculate overall score
        overall_score = self._calculate_score(
            metrics, defect_result, issues_count
        )
        
        processing_time = time.time() - start_time
        
        return ReviewResult(
            summary=agent_result.get("summary", "Review completed"),
            overall_score=overall_score,
            issues=issues,
            issues_count=issues_count,
            documentation=documentation,
            functions_documented=functions_documented,
            classes_documented=classes_documented,
            defect_prediction={
                "risk_score": defect_result.risk_score,
                "risk_level": defect_result.risk_level,
                "flagged_sections": defect_result.flagged_sections,
                "confidence": defect_result.confidence
            },
            rag_context={
                "sources_used": len(rag_context.split("###")) - 1 if rag_context else 0,
                "context_preview": rag_context[:500] if rag_context else ""
            },
            language=language,
            processing_time=processing_time,
            agent_reasoning=agent_result.get("reasoning", "")
        )
    
    def _build_review_prompt(self, code: str, language: str,
                             metrics: Dict, defect_result: Any,
                             rag_context: str, context: str) -> str:
        """Build the prompt for code review"""
        prompt = f"""Please review the following {language} code comprehensively.

## Code to Review:
```{language}
{code}
```

## Code Metrics:
- Total Lines: {metrics['total_lines']}
- Code Lines: {metrics['code_lines']}
- Functions: {metrics['functions_count']}
- Classes: {metrics['classes_count']}
- Complexity Score: {metrics['complexity_score']}/100

## Pre-flagged Issues (ML Analysis):
- Risk Level: {defect_result.risk_level.upper()}
- Risk Score: {defect_result.risk_score:.2f}
- Flagged Sections: {len(defect_result.flagged_sections)}

{f"## Additional Context: {context}" if context else ""}

## Relevant Standards and Best Practices:
{rag_context[:3000]}

## Your Task:
1. Analyze the code structure and logic
2. Identify bugs, security issues, and anti-patterns
3. Check adherence to best practices from the standards above
4. Provide specific, actionable suggestions for improvement
5. Rate the code quality and summarize your findings

Please provide your review in the following format:
- SUMMARY: Brief overview of code quality
- CRITICAL ISSUES: Security vulnerabilities and bugs (if any)
- WARNINGS: Style violations and potential problems
- SUGGESTIONS: Improvements and best practices
- POSITIVE ASPECTS: What the code does well"""
        
        return prompt
    
    async def _run_llm_analysis(self, prompt: str) -> Dict[str, Any]:
        """Run the LLM for detailed analysis"""
        try:
            # Create messages for analysis
            messages = [
                SystemMessage(content="""You are an expert code reviewer and documentation specialist. 
Your task is to thoroughly analyze code for quality, bugs, security issues, and best practices.
Always be constructive and educational in your feedback.
Prioritize issues by severity: security > bugs > performance > style."""),
                HumanMessage(content=prompt)
            ]
            
            # Invoke LLM
            response = await self.llm.ainvoke(messages)
            output = response.content
            
            # Parse the output into structured format
            summary = ""
            reasoning = output
            
            # Extract summary if present
            if "SUMMARY:" in output:
                summary_start = output.find("SUMMARY:") + 8
                summary_end = output.find("\n", summary_start + 50)
                if summary_end > summary_start:
                    summary = output[summary_start:summary_end].strip()
            else:
                # Use first paragraph as summary
                summary = output.split("\n\n")[0][:300]
            
            return {
                "summary": summary,
                "reasoning": reasoning,
                "raw_output": output
            }
        except Exception as e:
            return {
                "summary": f"Review completed with limitations: {str(e)}",
                "reasoning": str(e),
                "raw_output": ""
            }
    
    def _extract_issues(self, agent_result: Dict, 
                        defect_result: Any) -> List[Dict[str, Any]]:
        """Extract and combine issues from various sources"""
        issues = []
        
        # Add defect classifier issues
        for section in defect_result.flagged_sections:
            issues.append({
                "line": section.get("line"),
                "column": None,
                "severity": section.get("severity", "warning"),
                "category": "defect",
                "message": section.get("issue", ""),
                "suggestion": None,
                "code_snippet": section.get("code", "")
            })
        
        # Parse issues from LLM output
        output = agent_result.get("raw_output", "")
        
        # Look for critical issues section
        if "CRITICAL" in output.upper():
            # Simple extraction of critical issues
            critical_section = output.upper().split("CRITICAL")[1].split("\n")[1:5]
            for line in critical_section:
                if line.strip() and not line.strip().startswith(("WARNING", "SUGGESTION")):
                    issues.append({
                        "line": None,
                        "column": None,
                        "severity": "error",
                        "category": "critical",
                        "message": line.strip().lstrip("-").strip(),
                        "suggestion": None,
                        "code_snippet": None
                    })
        
        return issues
    
    def _count_issues(self, issues: List[Dict]) -> Dict[str, int]:
        """Count issues by severity"""
        counts = {"error": 0, "warning": 0, "info": 0, "suggestion": 0, "security": 0}
        for issue in issues:
            severity = issue.get("severity", "info")
            if severity in counts:
                counts[severity] += 1
        return counts
    
    def _calculate_score(self, metrics: Dict, defect_result: Any,
                         issues_count: Dict) -> float:
        """Calculate overall code quality score (0-100)"""
        score = 100.0
        
        # Deduct for complexity
        if metrics['complexity_score'] > 50:
            score -= (metrics['complexity_score'] - 50) * 0.3
        
        # Deduct for risk score
        score -= defect_result.risk_score * 30
        
        # Deduct for issues
        score -= issues_count.get("error", 0) * 10
        score -= issues_count.get("security", 0) * 15
        score -= issues_count.get("warning", 0) * 3
        score -= issues_count.get("info", 0) * 1
        
        # Bonus for good metrics
        if metrics['comment_lines'] > 0:
            comment_ratio = metrics['comment_lines'] / max(metrics['code_lines'], 1)
            if 0.1 <= comment_ratio <= 0.3:
                score += 5  # Good comment ratio
        
        return max(0, min(100, round(score, 1)))
    
    def quick_review(self, code: str, language: str) -> Dict[str, Any]:
        """
        Perform a quick synchronous review without full agent orchestration.
        Useful for fast feedback loops.
        """
        if not self._initialized:
            self.initialize()
        
        # Quick analysis
        metrics = code_parser.get_code_metrics(code, language)
        defect_result = defect_classifier.analyze(code, language)
        
        # Quick LLM call
        quick_prompt = f"""Quickly review this {language} code and provide 3-5 key observations:

```{language}
{code[:2000]}
```

Be concise. Focus on the most important issues."""
        
        response = self.llm.invoke([HumanMessage(content=quick_prompt)])
        
        return {
            "observations": response.content,
            "risk_level": defect_result.risk_level,
            "complexity": metrics['complexity_score'],
            "issues_found": len(defect_result.flagged_sections)
        }


# Global agent instance
review_agent = CodeReviewAgent()
