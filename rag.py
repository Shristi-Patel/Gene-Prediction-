import os
import argparse
import logging
import re
import warnings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

# Suppress Warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Embedding Function
def get_embedding_function():
    return HuggingFaceEmbeddings(model_name="./all-MiniLM-L6-v2-local")

# Populate Database
def populate_database():
    loader = TextLoader("processed_data.txt", encoding="utf-8")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    db = Chroma.from_documents(texts, get_embedding_function(), persist_directory="chroma_db")
    db.persist()
    print("Database built and persisted in chroma_db/")

# Logging Setup
logging.basicConfig(
    filename="chat_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log_interaction(question, answer):
    logging.info(f"User: {question}")
    logging.info(f"Bot: {answer}")
    logging.info("-" * 30) 

# Query Function
def query_database(question: str):
    import logging as pylogging
    pylogging.getLogger("chromadb").setLevel(pylogging.ERROR)
    pylogging.getLogger("sentence_transformers").setLevel(pylogging.ERROR)
    pylogging.getLogger("httpx").setLevel(pylogging.ERROR)

    db = Chroma(persist_directory="chroma_db", embedding_function=get_embedding_function())
    retriever = db.as_retriever(search_kwargs={"k": 5})
    results = retriever.get_relevant_documents(question)

    context_chunks = [doc.page_content for doc in results]
    context = "\n".join(context_chunks)

    prompt_template = ChatPromptTemplate.from_template("""
    You are a scientific reasoning assistant.
    Use the retrieved knowledge to answer.
    If a gene is indirectly related to a process via GO relationships, explain the reasoning step by step.
    If no relation exists, say "No evidence found".

    Question: {question}
    Context:
    {context}
    Answer:
    """)

    llm = OllamaLLM(model="llama3")
    prompt = prompt_template.format(question=question, context=context)
    response = llm.invoke(prompt)

    return response.strip()

# CLI
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--build", action="store_true", help="Build the ChromaDB database")
#     args = parser.parse_args()

#     if args.build:
#         populate_database()
#     else:
#         print("RAG-Reasoning Chatbot")
#         print("Type 'exit' to quit.")
#         while True:
#             q = input("You: ")
#             if q.lower() == "exit":
#                 break
#             answer = query_database(q)
#             print("Bot:", answer)
#             log_interaction(q, answer)

