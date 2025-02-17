from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils import *

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_store = InMemoryVectorStore(embeddings)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
    )


#Create the chunks from the document
def create_chunks(doc_path):
    # loaded_docs = read_document(doc_path)
    loaded_docs = extract_text_all_formats(doc_path)
    split_chunks = text_splitter.split_documents(loaded_docs)
    return split_chunks
 
#Return the vector store with populated chunks
def create_vector_store(doc_path):
    split_chunks = create_chunks(doc_path)
    vector_store.add_documents(split_chunks)
    return vector_store

