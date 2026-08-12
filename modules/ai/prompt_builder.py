from dataclasses import dataclass, field

# ----- Coding Rules mặc định theo ngôn ngữ -----
DEFAULT_RULES: dict[str, list[str]] = {
    "python": [
        "Follow PEP 8 coding conventions",
        "Use type hints for function parameters and return types",
        "Use docstrings for all public functions and classes",
        "Avoid mutable default arguments",
        "Prefer list comprehensions over map/filter where readable",
    ],
    "javascript": [
        "Use const/let instead of var",
        "Use arrow functions for callbacks",
        "Avoid == (use === instead)",
        "Handle promises with async/await instead of .then chains",
        "Use destructuring where appropriate",
    ],
    "java": [
        "Follow Java naming conventions (camelCase methods, PascalCase classes)",
        "Use Optional instead of returning null",
        "Prefer interfaces over abstract classes",
        "Close resources with try-with-resources",
        "Avoid raw types in generics",
    ],
    "general": [
        "Keep functions small and focused (Single Responsibility)",
        "Use meaningful variable and function names",
        "Avoid deep nesting (max 3 levels)",
        "Remove dead code and unused imports",
        "Add error handling for edge cases",
    ],
}


@dataclass
class PromptBuilder:
    """
    Build prompt cho AI review code.

    Ví dụ sử dụng:
        builder = PromptBuilder(
            source_code="def add(a, b): return a+b",
            language="python",
        )
        builder.add_rules(["No global variables"])
        prompt = builder.build()
    """

    source_code: str
    language: str = "general"
    file_name: str = ""
    custom_rules: list[str] = field(default_factory=list)

    # ---- Public Methods ----

    def add_rules(self, rules: list[str]) -> "PromptBuilder":
        """Thêm custom coding rules."""
        self.custom_rules.extend(rules)
        return self

    def add_language(self, language: str) -> "PromptBuilder":
        """Set ngôn ngữ lập trình."""
        self.language = language.lower()
        return self

    def build(self) -> str:
        """Build prompt hoàn chỉnh."""
        sections = [
            self._build_system_instruction(),
            self._build_code_section(),
            self._build_rules_section(),
            self._build_output_format(),
        ]
        return "\n\n".join(sections)

    # ---- Private Helpers ----

    def _build_system_instruction(self) -> str:
        return (
            "You are a senior code reviewer. "
            "Analyze the following source code and provide a detailed review.\n"
            "Focus on: code quality, potential bugs, security vulnerabilities, "
            "performance issues, and adherence to coding standards.\n"
            "Be constructive and provide specific suggestions for improvement."
        )

    def _build_code_section(self) -> str:
        header = "## Source Code"
        if self.file_name:
            header += f" ({self.file_name})"
        if self.language and self.language != "general":
            header += f" [Language: {self.language}]"

        return f"{header}\n\n```{self.language}\n{self.source_code}\n```"

    def _build_rules_section(self) -> str:
        # Merge default rules cho ngôn ngữ + custom rules
        lang_rules = DEFAULT_RULES.get(self.language, [])
        general_rules = DEFAULT_RULES.get("general", [])
        all_rules = general_rules + lang_rules + self.custom_rules

        if not all_rules:
            return ""

        rules_text = "\n".join(f"- {rule}" for rule in all_rules)
        return f"## Coding Rules to Check Against\n\n{rules_text}"

    def _build_output_format(self) -> str:
        return (
            "## Expected Output Format\n\n"
            "Please respond in the following JSON format:\n"
            "```json\n"
            "{\n"
            '  "summary": "Overall assessment of the code (2-3 sentences)",\n'
            '  "rating": <1-5 integer>,\n'
            '  "issues": [\n'
            "    {\n"
            '      "severity": "critical|major|minor|suggestion",\n'
            '      "line": <line_number or null>,\n'
            '      "title": "Brief issue title",\n'
            '      "description": "Detailed explanation",\n'
            '      "suggestion": "How to fix it"\n'
            "    }\n"
            "  ],\n"
            '  "strengths": ["Good thing 1", "Good thing 2"]\n'
            "}\n"
            "```\n"
            "IMPORTANT: Respond ONLY with valid JSON, no additional text."
        )