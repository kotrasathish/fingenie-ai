from groq import Groq

from config.settings import settings
from services.ai.prompt_service import SYSTEM_PROMPT


if not settings.GROQ_API_KEY:

    raise RuntimeError(
        "GROQ_API_KEY is missing. "
        "Add it to your .env file."
    )


client = Groq(
    api_key=settings.GROQ_API_KEY
)


class GroqService:

    def ask(
        self,
        messages,
        context=""
    ):

        conversation = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }

        ]

        # -----------------------------
        # RAG Context
        # -----------------------------

        if context:

            conversation.append({

                "role": "system",

                "content": f"""
Use the following financial knowledge
when answering the user.

CONTEXT:

{context}

Rules:

1. Prefer the supplied context when relevant.
2. Do not invent information from the context.
3. If the context does not contain the answer,
   use your general knowledge.
4. Keep the answer clear and concise.
"""

            })

        # -----------------------------
        # Messages
        # -----------------------------

        for msg in messages:

            if isinstance(msg, dict):

                role = msg.get(
                    "role",
                    "user"
                )

                content = msg.get(
                    "content",
                    ""
                )

            else:

                role = msg.role

                content = msg.message

            if role not in [
                "user",
                "assistant",
                "system"
            ]:

                role = "user"

            conversation.append({

                "role": role,

                "content": content

            })

        # -----------------------------
        # Groq
        # -----------------------------

        response = client.chat.completions.create(

            model=settings.GROQ_MODEL,

            messages=conversation,

            temperature=0.3,

            max_tokens=1000

        )

        return response.choices[0].message.content


groq_service = GroqService()