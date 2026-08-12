import json
import re
from dataclasses import dataclass, field


@dataclass
class ReviewIssue:
    severity: str       # "critical" | "major" | "minor" | "suggestion"
    title: str
    description: str
    suggestion: str = ""
    line: int | None = None


@dataclass
class AIReviewResult:
    """Kết quả review đã parse."""
    summary: str
    rating: int
    issues: list[ReviewIssue] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    raw_response: str = ""


class ResponseParser:
    """
    Parse raw AI response thành structured AIReviewResult.
    Xử lý cả trường hợp AI trả về markdown code block hoặc plain JSON.
    """

    @staticmethod
    def parse(raw_response: str) -> AIReviewResult:
        """
        Parse raw text từ AI thành AIReviewResult.

        Args:
            raw_response: Raw string trả về từ AI provider.

        Returns:
            AIReviewResult đã structured.
        """
        json_str = ResponseParser._extract_json(raw_response)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback: nếu không parse được JSON, trả về raw text làm summary
            return AIReviewResult(
                summary=raw_response[:500],
                rating=0,
                raw_response=raw_response,
            )

        # Parse issues
        issues = []
        for item in data.get("issues", []):
            issues.append(ReviewIssue(
                severity=item.get("severity", "suggestion"),
                title=item.get("title", ""),
                description=item.get("description", ""),
                suggestion=item.get("suggestion", ""),
                line=item.get("line"),
            ))

        return AIReviewResult(
            summary=data.get("summary", ""),
            rating=data.get("rating", 0),
            issues=issues,
            strengths=data.get("strengths", []),
            raw_response=raw_response,
        )

    @staticmethod
    def _extract_json(text: str) -> str:
        """Trích xuất JSON từ response, bỏ qua markdown code block nếu có."""
        # Pattern 1: ```json ... ``` hoặc ``` ... ```
        pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Pattern 2: Response là pure JSON
        text = text.strip()
        if text.startswith("{"):
            return text

        return text