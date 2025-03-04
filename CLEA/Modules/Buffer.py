from typing import Literal, Union, Any
import json
from langchain_openai import ChatOpenAI
from CLEA.utils import decode_md, ModelConfig
from CLEA.Modules.SumGenerator import SumGenerator


class HistoryRecord():
    '''
    Record a History Movement in one iteration
    '''
    def __init__(
        self,
        Observation : str = "",
        Movement : str = "",
        Feedback : str = ""
    ) -> None:
        

        self.Feedback = Feedback # what is the feedback of your movement?
        self.Movement = Movement # your action
        self.Observation = Observation # What did you see (provied on last iteration)
        
    def create_single_record(self) -> str:
        '''
        ### Construction single record summary data
        This is to print single record with:
        User instruction
        Environment (Observation from the environment)
        Movement
        Feed back
        '''
        return_str = ""
        if self.Observation != "":
            return_str += f"Environment Observation:\n{self.Observation}\n"
        if self.Movement != "":
            return_str += f"Movement:\n{self.Movement}\n"
        if self.Movement != "":
            return_str += f"Environment Feed back:\n{self.Feedback}\n"
        return return_str
                
    def create_records(self) -> str:
        '''
        Print the record in certain format
        '''
        return_str = ""
        return_str += "\n" # for better visualization
        if self.Observation != "":
            return_str += f"Environment:\n{self.Observation}\n"
        if self.Movement != "":
            return_str += f"Movement:\n{self.Movement}\n" 
        if self.Feedback != "":
            return_str += f"FeedBack:\n{self.Feedback}\n"     
        return_str += "\n"
        
        return return_str


class HistoryBuffer:
    '''
    ## History Buffer
    - History Buffer is a buffer to store historical status.
    - It will store the outcome of executor every clock cycle
    - History status will provide to executer as well
    - HistoryBuffer will only store the whole task
    - This buffer well contain a LLM for summarizer (just a small model)
    '''

    def __init__(
        self,
        summarizer : SumGenerator,
        max_records : int = 25 # max length of record
    ) -> None:
        '''
        ### Note:
        The lenth of history_list:
        1. env and action should be same
        2. dialog can be longer or shorter!!!!
        3. We use Chat model instead of OpenAI model
        use_outer_sum: Each iteration need a outer summary, do not use inner summarizer
        '''
        self.task_description : str = "" # get from planner
        self.start_time : str = ""
        self.history_list : list[HistoryRecord] = [] # old -> new
        self.is_empty : bool = True
        self.max_records = max_records
        
        self.summarizer = summarizer
        self.HistorySummary : str = "" 
  
    def peek_last_record(
        self
    ) -> HistoryRecord:
        '''
        ### Usage
        This function is to get the newest HistoryRecord object of the List
        '''
        return self.history_list[-1]
        
    def insert_history(
        self,
        record_info_dict : dict,
    ) -> None:
        '''
        ### Usage
        Insert output to history
        Insert to the top (index = 0) as we need to extract top n records
        
        ### params
        record_info_dict :
        { 
            "observation" : feedback from last iteration,
            "action": Action,
            "feed_back" : feedback of this iteration
        }
        '''
        if self.is_empty:
            self.is_empty = False
        
        record = HistoryRecord(
            Observation=record_info_dict["observation"],
            Movement=record_info_dict["action"],
            Feedback=record_info_dict["feed_back"],
        )
        
        self.history_list.append(record)
        if len(self.history_list) > self.max_records:
            self.history_list.pop(0)
            print(f"Warning: Max record nums {self.max_records} reached, drop last record.")
        
        self.summarize_History()
    
    def get_history(self) -> str:
        '''
        ## Main api for getting the history
        ## We well summarize when a new record came in, so not need to worry about summarizing anymore! just call it!
        '''
        return self.HistorySummary
            
    
    @staticmethod 
    def clip_top_n(
        top_n : int,
        length : int
    ) -> int:
        '''
        clip the top_n to valid region
        '''
        return top_n if top_n > 0 and top_n <= length else length
    
    def get_trajectory(self) -> str:
        '''
        get all history in the history list
        '''
        return_str = ""
        length = len(self.history_list)
        for i in range(length): # [0, len - top_n) <-> [len - top_n, len)
            record = self.history_list[i] # get the last top_n one
            if i == (length - 1):
                return_str += record.create_records()
            else: 
                return_str += record.create_records()
        
        return return_str
    
    def get_previous_history(self) -> str:
        '''
        ### Usage
        Output the whole history except top_n history (i.e., all history that will not be displayed)
        '''
        
        return_str = ""
        length = len(self.history_list)
        mem_top_n = self.clip_top_n(self.max_records, length)
        for i in range(length - mem_top_n): # [0, len - top_n) <-> [len - top_n, len)
            record = self.history_list[i] # get the last top_n one
            if i == (length - mem_top_n - 1):
                return_str += record.create_records()
            else: 
                return_str += record.create_records()
        
        return return_str
    
    def summarize_History(self) -> str:
        '''
        ### Usage:
        use LLM to summerize previous movement
        '''
        params = {
            "trajectory" : self.get_trajectory()
        }
        self.HistorySummary = self.summarizer.get_summary(params)
        return self.HistorySummary


if __name__ == "__main__":
    Observation = """-= Kitchen =-
You've just shown up in a kitchen.

You make out a closed fridge in the corner. You can see a closed conventional looking oven in the corner. You scan the room, seeing a table. The table is massive. But the thing hasn't got anything on it. What, you think everything in TextWorld should have stuff on it? You make out a counter. The counter is vast. On the counter you can see a cookbook and a knife. There's something strange about this being here, but you can't put your finger on it. You see a stove. However, the stove, like an empty stove, has nothing on it.

There is an open screen door leading north. There is a closed frosted-glass door leading west. There is an exit to the east. There is an exit to the south."""
    Movement = "open fridge"
    FeedBack = "You open the fridge, revealing a raw chicken leg and a raw chicken wing."
    record = HistoryRecord(
        Observation = Observation,
        Movement = Movement,
        Feedback = FeedBack
    )
    print(record.create_single_record())