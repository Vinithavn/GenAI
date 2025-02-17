import langchain
from langchain.schema import StrOutputParser
from pydantic import BaseModel
from fastapi import Query
from typing import Optional
from langchain.schema.prompt_template import format_document
from utils import *

summarizer_prompt = '''
Please provide a concise summary for the below context\n\n
Context:{context}
'''

class SummarizerRequest(BaseModel):
    model_name:str= Query('Gemini', enum=['Gemini', 'Lllama 3.2'])
    context:Optional[str]


def summarize_text(context,model_name):
    llm,_ = load_model(model_name)
    llm_prompt = langchain.PromptTemplate.from_template(summarizer_prompt)
    summarizer_chain = llm_prompt|llm|StrOutputParser()
    output = summarizer_chain.invoke({"context":context})
    return output


def summarize_document(doc_path,model_name):
    print(doc_path)
    document_content = extract_text_all_formats(doc_path)
    doc_prompt = langchain.PromptTemplate.from_template("{page_content}")
    llm,_ = load_model(model_name)
    
    llm_prompt = langchain.PromptTemplate.from_template(summarizer_prompt)
    
    stuff_chain = (
        {
        "context": lambda docs: "\n\n".join(
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
