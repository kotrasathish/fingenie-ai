from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


DOCUMENTS_DIR = Path("documents")
VECTORSTORE_DIR = Path("vectorstore")


def ingest_documents():

    documents = []

    for file in DOCUMENTS_DIR.glob("*.txt"):

        print(f"Loading: {file}")

        loader = TextLoader(
            str(file),
            encoding="utf-8"
        )

        documents.extend(
            loader.load()
        )

    if not documents:

        print("No documents found.")

        return

    print(
        f"Loaded {len(documents)} documents"
    )


    # Split documents

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=500,

        chunk_overlap=100

    )

    chunks = splitter.split_documents(
        documents
    )

    print(
        f"Created {len(chunks)} chunks"
    )


    # Local embedding model

    embeddings = HuggingFaceEmbeddings(

        model_name=
        "sentence-transformers/all-MiniLM-L6-v2"

    )


    # Create FAISS database

    vectorstore = FAISS.from_documents(

        chunks,

        embeddings

    )


    # Save locally

    vectorstore.save_local(
        str(VECTORSTORE_DIR)
    )


    print(
        "FAISS vector database created successfully."
    )


if __name__ == "__main__":

    ingest_documents()