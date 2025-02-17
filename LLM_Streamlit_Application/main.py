import streamlit as st
from RAG_application.retrieve_generate import *
from Summarizer_application.summarize import *
import os
from dotenv import load_dotenv
from warnings import filterwarnings
filterwarnings("ignore")

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

st.title("Welcome to the Streamlit Application")

task = st.selectbox("Select your task",options=[
    "Summarize",
    "RAG"
    ])
    

model_name = st.selectbox("Select a model to continue",
                              options = ["Gemini","Lllama 3.2"])
output = None
if task == "RAG":
    uploaded_files = st.file_uploader("Choose a file",accept_multiple_files=True)
    if uploaded_files is not None:
        filenames = [i.name for i in uploaded_files]
        search_query = st.text_input("Chat with your LLM") 
        button = st.button("Ask LLM") 
        if button:
            output = ask_llm(filenames,search_query,model_name)
            st.write(output)
        
elif task == "Summarize": 
    uploaded_files = st.file_uploader("Choose a file",accept_multiple_files=True)
    if uploaded_files is not None:
        filenames = [i.name for i in uploaded_files]
        button = st.button("Ask LLM") 
        if button:
            output = summarize_document(filenames,model_name)
            st.write(output)


    
