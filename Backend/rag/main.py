from rag.pipeline import load_documents, split_docs, rebuild_vectorstore, get_relevant_chunks, ask_query, clear_db
import time
from dotenv import load_dotenv

pdf_path = "data/1748527231-163198771-1984.pdf"
query = "Who is the book about?"

def main():
    load_dotenv()
    ttime = time.time()

    start = time.time()
    docs = load_documents(pdf_path)
    print(f"Time taken: {time.time() - start: .2f}")
    print("Document loaded successfully: len: ", len(docs))

    # for doc in docs[:10]:
    #     print(f"{doc}")
    #     print("<------------------------>")
    #     print("<------------------------>")
    #     print("<------------------------>")

    start = time.time()
    chunks = split_docs(docs)
    print(f"Time taken: {time.time() - start: .2f}")
    print("Broken chunks:: len: ", len(chunks))

    start = time.time()
    vectorstore = rebuild_vectorstore(chunks)
    print(f"Time taken to build vectorstore: {time.time() - start: .2f}")

    start = time.time()
    relevant_chunks = get_relevant_chunks(vectorstore, query)
    print(f"Time taken: {time.time() - start: .2f}")
    if not relevant_chunks:
        print("No relevant data found!")
        return

    context = "\n\n".join([chunk.page_content for chunk, _ in relevant_chunks])
    print(f"Context: \n{context}")

    # start = time.time()
    # results = ask_query(context, query)
    # print(results['content'])
    # print(f"End time: {time.time() - start : .2f}")


    print(f'Total time taken: {time.time() - ttime: .2f}')

if __name__ == "__main__":
    clear_db()
    # main()