import httpx

from common.exceptions import BadRequestException
from modules.ai.providers.base import BaseAIProvider


class GeminiProvider(BaseAIProvider):

    BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'


    def __init__(self, api_key: str, model: str = "gemini-3.6-flash"):
        self.api_key = api_key
        self.model = model

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate(self, prompt: str) -> str:
        url = f"{self.BASE_URL}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4096,
            },
        }
        async with httpx.AsyncClient(timeout=120) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]

            except httpx.HTTPStatusError as e:
                raise BadRequestException(
                    message=f"Gemini API error: {e.response.status_code} - {e.response.text}",
                    error_code="AI_PROVIDER_ERROR",
                )
            except (httpx.RequestError, KeyError, IndexError) as e:
                raise BadRequestException(
                    message=f"Failed to connect to Gemini: {str(e)}",
                    error_code="AI_CONNECTION_ERROR",
                )