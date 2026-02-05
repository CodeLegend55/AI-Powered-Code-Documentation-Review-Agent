"""
RAG Service - Retrieval-Augmented Generation using ChromaDB
Provides context-aware code review using stored programming standards and documentation
"""
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib

from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import settings

@dataclass
class RetrievedContext:
    """Container for retrieved documents"""
    documents: List[str]
    sources: List[Dict[str, str]]
    relevance_scores: List[float]

class RAGService:
    """RAG service for retrieving relevant programming standards and documentation"""
    
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIR
        self.collection_name = settings.COLLECTION_NAME
        self.embeddings = None
        self.vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self._initialized = False
    
    def initialize(self):
        """Initialize the RAG service with embeddings and vector store"""
        if self._initialized:
            return
        
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY
            )
            
            # Create or load vector store
            if os.path.exists(self.persist_directory):
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_name=self.collection_name
                )
            else:
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings,
                    collection_name=self.collection_name
                )
                # Initialize with default knowledge base
                self._load_default_knowledge()
            
            self._initialized = True
            
        except Exception as e:
            print(f"RAG initialization error: {e}")
            self._initialized = False
    
    def _load_default_knowledge(self):
        """Load default programming standards and best practices"""
        default_docs = [
            # Python Best Practices
            {
                "content": """
# Python Best Practices - PEP 8 Style Guide

## Naming Conventions
- Use snake_case for functions and variables
- Use PascalCase for class names
- Use UPPER_CASE for constants
- Avoid single-letter variable names except for counters

## Code Layout
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 79 characters for code, 72 for docstrings
- Surround top-level functions and classes with two blank lines
- Use blank lines sparingly inside functions

## Imports
- Imports should be on separate lines
- Order: standard library, related third party, local application
- Avoid wildcard imports (from module import *)

## Comments and Docstrings
- Write docstrings for all public modules, functions, classes, and methods
- Use inline comments sparingly
- Comments should be complete sentences
                """,
                "title": "Python PEP 8 Style Guide",
                "doc_type": "style_guide",
                "language": "python"
            },
            # Python Security
            {
                "content": """
# Python Security Best Practices

## Input Validation
- Never trust user input
- Use parameterized queries for database operations
- Validate and sanitize all inputs

## Common Vulnerabilities
- SQL Injection: Use ORM or parameterized queries
- Command Injection: Avoid os.system(), use subprocess with shell=False
- Path Traversal: Validate file paths, use os.path.realpath()

## Secure Coding
- Don't store sensitive data in code
- Use environment variables for secrets
- Implement proper error handling without exposing internals
- Use secure random number generation (secrets module)

## Dependencies
- Keep dependencies updated
- Use virtual environments
- Review third-party packages before using
                """,
                "title": "Python Security Best Practices",
                "doc_type": "best_practice",
                "language": "python"
            },
            # JavaScript Best Practices
            {
                "content": """
# JavaScript Best Practices

## Modern JavaScript
- Use const by default, let when reassignment is needed
- Never use var
- Use arrow functions for callbacks
- Use template literals for string interpolation
- Use destructuring for cleaner code

## Async Programming
- Prefer async/await over raw promises
- Always handle promise rejections
- Use Promise.all for parallel async operations

## Error Handling
- Use try-catch blocks appropriately
- Create custom error types for specific errors
- Never swallow errors silently

## Performance
- Avoid memory leaks (remove event listeners)
- Use requestAnimationFrame for animations
- Debounce/throttle expensive operations
                """,
                "title": "JavaScript Best Practices",
                "doc_type": "style_guide", 
                "language": "javascript"
            },
            # Java Best Practices
            {
                "content": """
# Java Best Practices

## Naming Conventions
- Classes: PascalCase (e.g., UserService)
- Methods and variables: camelCase (e.g., getUserById)
- Constants: UPPER_SNAKE_CASE (e.g., MAX_SIZE)
- Packages: lowercase (e.g., com.company.project)

## Object-Oriented Design
- Favor composition over inheritance
- Program to interfaces, not implementations
- Follow SOLID principles
- Keep classes focused (Single Responsibility)

## Exception Handling
- Never catch generic Exception
- Use specific exception types
- Don't use exceptions for control flow
- Always close resources (use try-with-resources)

## Collections
- Use appropriate collection types
- Prefer interface types in declarations (List, not ArrayList)
- Consider using immutable collections when appropriate
                """,
                "title": "Java Best Practices",
                "doc_type": "style_guide",
                "language": "java"
            },
            # Documentation Standards
            {
                "content": """
# Documentation Standards

## Google Style Python Docstrings
```python
def function_name(param1: str, param2: int) -> bool:
    '''Brief description of function.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is empty.
    '''
```

## NumPy Style Docstrings
```python
def function_name(param1, param2):
    '''
    Brief description.

    Parameters
    ----------
    param1 : str
        Description of param1.
    param2 : int
        Description of param2.

    Returns
    -------
    bool
        Description of return value.
    '''
```

## JSDoc Style
```javascript
/**
 * Brief description.
 *
 * @param {string} param1 - Description of param1.
 * @param {number} param2 - Description of param2.
 * @returns {boolean} Description of return value.
 * @throws {Error} When something goes wrong.
 */
```
                """,
                "title": "Documentation Standards",
                "doc_type": "style_guide",
                "language": "general"
            },
            # Code Review Checklist
            {
                "content": """
# Code Review Checklist

## Functionality
- Does the code do what it's supposed to do?
- Are edge cases handled?
- Is error handling appropriate?

## Code Quality
- Is the code readable and well-organized?
- Are variable and function names descriptive?
- Is there any code duplication?
- Is the code modular and maintainable?

## Performance
- Are there any obvious performance issues?
- Are database queries optimized?
- Is caching used appropriately?

## Security
- Is user input validated?
- Are there any SQL injection risks?
- Is sensitive data handled properly?

## Testing
- Are there unit tests for new functionality?
- Do existing tests still pass?
- Is test coverage adequate?

## Documentation
- Are public APIs documented?
- Are complex algorithms explained?
- Is the README updated if needed?
                """,
                "title": "Code Review Checklist",
                "doc_type": "best_practice",
                "language": "general"
            }
        ]
        
        for doc in default_docs:
            self.add_document(
                content=doc["content"],
                title=doc["title"],
                doc_type=doc["doc_type"],
                language=doc.get("language")
            )
    
    def add_document(self, content: str, title: str, doc_type: str, 
                     language: Optional[str] = None) -> str:
        """Add a document to the knowledge base"""
        if not self._initialized:
            self.initialize()
        
        # Create document ID
        doc_id = hashlib.md5(f"{title}:{content[:100]}".encode()).hexdigest()
        
        # Split content into chunks
        chunks = self.text_splitter.split_text(content)
        
        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "doc_id": doc_id,
                    "title": title,
                    "doc_type": doc_type,
                    "language": language or "general",
                    "chunk_index": i
                }
            )
            documents.append(doc)
        
        # Add to vector store
        self.vectorstore.add_documents(documents)
        
        return doc_id
    
    def retrieve(self, query: str, language: Optional[str] = None, 
                 k: int = 5) -> RetrievedContext:
        """Retrieve relevant documents for a query"""
        if not self._initialized:
            self.initialize()
        
        # Build filter
        filter_dict = None
        if language:
            filter_dict = {"$or": [
                {"language": language},
                {"language": "general"}
            ]}
        
        # Perform similarity search
        try:
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query, k=k, filter=filter_dict
            )
        except Exception:
            # Fallback without filter if it fails
            results = self.vectorstore.similarity_search_with_relevance_scores(
                query, k=k
            )
        
        documents = []
        sources = []
        scores = []
        
        for doc, score in results:
            documents.append(doc.page_content)
            sources.append({
                "title": doc.metadata.get("title", "Unknown"),
                "doc_type": doc.metadata.get("doc_type", "unknown"),
                "language": doc.metadata.get("language", "general")
            })
            scores.append(float(score))
        
        return RetrievedContext(
            documents=documents,
            sources=sources,
            relevance_scores=scores
        )
    
    def get_context_for_review(self, code: str, language: str, 
                               focus_areas: List[str] = None) -> str:
        """Get formatted context for code review"""
        queries = [
            f"{language} best practices and style guide",
            f"{language} code review checklist",
            f"{language} common bugs and anti-patterns"
        ]
        
        if focus_areas:
            queries.extend([f"{language} {area}" for area in focus_areas])
        
        all_contexts = []
        seen_titles = set()
        
        for query in queries:
            result = self.retrieve(query, language=language, k=3)
            for doc, source in zip(result.documents, result.sources):
                if source["title"] not in seen_titles:
                    all_contexts.append(f"### {source['title']}\n{doc}")
                    seen_titles.add(source["title"])
        
        return "\n\n".join(all_contexts[:5])  # Limit to top 5 unique sources
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        if not self._initialized:
            self.initialize()
        
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            # Get unique documents
            results = collection.get(include=["metadatas"])
            doc_types = {}
            languages = {}
            
            for metadata in results.get("metadatas", []):
                if metadata:
                    dt = metadata.get("doc_type", "unknown")
                    lang = metadata.get("language", "unknown")
                    doc_types[dt] = doc_types.get(dt, 0) + 1
                    languages[lang] = languages.get(lang, 0) + 1
            
            return {
                "total_chunks": count,
                "documents_by_type": doc_types,
                "documents_by_language": languages
            }
        except Exception as e:
            return {"error": str(e)}


# Global RAG service instance
rag_service = RAGService()
