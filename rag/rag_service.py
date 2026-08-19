from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config.settings import settings


VECTORSTORE_DIR = Path(
    settings.VECTORSTORE_DIR
)


class RAGService:

    def __init__(self):

        self.embeddings = HuggingFaceEmbeddings(

            model_name=settings.EMBEDDING_MODEL

        )

        self.vectorstore = None

        self.similarity_threshold = (
            settings.RAG_SIMILARITY_THRESHOLD
        )

    def load_vectorstore(self):

        if not VECTORSTORE_DIR.exists():

            raise FileNotFoundError(

                "Vector database not found. "
                "Run: python -m rag.ingest"

            )

        self.vectorstore = FAISS.load_local(

            str(VECTORSTORE_DIR),

            self.embeddings,

            allow_dangerous_deserialization=True

        )

    def search(
        self,
        query,
        k=None
    ):

        if self.vectorstore is None:

            self.load_vectorstore()

        if k is None:

            k = settings.RAG_TOP_K

        return self.vectorstore.similarity_search_with_score(

            query,

            k=k

        )

    def get_context(
        self,
        query,
        k=None
    ):

        results = self.search(
            query,
            k
        )

        if not results:

            return {
                "context": "",
                "sources": []
            }

        context_parts = []

        sources = []

        for document, score in results:

            if score > self.similarity_threshold:

                continue

            source = document.metadata.get(
                "source",
                "Unknown"
            )

            source_name = Path(
                source
            ).name

            context_parts.append(

                f"Source: {source_name}\n"
                f"{document.page_content}"

            )

            source_data = {

                "source": source_name,

                "score": round(
                    float(score),
                    4
                )

            }

            if source_data not in sources:

                sources.append(
                    source_data
                )

        if not context_parts:

            return {
                "context": "",
                "sources": []
            }

        return {

            "context": "\n\n".join(
                context_parts
            ),

            "sources": sources

        }


rag_service = RAGService()