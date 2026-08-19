from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


VECTORSTORE_DIR = Path("vectorstore")


class RAGService:

    def __init__(self):
        self.embeddings = None
        self.vectorstore = None

    def load_vectorstore(self):

        if self.vectorstore is not None:
            return

        if not VECTORSTORE_DIR.exists():
            raise FileNotFoundError(
                "Vector database not found. "
                "Run: python -m rag.ingest"
            )

        print("Loading embedding model...")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        print("Loading FAISS vectorstore...")

        self.vectorstore = FAISS.load_local(
            str(VECTORSTORE_DIR),
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        print("RAG vectorstore loaded.")

    def search(self, query, k=4):

        self.load_vectorstore()

        return self.vectorstore.similarity_search(
            query,
            k=k
        )

    def get_context(self, query, k=4):

        documents = self.search(query, k)

        if not documents:
            return ""

        context_parts = []

        for document in documents:

            source = document.metadata.get(
                "source",
                "Unknown"
            )

            context_parts.append(
                f"Source: {source}\n"
                f"{document.page_content}"
            )

        return "\n\n".join(context_parts)


rag_service = RAGService()