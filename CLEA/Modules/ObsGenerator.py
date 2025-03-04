from langchain_openai import ChatOpenAI
import json
from CLEA import utils
from CLEA.BaseModules.agent_general import GenralAgent
from typing import (
    List,
    Dict,
    Tuple,
    Optional,
    Any,
    Literal
)

class ObsGenerator(GenralAgent):
        
    def get_obs_description(
            self, 
            params : Dict[str, Any] = None,
            image_paths : List = None,
            base64_image : bool = True,
            image_type : Literal["jpeg", "png", "webp", "gif"] = "jpeg"
        ) -> dict:
        '''
        Create sub-graph for each iterations
        '''
        obs = self.create_completion(params, image_paths, base64_image, image_type)
        return obs