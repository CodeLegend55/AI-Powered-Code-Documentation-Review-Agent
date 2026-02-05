"""
Defect Classifier Service
ML-based classifier to pre-flag potential code issues
Uses pattern recognition and heuristics with optional GAN-style training
"""
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import hashlib

@dataclass
class DefectPrediction:
    """Result of defect analysis"""
    risk_score: float
    risk_level: str
    flagged_sections: List[Dict[str, Any]]
    confidence: float
    issues_detected: List[str]

class DefectClassifier:
    """
    ML-based defect classifier that pre-flags high-risk code sections.
    Uses a combination of:
    1. Pattern matching for known anti-patterns
    2. Statistical analysis of code structure
    3. ML classification based on code features
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 3))
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self._is_trained = False
        
        # Known anti-patterns by language
        self.anti_patterns = {
            "python": [
                (r"except\s*:", "Bare except clause catches all exceptions", "error"),
                (r"eval\s*\(", "Use of eval() is a security risk", "security"),
                (r"exec\s*\(", "Use of exec() is a security risk", "security"),
                (r"from\s+\w+\s+import\s+\*", "Wildcard import pollutes namespace", "warning"),
                (r"global\s+\w+", "Global variable usage", "warning"),
                (r"print\s*\(.*\)\s*$", "Debug print statement", "info"),
                (r"#\s*TODO", "TODO comment found", "info"),
                (r"#\s*FIXME", "FIXME comment found", "warning"),
                (r"#\s*HACK", "HACK comment found", "warning"),
                (r"password\s*=\s*['\"]", "Hardcoded password detected", "security"),
                (r"api[_-]?key\s*=\s*['\"]", "Hardcoded API key detected", "security"),
                (r"sleep\s*\(\s*\d+\s*\)", "Sleep call may indicate polling anti-pattern", "warning"),
                (r"except\s+Exception\s*:", "Catching generic Exception", "warning"),
                (r"\.format\(.*\)\s*$", "Consider using f-strings for formatting", "suggestion"),
                (r"^\s*pass\s*$", "Empty block with pass", "info"),
                (r"assert\s+", "Assert statement (disabled in optimized mode)", "warning"),
                (r"os\.system\s*\(", "os.system() is vulnerable to command injection", "security"),
            ],
            "javascript": [
                (r"\bvar\s+", "Use let/const instead of var", "warning"),
                (r"eval\s*\(", "Use of eval() is a security risk", "security"),
                (r"innerHTML\s*=", "innerHTML can lead to XSS vulnerabilities", "security"),
                (r"document\.write\s*\(", "document.write() is deprecated", "warning"),
                (r"==\s*null|null\s*==", "Use === for strict equality", "warning"),
                (r"!=\s*null|null\s*!=", "Use !== for strict inequality", "warning"),
                (r"console\.log\s*\(", "Console log statement (debug)", "info"),
                (r"debugger", "Debugger statement found", "warning"),
                (r"alert\s*\(", "Alert statement (debug/bad UX)", "warning"),
                (r"\.then\s*\(.*\.then\s*\(", "Promise chain - consider async/await", "suggestion"),
                (r"callback.*callback", "Nested callbacks - consider async/await", "warning"),
                (r"new\s+Function\s*\(", "Dynamic function creation is risky", "security"),
                (r"setTimeout\s*\(['\"]", "String in setTimeout is like eval", "security"),
            ],
            "java": [
                (r"catch\s*\(\s*Exception\s+", "Catching generic Exception", "warning"),
                (r"catch\s*\(\s*Throwable\s+", "Catching Throwable is too broad", "error"),
                (r"e\.printStackTrace\s*\(\s*\)", "printStackTrace() in production code", "warning"),
                (r"System\.out\.print", "System.out usage (use logger)", "warning"),
                (r"public\s+\w+\s+\w+\s*;", "Public field without getter/setter", "warning"),
                (r"new\s+String\s*\(\s*['\"]", "Unnecessary String object creation", "suggestion"),
                (r"==\s*\"|\"\s*==", "String comparison with == instead of equals()", "error"),
                (r"\.equals\s*\(\s*null\s*\)", "null.equals() will throw NPE", "error"),
                (r"synchronized\s*\(\s*this\s*\)", "Synchronizing on 'this' is risky", "warning"),
                (r"Thread\.sleep\s*\(", "Thread.sleep() in production code", "warning"),
                (r"//\s*TODO", "TODO comment found", "info"),
                (r"//\s*FIXME", "FIXME comment found", "warning"),
            ],
            "general": [
                (r"password|passwd|pwd", "Potential password handling", "security"),
                (r"secret|api[_-]?key|token", "Potential secret/token handling", "security"),
                (r"TODO|FIXME|HACK|XXX", "Unfinished code marker", "warning"),
                (r"[A-Za-z]+\d{3,}", "Magic number in identifier", "info"),
            ]
        }
        
        # Code smell patterns
        self.code_smells = {
            "long_function": (50, "Function is too long (> 50 lines)"),
            "many_parameters": (5, "Too many parameters (> 5)"),
            "deep_nesting": (4, "Deep nesting level (> 4)"),
            "long_line": (120, "Line too long (> 120 chars)"),
            "complex_condition": (3, "Complex boolean condition (> 3 operators)"),
        }
        
        # Initialize with synthetic training data
        self._initialize_training()
    
    def _initialize_training(self):
        """Initialize the classifier with synthetic training data"""
        # Generate synthetic training samples
        training_samples = self._generate_synthetic_data()
        
        if len(training_samples) > 0:
            X = [sample["code"] for sample in training_samples]
            y = [sample["label"] for sample in training_samples]
            
            try:
                X_vectorized = self.vectorizer.fit_transform(X)
                self.classifier.fit(X_vectorized, y)
                self._is_trained = True
            except Exception as e:
                print(f"Training error: {e}")
                self._is_trained = False
    
    def _generate_synthetic_data(self) -> List[Dict[str, Any]]:
        """
        Generate synthetic training data (GAN-inspired approach)
        Creates both 'clean' and 'defective' code samples for training
        """
        samples = []
        
        # Clean code examples
        clean_samples = [
            """def calculate_sum(numbers: List[int]) -> int:
    '''Calculate the sum of numbers.'''
    if not numbers:
        return 0
    return sum(numbers)""",
            """async def fetch_data(url: str) -> dict:
    '''Fetch data from URL with proper error handling.'''
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
    except HTTPError as e:
        logger.error(f"HTTP error: {e}")
        raise""",
            """class UserService:
    '''Service for user operations.'''
    
    def __init__(self, repository: UserRepository):
        self._repository = repository
    
    def get_user(self, user_id: int) -> Optional[User]:
        '''Get user by ID.'''
        return self._repository.find_by_id(user_id)""",
        ]
        
        # Defective code examples
        defective_samples = [
            """def process(x):
    try:
        result = eval(x)
        exec(x)
    except:
        pass
    return result""",
            """def login(user, pwd):
    password = "admin123"
    if pwd == password:
        global logged_in
        logged_in = True
    print("Login: " + pwd)""",
            """def fetch(url):
    import os
    os.system("curl " + url)
    data = None
    if data == None:
        pass""",
            """var x = 1;
