from rag.exceptions import VectorstoreInitError, DocumentProcessingError, VectorstoreError
from rag.pipeline import load_documents, split_docs
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from typing import Iterable

def split_and_add_docs_to_vectorstore(docs: Iterable[Document], vectorstore: Chroma = None, metadata: dict = None):
    if not vectorstore:
        raise VectorstoreInitError("Vectorstore instance is missing.")
    try:
        chunks = split_docs(docs, metadata=metadata or {})
        vectorstore.add_documents(chunks)
    except Exception as e:
        raise DocumentProcessingError(f"Failed to split and add docs. {e}")
        

def add_pdf_to_vectorstore(file_path: str, vectorstore: Chroma = None, metadata: dict = None):
    try:
        docs = load_documents(file_path)
        split_and_add_docs_to_vectorstore(docs, vectorstore, metadata)
    except Exception as e:
          raise DocumentProcessingError(f"Failed to process and insert documents: {e}")
    

def add_content_to_vectorstore(content: str, vectorstore: Chroma = None, metadata: dict = None):
    try:
        # string to docs
        doc = Document(page_content=content, metadata=metadata)
        split_and_add_docs_to_vectorstore([doc], vectorstore, metadata)
    except Exception as e:
        raise DocumentProcessingError(f"Failed to process and insert documents: {e}")


def delete_doc_from_vectorstore(filter: dict, vectorstore: Chroma = None):
    if not vectorstore:
        raise VectorstoreInitError("Vectorstore instance is missing.")
    
    if not filter or not isinstance(filter, dict):
        raise ValueError("Filters must be non-empty dictionary.")

    try:
        chroma_collection = vectorstore._collection
        chroma_collection.delete(where=filter)

    except Exception as e:
        raise VectorstoreError(f"Error deleting file from vectorstore: {str(e)}")