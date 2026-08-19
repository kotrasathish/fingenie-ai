import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    APP_NAME = "FinGenie AI"

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "qwen/qwen3.6-27b"
    )

    EMBEDDING_MODEL = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    VECTORSTORE_DIR = os.getenv(
        "VECTORSTORE_DIR",
        "vectorstore"
    )

    RAG_TOP_K = int(
        os.getenv(
            "RAG_TOP_K",
            "4"
        )
    )

    RAG_SIMILARITY_THRESHOLD = float(
        os.getenv(
            "RAG_SIMILARITY_THRESHOLD",
            "1.20"
        )
    )


settings = Settings()