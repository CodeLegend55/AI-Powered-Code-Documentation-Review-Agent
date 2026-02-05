"""
Documentation Generator Service
Generates comprehensive documentation for code using LLM
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from config import settings, DOC_STYLES
from services.code_parser import code_parser, FunctionInfo, ClassInfo, ParseResult

@dataclass
class GeneratedDoc:
    """Container for generated documentation"""
    original_code: str
    documented_code: str
    functions: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    style: str

class DocumentationGenerator:
    """Service for generating code documentation using LLM"""
    
    def __init__(self):
        self.llm = None
        self._initialized = False
    
    def initialize(self):
        """Initialize the LLM"""
        if self._initialized:
            return
        
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            temperature=0.2,
            google_api_key=settings.GOOGLE_API_KEY
        )
        self._initialized = True
    
    def generate_function_doc(self, func: FunctionInfo, language: str, 
                               style: str, context: str = "") -> str:
        """Generate documentation for a single function"""
        if not self._initialized:
            self.initialize()
        
        style_info = DOC_STYLES.get(style, DOC_STYLES["google"])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical documentation writer. 
Generate comprehensive, accurate documentation for code following the specified style.
Be precise about parameter types, return types, and potential exceptions.
Include meaningful examples when appropriate.

Documentation Style: {style_name}
Style Description: {style_description}

Reference Context:
{context}"""),
            ("human", """Generate documentation for this {language} function:

Function Name: {func_name}
Signature: {signature}
Parameters: {parameters}
Return Type: {return_type}
Is Async: {is_async}

Function Body:
```{language}
{body}
```

Generate ONLY the docstring/documentation comment, nothing else. Follow the {style_name} style exactly.""")
        ])
        
        params_str = ", ".join([
            f"{p['name']}: {p.get('type', 'Any')}" + (f" = {p['default']}" if p.get('default') else "")
            for p in func.parameters
        ])
        
        response = self.llm.invoke(prompt.format_messages(
            style_name=style_info["name"],
            style_description=style_info["description"],
            context=context[:2000] if context else "No additional context",
            language=language,
            func_name=func.name,
            signature=func.signature,
            parameters=params_str,
            return_type=func.return_type or "Unknown",
            is_async=func.is_async,
            body=func.body[:3000]  # Limit body length
        ))
        
        return response.content.strip()
    
    def generate_class_doc(self, cls: ClassInfo, language: str,
                           style: str, context: str = "") -> Dict[str, Any]:
        """Generate documentation for a class and its methods"""
        if not self._initialized:
            self.initialize()
        
        style_info = DOC_STYLES.get(style, DOC_STYLES["google"])
        
        # Generate class-level docstring
        class_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical documentation writer.
Generate comprehensive class documentation following the specified style.

Documentation Style: {style_name}

Reference Context:
{context}"""),
            ("human", """Generate documentation for this {language} class:

Class Name: {class_name}
Base Classes: {bases}
Attributes: {attributes}
Methods: {methods}