eval(userInput);
document.innerHTML = data;
console.log(x);""",
        ]
        
        for code in clean_samples:
            samples.append({"code": code, "label": 0})
        
        for code in defective_samples:
            samples.append({"code": code, "label": 1})
        
        # Generate more variations
        for _ in range(20):
            samples.append({"code": self._generate_clean_code(), "label": 0})
            samples.append({"code": self._generate_defective_code(), "label": 1})
        
        return samples
    
    def _generate_clean_code(self) -> str:
        """Generate a clean code sample"""
        templates = [
            "def {name}({params}) -> {ret}:\n    '''{doc}'''\n    return {value}",
            "class {name}:\n    '''{doc}'''\n    def __init__(self):\n        pass",
            "async def {name}():\n    '''{doc}'''\n    result = await operation()\n    return result",
        ]
        
        names = ["process", "calculate", "fetch", "handle", "validate"]
        params = ["data: dict", "items: list", "value: int", "name: str"]
        docs = ["Process the data.", "Calculate result.", "Handle operation."]
        
        template = np.random.choice(templates)
        return template.format(
            name=np.random.choice(names),
            params=np.random.choice(params),
            ret="dict",
            doc=np.random.choice(docs),
            value="result"
        )
    
    def _generate_defective_code(self) -> str:
        """Generate a defective code sample"""
        templates = [
            "def {name}():\n    try:\n        eval(input())\n    except:\n        pass",
            "var {name};\nconsole.log({name});\neval(data);",
            "def {name}(x):\n    global state\n    exec(x)\n    password = 'secret123'",
            "function {name}() {{\n    document.innerHTML = data;\n    eval(code);\n}}",
        ]
        
        names = ["process", "handle", "execute", "run"]
        
        template = np.random.choice(templates)
        return template.format(name=np.random.choice(names))
    
    def analyze(self, code: str, language: str = "python") -> DefectPrediction:
        """Analyze code for potential defects"""
        issues = []
        flagged_sections = []
        
        lines = code.split('\n')
        
        # Pattern-based detection
        patterns = self.anti_patterns.get(language, []) + self.anti_patterns.get("general", [])
        
        for pattern, message, severity in patterns:
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(f"Line {i+1}: {message}")
                    flagged_sections.append({
                        "line": i + 1,
                        "code": line.strip(),
                        "issue": message,
                        "severity": severity,
                        "pattern": pattern
                    })
        
        # Code smell detection
        smell_issues = self._detect_code_smells(code, lines)
        issues.extend(smell_issues)
        
        # ML-based classification
        ml_score = self._ml_classify(code)
        
        # Calculate overall risk score
        severity_weights = {"error": 1.0, "security": 0.9, "warning": 0.5, "info": 0.2, "suggestion": 0.1}
        
        pattern_score = 0
        for section in flagged_sections:
            pattern_score += severity_weights.get(section.get("severity", "info"), 0.2)
        
        # Normalize pattern score
        pattern_score = min(1.0, pattern_score / 5)
        
        # Combine scores
        risk_score = (0.4 * ml_score + 0.6 * pattern_score)
        risk_score = min(1.0, max(0.0, risk_score))
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return DefectPrediction(
            risk_score=round(risk_score, 3),
            risk_level=risk_level,
            flagged_sections=flagged_sections,
            confidence=0.8 if self._is_trained else 0.5,
            issues_detected=issues
        )
    
    def _detect_code_smells(self, code: str, lines: List[str]) -> List[str]:
        """Detect code smells"""
        issues = []
        
        # Long lines
        max_line_len = self.code_smells["long_line"][0]
        for i, line in enumerate(lines):
            if len(line) > max_line_len:
                issues.append(f"Line {i+1}: {self.code_smells['long_line'][1]} ({len(line)} chars)")
        
        # Deep nesting
        max_nesting = self.code_smells["deep_nesting"][0]
        for i, line in enumerate(lines):
            indent = len(line) - len(line.lstrip())
            nesting = indent // 4
            if nesting > max_nesting:
                issues.append(f"Line {i+1}: {self.code_smells['deep_nesting'][1]} (level {nesting})")
        
        # Complex conditions
        complex_pattern = r'(and|or|\&\&|\|\|)'
        for i, line in enumerate(lines):
            operators = len(re.findall(complex_pattern, line, re.IGNORECASE))
            if operators > self.code_smells["complex_condition"][0]:
                issues.append(f"Line {i+1}: {self.code_smells['complex_condition'][1]}")
        
        return issues
    
    def _ml_classify(self, code: str) -> float:
        """Use ML classifier to predict defect probability"""
        if not self._is_trained:
            return 0.5  # Neutral score if not trained
        
        try:
            X = self.vectorizer.transform([code])
            proba = self.classifier.predict_proba(X)[0]
            return float(proba[1])  # Probability of being defective
        except Exception:
            return 0.5
    
    def get_severity_summary(self, flagged_sections: List[Dict]) -> Dict[str, int]:
        """Get count of issues by severity"""
        summary = {"error": 0, "security": 0, "warning": 0, "info": 0, "suggestion": 0}
        for section in flagged_sections:
            sev = section.get("severity", "info")
            summary[sev] = summary.get(sev, 0) + 1
        return summary


# Global classifier instance
defect_classifier = DefectClassifier()
