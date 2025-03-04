from langchain_openai import ChatOpenAI
import yaml
from CLEA.utils import ModelConfig, image_to_base64
from typing import (
    List,
    Dict,
    Tuple,
    Optional,
    Any,
    Literal
)
from functools import partial

from CLEA.utils import decode_md
SEED = 1024


'''
Image input
'''

import re
from CLEA.utils import extract_tag_content


    
def replace_match(
        match: re.Match, 
        params: Dict[str, str]
    ) -> str:
    
    param_name = match.group(1) 
    if param_name in params:
        return str(params[param_name])  
    else:
        return "None" 
    

def template_preprocess(template: str, params: Dict[str, str]) -> str:
    
   
    pattern = re.compile(r'\{\{(\w+)\}\}')
    segments = []
    last_end = 0
    
    for match_pattern in pattern.finditer(template):
        
        replacement = replace_match(match_pattern, params)

      
        if replacement != "None":
            segments.append(template[last_end:match_pattern.end()])
        else:
            pass

        last_end = match_pattern.end()


    result = ''.join(segments)
    return result 

def render_template(template: str, params: Dict[str, str]) -> str:
    
    processed_template = template_preprocess(template, params)
    pattern = re.compile(r'\{\{(\w+)\}\}')


    replacement_function = partial(replace_match, params=params) 


    result = pattern.sub(replacement_function, processed_template)

    return result

class GenralAgent:
    
    def __init__(
            self,
            model_config : ModelConfig,
            template_path : str,
        ) -> None:
            with open(template_path, "r")as fp:
                self.template = fp.read()
            
            self.client = ChatOpenAI(
                api_key = model_config.api_key,
                model = model_config.model,
                base_url = model_config.base_url,
                temperature = model_config.temperature,
                top_p = model_config.top_p,
                max_tokens = model_config.max_tokens,
                seed = model_config.seed
            )
            

    def create_completion(
        self,
        params : Dict[str, Any] = None,
        image_paths : List = None,
        base64_image : bool = True,
        image_type : Literal["jpeg", "png", "webp", "gif"] = "jpeg"
    ) -> Tuple:
        """
        Create a completion from messages in text (and potentially also encoded images).
        - If image path is None, then it is a LLM mode Agent
        - If you provide image_path, then it is a VLM mode Agent
        - base64_image is True then the image_path is just the base64 string
        - base64_image is False then the image_path must be a valid path toward were the image save
        """
        prompt = self.assemble_prompt(params, image_paths, base64_image, image_type)
        return self.client.invoke(prompt).content
    
    def assemble_prompt(
            self, 
            params: Dict[str, Any] = None,
            image_paths : List = None,
            base64_image : bool = True,
            image_type : Literal["jpeg", "png", "webp", "gif"] = "jpeg"
        ) -> List[Dict[str, Any]]:
        '''
        fill in the prompt
        - image_paths: a list of image path that need to provide to the VLM
        '''
        if image_paths == None:
            system_prompt = extract_tag_content(self.template, "system")
            user_prompt_template = extract_tag_content(self.template, "user")

            user_prompt = render_template(user_prompt_template, params)
            
            input_info = [
                {
                    "role" : "system",
                    "content" : system_prompt
                },
                {
                    "role" : "user",
                    "content" : user_prompt
                }
            ]
            
        else:
            system_prompt = extract_tag_content(self.template, "system")
            user_prompt_template = extract_tag_content(self.template, "user")

            user_prompt = render_template(user_prompt_template, params)
            
            if not base64_image:
                images = [image_to_base64(image_path) for image_path in image_paths] # read images
            else:
                images = image_paths # directly load if path is just base64 string
            
            input_info = [
                {
                    "role" : "system",
                    "content" : system_prompt
                },
                {
                    "role" : "user",
                    "content" : [
                        {"type" : "text", "text" : user_prompt},
                    ]
                }
            ]
            
            # add images
            for image in images:
                image_formatted = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{image_type};base64,{image}"
                    }
                }
                input_info[-1]["content"].append(image_formatted)  
                
        return input_info

    
    
            
            
       