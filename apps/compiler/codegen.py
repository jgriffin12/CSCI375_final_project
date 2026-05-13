import json
from pathlib import Path
from typing import Any

from apps.compiler.ast_nodes import Program
from apps.compiler.semantic import PolicySemanticAnalyzer


class PolicyCodeGenerator:
    """Generate JSON configuration consumed by CJ Secure."""

    def __init__(self, analyzer: PolicySemanticAnalyzer | None = None) -> None:
        self.analyzer = analyzer or PolicySemanticAnalyzer()

    def generate_dict(self, program: Program, source_name: str = "<memory>") -> dict[str, Any]:
        """Generate a Python dictionary representing the checked policy."""
        compiled = self.analyzer.analyze(program)
        compiled["metadata"] = {
            "language": "CJ Secure Policy Language",
            "source": source_name,
        }
        return compiled

    def write_json(self, program: Program, output_path: str, source_name: str) -> None:
        """Generate and write JSON output to disk."""
        compiled = self.generate_dict(program, source_name)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(compiled, indent=2), encoding="utf-8")
