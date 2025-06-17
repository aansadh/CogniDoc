from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from rag.embeddings.embeddings_store import get_embedding_model
import os
import httpx
import requests
import shutil
from rag.exceptions import ContextNotFoundError, QueryProcessingError, EnvironmentError

def load_documents(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} doesn't exist.")
    loader = PyMuPDFLoader(file_path)
    return loader.load()


def split_docs(documents, metadata: dict = None):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = []
    for doc in documents:
        doc_chunks = splitter.split_documents([doc])
        for chunk in doc_chunks:
            chunk.metadata.update(doc.metadata) 
            if metadata:
                chunk.metadata.update(metadata) 
            chunks.append(chunk)
    return chunks


def rebuild_vectorstore(docs, persist_directory="chroma_db"):
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embedding_model = get_embedding_model(EMBEDDING_PROVIDER, EMBEDDING_MODEL)

    if(os.path.exists(persist_directory) and os.listdir(persist_directory)):
        return Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

    vectorstore = Chroma.from_documents(docs, embedding=embedding_model, persist_directory=persist_directory)
    return vectorstore


def get_relevant_chunks(vectorstore, query, filter=None, relevance_threshold=0.3):
    relevant_chunks = vectorstore.similarity_search_with_relevance_scores(query, k=3, filter=filter)
    if(len(relevant_chunks) == 0 or relevant_chunks[0][1] < relevance_threshold):
        raise ContextNotFoundError("No relevant documents found for the query!")
    
    return relevant_chunks 


def get_context(vectorstore, query, filter=None):
    relevant_chunks = get_relevant_chunks(vectorstore, query, filter)
    context = ""
    sources = []

    for doc, _ in relevant_chunks:
        page = doc.metadata.get("page", "N/A")
        source = doc.metadata.get("file_name", "Unknown")
        sources.append(f"{source} (page {page})")
        context += f"{doc.page_content}\n\n"

    return {
        "context": context.strip(),
        "sources": sources
    }


def ask_query(context: str, query: str, url: str = None):
    API_URL = url or os.getenv("API_URL")
    if not API_URL:
        raise EnvironmentError("API URL is missing. Set the API_URL environment variable.")

    API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    if not API_KEY:
        raise EnvironmentError("Hugging Face API key is missing. Set HUGGINGFACE_API_KEY environment variable.")

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    prompt = f"""
                You are an intelligent assistant. Your task is to answer the user's question based ONLY on the provided context.
                If the answer is not found in the context, clearly state that you don't have enough information.
                Avoid making up answers or using external knowledge.

                Context:
                {context}

                Question:
                {query}

                Answer:
            """

    payload = {
        "messages": [
            # {"role": "system", "content": ""},
            {"role": "user", "content": prompt.strip()}
        ],
        "model": "microsoft/phi-4"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        return result['choices'][0]['message']
    except requests.HTTPError as e:
        raise QueryProcessingError(f"Model API error: {e.response.status_code} - {e.response.text}")
    except requests.RequestException as e:
        raise QueryProcessingError(f"Request to model API failed: {str(e)}")
    except Exception as e:
        raise QueryProcessingError(f"Unexpected error during query: {str(e)}")
    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(API_URL, headers=headers, json=payload)
    #         response.raise_for_status()
    #         result = response.json()
    #         return result["choices"][0]["message"]

    # except httpx.HTTPStatusError as e:
    #     raise QueryProcessingError(f"Model API error: {e.response.status_code} - {e.response.text}")

    # except httpx.RequestError as e:
    #     raise QueryProcessingError(f"Request to model API failed: {str(e)}")

    # except Exception as e:
    #     raise QueryProcessingError(f"Unexpected error during query: {str(e)}")


def clear_db(persist_directory="chroma_db"):
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print("ChromaDB has been cleared")
    else:
        print("ChromaDB directory does not exist")


def process_query(query: str, filter: dict, vectorstore: Chroma = None):
    context = get_context(vectorstore, query, filter=filter)
    
    results = ask_query(context['context'], query)

    return {
        "response": results['content'],
        "sources": list(set(context["sources"])),
    }
