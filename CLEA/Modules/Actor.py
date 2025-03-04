from langchain_openai import ChatOpenAI
import yaml
from CLEA.utils import yaml_decoder
from CLEA.BaseModules.agent_general import GenralAgent

class Actor(GenralAgent):
    '''
    Actor is to generate subgoal and movement sequence to achieve it
    '''    
    def get_plan(self, params : dict) -> tuple:
        '''
        return: subgoal, plan, prompt, returned string
        '''
        return_str = self.create_completion(params)
        try:
            yaml_str = yaml_decoder(return_str)
        except:
            yaml_str = return_str 
        
        load_dict =  yaml.safe_load(yaml_str)
        
        return load_dict["Subgoal"], list(load_dict["Action Plan"]), self.assemble_prompt(params), return_str