"""
Code Parser Service - AST Analysis for Multiple Languages
Extracts functions, classes, and code structure for analysis
"""
import ast
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class FunctionInfo:
    """Information about a parsed function"""
    name: str
    start_line: int
    end_line: int
    signature: str
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    body: str
    decorators: List[str]
    docstring: Optional[str]
    is_async: bool = False
    is_method: bool = False
    class_name: Optional[str] = None

@dataclass
class ClassInfo:
    """Information about a parsed class"""
    name: str
    start_line: int
    end_line: int
    bases: List[str]
    methods: List[FunctionInfo]
    attributes: List[Dict[str, Any]]
    docstring: Optional[str]
    decorators: List[str]

@dataclass
class ParseResult:
    """Complete parsing result"""
    language: str
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[str]
    global_variables: List[Dict[str, Any]]
    errors: List[str]
    complexity_score: float

class CodeParser:
    """Multi-language code parser using AST analysis"""
    
    def __init__(self):
        self.parsers = {
            'python': self._parse_python,
            'javascript': self._parse_javascript,
            'typescript': self._parse_javascript,  # Similar structure
            'java': self._parse_java,
        }
    
    def parse(self, code: str, language: str) -> ParseResult:
        """Parse code and extract structural information"""
        language = language.lower()
        
        if language in self.parsers:
            return self.parsers[language](code)
        else:
            # Fallback to regex-based parsing
            return self._parse_generic(code, language)
    
    def _parse_python(self, code: str) -> ParseResult:
        """Parse Python code using AST"""
        functions = []
        classes = []
        imports = []
        global_vars = []
        errors = []
        
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            
            for node in ast.walk(tree):
                # Extract imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            # Process top-level nodes
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func_info = self._extract_python_function(node, lines)
                    functions.append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_python_class(node, lines)
                    classes.append(class_info)
                    
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            global_vars.append({
                                'name': target.id,
                                'line': node.lineno,
                                'value': ast.unparse(node.value) if hasattr(ast, 'unparse') else str(node.value)
                            })
            
            complexity = self._calculate_complexity(tree)
            
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
            complexity = 0.0
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
            complexity = 0.0
        
        return ParseResult(
            language='python',
            functions=functions,
            classes=classes,
            imports=imports,
            global_variables=global_vars,
            errors=errors,
            complexity_score=complexity
        )
    
    def _extract_python_function(self, node: ast.FunctionDef, lines: List[str], 
                                   class_name: Optional[str] = None) -> FunctionInfo:
        """Extract information from a Python function node"""
        # Get parameters
        parameters = []
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'type': ast.unparse(arg.annotation) if arg.annotation and hasattr(ast, 'unparse') else None,
                'default': None
            }
            parameters.append(param)
        
        # Handle default values
        defaults = node.args.defaults
        if defaults:
            offset = len(parameters) - len(defaults)
            for i, default in enumerate(defaults):
                if hasattr(ast, 'unparse'):
                    parameters[offset + i]['default'] = ast.unparse(default)
        
        # Get return type
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        
        # Build signature
        params_str = []
        for p in parameters:
            s = p['name']
            if p['type']:
                s += f": {p['type']}"
            if p['default']:
                s += f" = {p['default']}"
            params_str.append(s)
        
        signature = f"def {node.name}({', '.join(params_str)})"
        if return_type:
            signature += f" -> {return_type}"
        
        # Get decorators
        decorators = []
        for dec in node.decorator_list:
            if hasattr(ast, 'unparse'):
                decorators.append(ast.unparse(dec))
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Get body
        body = '\n'.join(lines[node.lineno - 1:node.end_lineno])
        
        return FunctionInfo(
            name=node.name,
            start_line=node.lineno,
            end_line=node.end_lineno,
            signature=signature,
            parameters=parameters,
            return_type=return_type,
            body=body,
            decorators=decorators,
            docstring=docstring,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_method=class_name is not None,
            class_name=class_name
        )
    
    def _extract_python_class(self, node: ast.ClassDef, lines: List[str]) -> ClassInfo:
        """Extract information from a Python class node"""
        # Get base classes
        bases = []
        for base in node.bases:
            if hasattr(ast, 'unparse'):
                bases.append(ast.unparse(base))
        
        # Get methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._extract_python_function(item, lines, class_name=node.name)
                methods.append(method)
        
        # Get class attributes
        attributes = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attr = {
                    'name': item.target.id,
                    'type': ast.unparse(item.annotation) if item.annotation and hasattr(ast, 'unparse') else None,
                    'line': item.lineno
                }
                attributes.append(attr)
        
        # Get decorators
        decorators = []
        for dec in node.decorator_list:
            if hasattr(ast, 'unparse'):
                decorators.append(ast.unparse(dec))
        
        return ClassInfo(
            name=node.name,
            start_line=node.lineno,
            end_line=node.end_lineno,
            bases=bases,
            methods=methods,
            attributes=attributes,
            docstring=ast.get_docstring(node),
            decorators=decorators
        )
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity score"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Control flow statements add complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        # Normalize to 0-100 scale
        return min(100, complexity * 5)
    
    def _parse_javascript(self, code: str) -> ParseResult:
        """Parse JavaScript/TypeScript code using regex patterns"""
        functions = []
        classes = []
        imports = []
        errors = []
        
        lines = code.split('\n')
        
        # Extract imports
        import_pattern = r"import\s+(?:{[^}]+}|\*\s+as\s+\w+|\w+)\s+from\s+['\"]([^'\"]+)['\"]"
        imports = re.findall(import_pattern, code)
        
        # Extract functions
        func_patterns = [
            r"(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*(\w+))?\s*{",
            r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*(?::\s*(\w+))?\s*=>\s*{?",
            r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\([^)]*\)",
        ]
        
        for pattern in func_patterns:
            for match in re.finditer(pattern, code):
                name = match.group(1)
                line_num = code[:match.start()].count('\n') + 1
                
                # Find function body (simplified)
                start_idx = match.start()
                body_start = code.find('{', start_idx)
                if body_start != -1:
                    body, end_idx = self._find_matching_brace(code, body_start)
                    end_line = code[:end_idx].count('\n') + 1
                else:
                    body = ""
                    end_line = line_num
                
                functions.append(FunctionInfo(
                    name=name,
                    start_line=line_num,
                    end_line=end_line,
                    signature=match.group(0),
                    parameters=[],
                    return_type=None,
                    body=body,
                    decorators=[],
                    docstring=None,
                    is_async='async' in match.group(0)
                ))
        
        # Extract classes
        class_pattern = r"class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{"
        for match in re.finditer(class_pattern, code):
            name = match.group(1)
            base = match.group(2)
            line_num = code[:match.start()].count('\n') + 1
            
            classes.append(ClassInfo(
                name=name,
                start_line=line_num,
                end_line=line_num,  # Simplified
                bases=[base] if base else [],
                methods=[],
                attributes=[],
                docstring=None,
                decorators=[]
            ))
        
        return ParseResult(
            language='javascript',
            functions=functions,
            classes=classes,
            imports=imports,
            global_variables=[],
            errors=errors,
            complexity_score=self._estimate_complexity(code)
        )
    
    def _parse_java(self, code: str) -> ParseResult:
        """Parse Java code using regex patterns"""
        functions = []
        classes = []
        imports = []
        errors = []
        
        # Extract imports
        import_pattern = r"import\s+([\w.]+);"
        imports = re.findall(import_pattern, code)
        
        # Extract classes
        class_pattern = r"(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?\s*{"
        for match in re.finditer(class_pattern, code):
            name = match.group(1)
            base = match.group(2)
            interfaces = match.group(3)
            line_num = code[:match.start()].count('\n') + 1
            
            bases = []
            if base:
                bases.append(base)
            if interfaces:
                bases.extend([i.strip() for i in interfaces.split(',')])
            
            classes.append(ClassInfo(
                name=name,
                start_line=line_num,
                end_line=line_num,
                bases=bases,
                methods=[],
                attributes=[],
                docstring=None,
                decorators=[]
            ))
        
        # Extract methods
        method_pattern = r"(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w,\s]+)?\s*{"
        for match in re.finditer(method_pattern, code):
            return_type = match.group(1)
            name = match.group(2)
            params = match.group(3)
            line_num = code[:match.start()].count('\n') + 1
            
            # Skip constructors and common keywords
            if name in ['if', 'while', 'for', 'switch', 'try', 'catch']:
                continue
            
            # Parse parameters
            parameters = []
            if params.strip():
                for param in params.split(','):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        parameters.append({
                            'name': parts[-1],
                            'type': ' '.join(parts[:-1]),
                            'default': None
                        })
            
            functions.append(FunctionInfo(
                name=name,
                start_line=line_num,
                end_line=line_num,
                signature=f"{return_type} {name}({params})",
                parameters=parameters,
                return_type=return_type,
                body="",
                decorators=[],
                docstring=None
            ))
        
        return ParseResult(
            language='java',
            functions=functions,
            classes=classes,
            imports=imports,
            global_variables=[],
            errors=errors,
            complexity_score=self._estimate_complexity(code)
        )
    
    def _parse_generic(self, code: str, language: str) -> ParseResult:
        """Generic fallback parser using regex"""
        return ParseResult(
            language=language,
            functions=[],
            classes=[],
            imports=[],
            global_variables=[],
            errors=[f"No specific parser for {language}, using generic analysis"],
            complexity_score=self._estimate_complexity(code)
        )
    
    def _find_matching_brace(self, code: str, start: int) -> Tuple[str, int]:
        """Find matching closing brace"""
        count = 0
        for i, char in enumerate(code[start:], start):
            if char == '{':
                count += 1
            elif char == '}':
                count -= 1
                if count == 0:
                    return code[start:i+1], i
        return code[start:], len(code)
    
    def _estimate_complexity(self, code: str) -> float:
        """Estimate complexity using heuristics"""
        complexity = 1
        
        # Count control flow keywords
        keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch', '&&', '||', '?']
        for kw in keywords:
            complexity += code.count(kw)
        
        return min(100, complexity * 2)
    
    def get_code_metrics(self, code: str, language: str) -> Dict[str, Any]:
        """Get various code metrics"""
        lines = code.split('\n')
        
        # Count lines
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*')))
        code_lines = total_lines - blank_lines - comment_lines
        
        # Parse structure
        parse_result = self.parse(code, language)
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'blank_lines': blank_lines,
            'comment_lines': comment_lines,
            'functions_count': len(parse_result.functions),
            'classes_count': len(parse_result.classes),
            'imports_count': len(parse_result.imports),
            'complexity_score': parse_result.complexity_score,
            'avg_function_length': self._avg_function_length(parse_result.functions) if parse_result.functions else 0
        }
    
    def _avg_function_length(self, functions: List[FunctionInfo]) -> float:
        """Calculate average function length"""
        if not functions:
            return 0
        lengths = [f.end_line - f.start_line + 1 for f in functions]
        return sum(lengths) / len(lengths)


# Global parser instance
code_parser = CodeParser()
