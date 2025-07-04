import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_documents(folder_path):
    documents = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        elif filename.endswith(".md"):
            loader = TextLoader(file_path)
            loaded = loader.load()
            for doc in loaded:
                doc.metadata["source"] = filename
            documents.extend(loaded)
        elif filename.endswith(".txt"):
            loader = TextLoader(file_path)
            loaded = loader.load()
            for doc in loaded:
                doc.metadata["source"] = filename
            documents.extend(loaded)

    return documents

def split_documents(documents, chunk_size=500, chunk_overlap=50):
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(documents)

    for chunk in chunks:
        if 'source' in chunk.metadata:
            filename = os.path.basename(chunk.metadata['source'])
            chunk.page_content = f"{chunk.page_content.strip()} ({filename})"

    return chunks

if __name__ == "__main__":
    docs = load_documents("./data")
    chunks = split_documents(docs)

    print(f"Loaded {len(docs)} documents.")
    print(f"Generated {len(chunks)} chunks.")
