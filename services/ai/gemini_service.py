import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


class GeminiService:

    def ask(self, message: str):

        for _ in range(3):

            try:

                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=message,
                )

                return response.text

            except Exception as e:

                if "503" in str(e):
                    time.sleep(2)
                    continue

                raise e

        raise Exception("Gemini is currently unavailable.")


gemini_service = GeminiService()