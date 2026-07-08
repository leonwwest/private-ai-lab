from __future__ import annotations

import httpx

from app.config import Settings

SYSTEM_PROMPT = (
    "Du bist ein interner Private-AI-Assistent. Antworte nur auf Basis des "
    "bereitgestellten Kontexts. Wenn der Kontext nicht reicht, sage klar, "
    "welche Information fehlt. Nenne relevante Quellen kurz am Ende."
)


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.llm_base_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.timeout_seconds = settings.llm_timeout_seconds

    async def answer(self, question: str, context_blocks: list[str]) -> str:
        if not context_blocks:
            return (
                "Ich habe keine passenden Dokumentstellen gefunden. "
                "Bitte lade zuerst relevante PDFs hoch oder formuliere die Frage genauer."
            )

        if self.base_url.lower() == "mock":
            return (
                "Testmodus: Ich wuerde die Frage anhand der gefundenen "
                f"{len(context_blocks)} Kontextstellen beantworten."
            )

        context = "\n\n".join(context_blocks)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Kontext:\n"
                    f"{context}\n\n"
                    f"Frage: {question}\n\n"
                    "Antworte praezise und mit Quellenhinweisen."
                ),
            },
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]
