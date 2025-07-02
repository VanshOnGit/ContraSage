from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import sys
import os

sys.path.append(os.path.abspath("."))

from rag.doc_loader import load_documents, split_documents

# GLOBAL CACHE
_cached_vectorstore = None

def create_vectorstore():
    global _cached_vectorstore
    if _cached_vectorstore is not None:
        return _cached_vectorstore

    docs = load_documents("./data")
    chunks = split_documents(docs)

    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embedding_model)
    
    _cached_vectorstore = vectorstore
    return vectorstore

def get_relevant_context(query: str, k: int = 5) -> str:
    vectorstore = create_vectorstore()
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": k})
    docs = retriever.invoke(query)
    return "\n".join([doc.page_content for doc in docs])

def retrieve(query, k=3):
    vectorstore = create_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return [r.page_content for r in results]

if __name__ == "__main__":
    query = "Are employees allowed to work from home?"
    results = retrieve(query)
    print("\nTop matching chunks:\n")
    for r in results:
        print("-", r)
