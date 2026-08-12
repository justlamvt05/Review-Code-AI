from abc import ABC, abstractmethod

from core.config import settings


class BaseAIProvider(ABC):

    @abstractmethod
    async def generate(self, prompt: str) -> str:

        """
        Gửi prompt đến AI và nhận raw response string.

        Args:
            prompt: Prompt đã build xong từ PromptBuilder.

        Returns:
            Raw text response từ AI model.

        Raises:
            AIProviderException: Khi gọi API thất bại.
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Tên provider (ví dụ: 'openai', 'gemini', 'claude')."""
        ...
def create_ai_provider(provider_name: str | None = None) -> BaseAIProvider:
    """
    Factory: tạo AI provider dựa trên config.

    Args:
        provider_name: Override provider. Nếu None, dùng settings.ai_provider.

    Returns:
        Instance của BaseAIProvider tương ứng.
    """
    name = (provider_name or settings.ai_provider).lower()

    match name:
        # case "openai":
        #     if not settings.openai_api_key:
        #         raise ValueError("OPENAI_API_KEY is not configured")
        #     return OpenAIProvider(
        #         api_key=settings.openai_api_key,
        #         model=settings.openai_model,
        #     )
        case "gemini":
            from modules.ai.providers.gemini_provider import GeminiProvider
            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is not configured")
            return GeminiProvider(
                api_key=settings.gemini_api_key,
                model=settings.gemini_model,
            )
        # case "claude":
        #     if not settings.claude_api_key:
        #         raise ValueError("CLAUDE_API_KEY is not configured")
        #     return ClaudeProvider(
        #         api_key=settings.claude_api_key,
        #         model=settings.claude_model,
        #     )
        case _:
            raise ValueError(f"Unknown AI provider: {name}")