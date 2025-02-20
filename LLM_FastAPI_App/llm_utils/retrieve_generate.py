from langchain_core.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from utils import *

RAG_PROMPT = PromptTemplate.from_template("""You are an assistant for question-answering tasks. Use the following piecesofretrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise. You are also provided with additional contexts regarding the user's question
Question: {question} 
Context: {context}
Additional_context :{chat_history} 
Answer:
""")


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)


# Create the chunks from the document
def create_chunks(doc_path):
    # loaded_docs = read_document(doc_path)
    loaded_docs = extract_text_all_formats(doc_path)
    split_chunks = text_splitter.split_documents(loaded_docs)
    return split_chunks


# Return the vector store with populated chunks
def create_vector_store(doc_path, embeddings):
    vector_store = InMemoryVectorStore(embeddings)
    split_chunks = create_chunks(doc_path)
    vector_store.add_documents(split_chunks)
    return vector_store


def get_retrieved_content(doc_path,query,embeddings):
    vector_store = create_vector_store(doc_path,embeddings)
    retrieved_docs = vector_store.similarity_search(query)
    document_content = "\n\n".join(i.page_content for i in retrieved_docs)
    return document_content



def ask_llm(query,history,doc_path,model_name):
    llm,embeddings = load_model(model_name)
    document_content = get_retrieved_content(doc_path,query,embeddings)
    rag_chain = RAG_PROMPT|llm|StrOutputParser()
    output = rag_chain.invoke({"question":query,
                               "context":document_content,
                               'chat_history':history})
    if llm is not None:
        return output
    else:
        return "Please select a model to chat"