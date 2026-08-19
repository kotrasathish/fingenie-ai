import os
import time

from dotenv import load_dotenv
from google import genai

from services.ai.prompt_service import SYSTEM_PROMPT

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class GeminiService:

    def ask(self, messages):

        prompt = SYSTEM_PROMPT + "\n\n"

        for msg in messages:

            prompt += f"{msg.role}: {msg.message}\n"

        for _ in range(3):

            try:

                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=prompt,
                )

                return response.text

            except Exception as e:

                if "503" in str(e):
                    time.sleep(2)
                    continue

                raise e

        raise Exception("Gemini is currently unavailable.")


gemini_service = GeminiService()