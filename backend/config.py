"""
Configuration settings for the Code Review Agent
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    GOOGLE_API_KEY: str = ""
    GITHUB_TOKEN: Optional[str] = None
    
    # LLM Configuration
    MODEL_NAME: str = "gemini-1.5-flash"
    EMBEDDING_MODEL: str = "models/embedding-001"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.2
    
    # Vector Database
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    COLLECTION_NAME: str = "code_standards"
    
    # Application Settings
    DEBUG: bool = True
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Code Analysis
    SUPPORTED_LANGUAGES: list = ["python", "javascript", "java", "typescript", "cpp", "go"]
    MAX_CODE_LENGTH: int = 50000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Documentation Style Templates
DOC_STYLES = {
    "google": {
        "name": "Google Style",
        "description": "Google's Python docstring style",
        "template": '''"""
{summary}

{extended_description}

Args:
{args}

Returns:
{returns}

Raises:
{raises}

Example:
{example}
"""'''
    },
    "numpy": {
        "name": "NumPy Style", 
        "description": "NumPy documentation style",
        "template": '''"""
{summary}

{extended_description}

Parameters
----------
{parameters}

Returns
-------
{returns}

Examples
--------
{examples}
"""'''
    },
    "sphinx": {
        "name": "Sphinx/reStructuredText",
        "description": "Sphinx documentation style",
        "template": '''"""
{summary}

{extended_description}

:param {param}: {param_desc}
:type {param}: {param_type}
:returns: {returns}
:rtype: {return_type}
:raises {exception}: {exception_desc}
"""'''
    },
    "javadoc": {
        "name": "Javadoc Style",
        "description": "Java documentation style",
        "template": '''/**
 * {summary}
 *
 * {extended_description}
 *
 * @param {param} {param_desc}
 * @return {returns}
 * @throws {exception} {exception_desc}
 */'''
    },
    "jsdoc": {
        "name": "JSDoc Style",
        "description": "JavaScript documentation style",
        "template": '''/**
 * {summary}
 *
 * {extended_description}
 *
 * @param {{{param_type}}} {param} - {param_desc}
 * @returns {{{return_type}}} {returns}
 * @throws {{{exception}}} {exception_desc}
 * @example
 * {example}
 */'''
    }
}

# Code Quality Rules
CODE_QUALITY_RULES = {
    "python": [
        "Follow PEP 8 style guide",
        "Use meaningful variable names",
        "Add type hints to function parameters and return values",
        "Keep functions under 50 lines",
        "Avoid global variables",
        "Use list comprehensions where appropriate",
        "Handle exceptions properly",
        "Avoid bare except clauses"
    ],
    "javascript": [
        "Follow ESLint recommended rules",
        "Use const/let instead of var",
        "Use arrow functions where appropriate",
        "Avoid callback hell - use async/await",
        "Handle promises properly",
        "Use meaningful variable names",
        "Avoid global variables"
    ],
    "java": [
        "Follow Java naming conventions",
        "Use meaningful class and method names",
        "Keep methods focused (single responsibility)",
        "Handle exceptions properly",
        "Use interfaces for abstraction",
        "Avoid magic numbers",
        "Close resources properly"
    ]
}
