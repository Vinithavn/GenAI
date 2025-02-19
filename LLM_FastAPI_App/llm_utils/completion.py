from utils import *

def generate(chat_history,query,model_name):
    llm,embeddings = load_model(model_name)
    if chat_history:
        output = llm.invoke(f"query:{query}, history:{chat_history}")
    else:
        output = llm.invoke(query)
    if llm is not None:
        return output.content
    else:
        return "Please select a model to chat"