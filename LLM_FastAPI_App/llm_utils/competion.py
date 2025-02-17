from utils import *

def generate(query,model_name):
    llm,embeddings = load_model(model_name)
    
    output = llm.invoke(query)
    if llm is not None:
        return output.content
    else:
        return "Please select a model to chat"