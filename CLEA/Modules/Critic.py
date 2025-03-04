from langchain_openai import ChatOpenAI
import yaml
from CLEA import utils
from CLEA.utils import yaml_decoder
from CLEA.BaseModules.agent_general import GenralAgent
from typing import Dict, Any, List, Literal
class Critic(GenralAgent):
    '''
    critic is used to check if there is some error in execution.
    '''
            
    def get_feed_back(
            self, 
            params : Dict[str, Any] = None,
            image_paths : List = None,
            base64_image : bool = True,
            image_type : Literal["jpeg", "png", "webp", "gif"] = "jpeg"
        ) -> dict:
        '''
        params:
        {
            "goal": Actor's goal
            "history" : You have done
            "relationships" : Spatio memory
            "observation" : what you see
            "possible_actions" : possible actions
            "action": Actor's perposed action
        }
        '''
        return_str = self.create_completion(params, image_paths, base64_image, image_type)
        try:
            yaml_str = yaml_decoder(return_str)
        except:
            yaml_str = return_str 
        
        load_dict =  yaml.safe_load(yaml_str)
        
        return bool(load_dict["Action Suitability"]), load_dict["Feedback"], self.assemble_prompt(params, image_paths, base64_image, image_type),  return_str