Generate ONLY the class-level docstring/documentation comment.""")
        ])
        
        attrs_str = ", ".join([f"{a['name']}: {a.get('type', 'Any')}" for a in cls.attributes])
        methods_str = ", ".join([m.name for m in cls.methods])
        
        class_doc = self.llm.invoke(class_prompt.format_messages(
            style_name=style_info["name"],
            context=context[:1500] if context else "No additional context",
            language=language,
            class_name=cls.name,
            bases=", ".join(cls.bases) if cls.bases else "None",
            attributes=attrs_str or "None",
            methods=methods_str or "None"
        )).content.strip()
        
        # Generate method docs
        method_docs = []
        for method in cls.methods:
            method_doc = self.generate_function_doc(method, language, style, context)
            method_docs.append({
                "name": method.name,
                "signature": method.signature,
                "docstring": method_doc,
                "start_line": method.start_line
            })
        
        return {
            "name": cls.name,
            "docstring": class_doc,
            "methods": method_docs,
            "start_line": cls.start_line
        }
    
    def generate_documentation(self, code: str, language: str, 
                                style: str = "google", 
                                context: str = "") -> GeneratedDoc:
        """Generate documentation for entire code"""
        if not self._initialized:
            self.initialize()
        
        # Parse the code
        parse_result = code_parser.parse(code, language)
        
        functions_documented = []
        classes_documented = []
        
        # Document standalone functions
        for func in parse_result.functions:
            if not func.is_method:  # Skip class methods, they're handled with classes
                docstring = self.generate_function_doc(func, language, style, context)
                functions_documented.append({
                    "name": func.name,
                    "signature": func.signature,
                    "docstring": docstring,
                    "start_line": func.start_line
                })
        
        # Document classes
        for cls in parse_result.classes:
            class_doc = self.generate_class_doc(cls, language, style, context)
            classes_documented.append(class_doc)
        
        # Insert documentation into code
        documented_code = self._insert_documentation(
            code, language, functions_documented, classes_documented, parse_result
        )
        
        return GeneratedDoc(
            original_code=code,
            documented_code=documented_code,
            functions=functions_documented,
            classes=classes_documented,
            style=style
        )
    
    def _insert_documentation(self, code: str, language: str,
                              functions: List[Dict], classes: List[Dict],
                              parse_result: ParseResult) -> str:
        """Insert generated documentation into code"""
        lines = code.split('\n')
        insertions = []  # (line_number, docstring)
        
        # Collect all insertions
        for func in functions:
            if func.get("start_line"):
                insertions.append((func["start_line"], func["docstring"], "function"))
        
        for cls in classes:
            if cls.get("start_line"):
                insertions.append((cls["start_line"], cls["docstring"], "class"))
                for method in cls.get("methods", []):
                    if method.get("start_line"):
                        insertions.append((method["start_line"], method["docstring"], "method"))
        
        # Sort by line number in reverse order to maintain line numbers while inserting
        insertions.sort(key=lambda x: x[0], reverse=True)
        
        # Insert docstrings
        for line_num, docstring, doc_type in insertions:
            idx = line_num - 1
            if idx < len(lines):
                # Get indentation of the function/class definition
                original_line = lines[idx]
                indent = len(original_line) - len(original_line.lstrip())
                indent_str = ' ' * (indent + 4)  # Add extra indent for docstring content
                
                # Format docstring with proper indentation
                formatted_doc = self._format_docstring(docstring, indent_str, language)
                
                # Insert after the definition line
                # Find the line with the colon (for Python) or opening brace
                insert_idx = idx + 1
                if language == 'python':
                    # Find the line ending with ':'
                    while insert_idx < len(lines) and not lines[insert_idx - 1].rstrip().endswith(':'):
                        insert_idx += 1
                
                lines.insert(insert_idx, formatted_doc)
        
        return '\n'.join(lines)
    
    def _format_docstring(self, docstring: str, indent: str, language: str) -> str:
        """Format docstring with proper indentation"""
        # Clean up the docstring
        docstring = docstring.strip()
        
        # Remove code block markers if present
        if docstring.startswith('```'):
            lines = docstring.split('\n')
            docstring = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
        
        # Add indentation to each line
        doc_lines = docstring.split('\n')
        formatted_lines = []
        for i, line in enumerate(doc_lines):
            if i == 0:
                formatted_lines.append(indent[4:] + line)  # First line less indented
            else:
                formatted_lines.append(indent + line.strip() if line.strip() else '')
        
        return '\n'.join(formatted_lines)
    
    def generate_quick_summary(self, code: str, language: str) -> str:
        """Generate a quick summary of what the code does"""
        if not self._initialized:
            self.initialize()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a code analyst. Provide brief, clear summaries of code functionality."),
            ("human", """Provide a brief summary (2-3 sentences) of what this {language} code does:

```{language}
{code}
```

Summary:""")
        ])
        
        response = self.llm.invoke(prompt.format_messages(
            language=language,
            code=code[:5000]
        ))
        
        return response.content.strip()


# Global documentation generator instance
doc_generator = DocumentationGenerator()
