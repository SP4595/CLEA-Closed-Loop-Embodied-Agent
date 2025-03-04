import re
from langchain_openai.embeddings import OpenAIEmbeddings
import os
import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objs as go
from plotly.offline import plot
import base64

# Set work dir to root
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
os.chdir(parent_path)

SEED = 1024


def image_to_base64(image_path):
    '''
    Read image to base64 format
    '''
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_tag_content(text: str, label: str) -> str:
    

    pattern = rf'<{label}>\n?(.*?)\n?</{label}>'
    

    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        content = match.group(1)
 
        content = content.lstrip('\n').rstrip('\n')
        return content
    else:
        return ''

def yaml_decoder(output : str) -> tuple:
        '''
        decode output of critic
        '''
        return decode_md(output, "YAML")[-1]

def decode_md(
        output : str,
        code_type : str
    ) -> list[str]:
        '''
        ### Usage:
        This function is to decode markdown code format: eg: ```json  ``` 
        '''
        # Define a regex pattern to extract code blocks of a specific type
        pattern = rf'```(?:{code_type}\s*)?(.*?)\s*```'
        
        # Find all matches in the text
        matches = re.findall(pattern, output, re.DOTALL| re.IGNORECASE)
        
        # Return a list of all code blocks of the specified type
        return matches

def extract_all_code_blocks(text : str) -> list[str]:
    # Pattern to match text surrounded by triple backticks
    pattern = r'```(.*?)```'
    
    # Extract all non-overlapping matches of the pattern
    code_blocks = re.findall(pattern, text, flags=re.DOTALL)
    
    return code_blocks

def normalize_string(string : str) -> str:
    '''
    String to normalized format
    '''
    return string.strip().lower()

class ModelConfig:
    def __init__(
        self,
        model : str,
        base_url : str,
        temperature=0.1,
        top_p=0.7,
        max_tokens = 1024,
        seed = SEED,
        api_key : str = " "
    ) -> None:
        '''
        config settings for model
        '''
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.seed = seed
    
