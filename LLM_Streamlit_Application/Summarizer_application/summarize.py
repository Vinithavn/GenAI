import langchain
from utils import *
from langchain.schema import StrOutputParser
from langchain.schema.prompt_template import format_document


SUMMARIZER_PROMPT = """Write a concise summary of the following:
    "{text}"
    CONCISE SUMMARY:"""



def summarize_document(doc_path,model_name):
    print(doc_path)
    document_content = extract_text_all_formats(doc_path)
    doc_prompt = langchain.PromptTemplate.from_template("{page_content}")
    llm = load_model(model_name)
    
    llm_prompt = langchain.PromptTemplate.from_template(SUMMARIZER_PROMPT)
    
    stuff_chain = (
        {
        "text": lambda docs: "\n\n".join(
            format_document(doc, doc_prompt) for doc in docs
            )
            }
    | llm_prompt         # Prompt for Gemini
    | llm                # Gemini function
    | StrOutputParser()  # output parser
)
    if llm is not None:
        llm_response = stuff_chain.invoke(document_content)
    else:
        llm_response = "Please select a model to chat"
    return llm_response
