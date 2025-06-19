from rag.exceptions import VectorstoreInitError, DocumentProcessingError, VectorstoreError
from rag.pipeline import load_documents, split_docs
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from typing import Iterable
from rag.embeddings.embeddings_store import get_embedding_model
import shutil, os

class VectorstoreOperator:
    """
    Handles CRUD operations for the vectorstore.
    """
    def __init__(self, vectorstore: Chroma, persist_directory: str = "chroma_db"):
        self.vectorstore = vectorstore
        self.persist_directory = persist_directory

    def _split_and_add_docs(self, docs: Iterable[Document], metadata: dict = None):
        try:
            chunks = split_docs(docs, metadata=metadata or {})
            self.vectorstore.add_documents(chunks)
        except Exception as e:
            raise DocumentProcessingError(f"Failed to split and add docs. {e}")

    def add_pdf(self, file_path: str, metadata: dict = None):
        try:
            docs = load_documents(file_path)
            self._split_and_add_docs_to_vectorstore(docs, metadata)
        except Exception as e:
            raise DocumentProcessingError(f"Failed to process and insert documents: {e}")

    def add_content(self, content: str, metadata: dict = None):
        try:
            doc = Document(page_content=content, metadata=metadata)
            self._split_and_add_docs_to_vectorstore([doc], metadata)
        except Exception as e:
            raise DocumentProcessingError(f"Failed to process and insert documents: {e}")

    def delete_doc(self, filter: dict):
        try:
            chroma_collection = self.vectorstore._collection
            chroma_collection.delete(where=filter)
        except Exception as e:
            raise VectorstoreError(f"Error deleting file from vectorstore: {str(e)}")
        
####################################################################################################

def rebuild_vectorstore(docs, vectorstore: Chroma, persist_directory="chroma_db"):
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embedding_model = get_embedding_model(EMBEDDING_PROVIDER, EMBEDDING_MODEL)

    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        return Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

    vectorstore = Chroma.from_documents(docs, embedding=embedding_model, persist_directory=persist_directory)
    return vectorstore

def clear_db(persist_directory="chroma_db"):
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print("ChromaDB has been cleared")
    else:
        print("ChromaDB directory does not exist")
