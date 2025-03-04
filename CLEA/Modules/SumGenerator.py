from langchain_openai import ChatOpenAI
import json
from CLEA import utils
from CLEA.BaseModules.agent_general import GenralAgent

class SumGenerator(GenralAgent):
        
    def get_summary(
        self,
        params : str
    ) -> str:
        '''
        Create sub-graph for each iterations
        '''
        summary = self.create_completion(params)
        return summary