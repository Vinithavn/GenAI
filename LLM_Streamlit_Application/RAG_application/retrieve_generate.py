from RAG_application.indexing import * 
from langchain_core.prompts import PromptTemplate
from langchain.schema import StrOutputParser

RAG_PROMPT = PromptTemplate.from_template("""You are an assistant for question-answering tasks. Use the following piecesofretrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
""") 


def get_retrieved_content(doc_path,query):
    vector_store = create_vector_store(doc_path)
    retrieved_docs = vector_store.similarity_search(query)
    document_content = "\n\n".join(i.page_content for i in retrieved_docs)
    return document_content




def ask_llm(doc_path,user_query,model_name):
    document_content = get_retrieved_content(doc_path,user_query)
    llm = load_model(model_name)
    rag_chain = RAG_PROMPT|llm|StrOutputParser()
    output = rag_chain.invoke({"question":user_query,
                      "context":document_content})
    if llm is not None:
        return output
    else:
        return "Please select a model to chat"