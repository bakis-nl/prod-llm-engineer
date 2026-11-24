from groq import AsyncGroq, APITimeoutError
from .provider import ModelTimeoutError

class APIClient:
    def __init__(self, sdk: AsyncGroq):
        self.sdk = sdk

    async def complete(self, *, model: str, prompt: str) -> str:
        try:
            completion = await self.sdk.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
        except APITimeoutError as exc:
            raise ModelTimeoutError("Model API timed out") from exc

        if not completion.choices:
            raise RuntimeError("Groq returned no choices")

        text = completion.choices[0].message.content
        if text is None:
            raise RuntimeError("Groq returned no text")

        return text