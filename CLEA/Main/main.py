from CLEA.Modules.Actor import Actor
from CLEA.Modules.Critic import Critic
from CLEA.Modules.ObsGenerator import ObsGenerator
from CLEA.Modules.SumGenerator import SumGenerator
from CLEA.API.APIprocesser import APIProcesser
from CLEA.Modules.Buffer import HistoryBuffer
from CLEA.Modules.Logger import Logger
from CLEA.utils import ModelConfig
from CLEA.API.Env import BridgeEnv
from datetime import datetime
import yaml
import os

class CLEAAgent:
    def __init__(
            self,
            actor_config : ModelConfig,
            critic_config: ModelConfig,
            obsgenerator_config: ModelConfig,
            summarizer_config : ModelConfig,
            actor_path : str,
            critic_path : str,
            obsgenerator_path : str,
            summarizer_path : str,
            knowledge_path : str,
            task : str,
            interactive_objects : list[str],
            navigation_points :list[str],
            function_filter_list : list[str],
            check_point_path = "ckpt",
            base64_image : str = False,
            max_records : int = 30,
            wo_critic : bool = True
        ) -> None:
        '''
        base64_image means whether we directly pass the base64 image to VLM
        '''
        
        # setings
        
        self.base64_image = base64_image
        
        with open(knowledge_path, "r") as fp:
            self.knowledge = fp.read()
        
        # by default, the image save directory is in the checkpoint saving path
        if not os.path.exists(check_point_path):
            os.makedirs(check_point_path)
            
        # Get time
        now = datetime.now()

        # format
        time_str = now.strftime("%Y_%m_%d_%H_%M_%S")
        
        self.check_point_path = check_point_path
        
        self.now_ckpt_path = os.path.join(check_point_path, f"ckpt_{time_str}")
        
        if not self.base64_image:
            self.image_save_path = os.path.join(self.now_ckpt_path, "images")
        
        os.makedirs(self.now_ckpt_path)
        os.makedirs(self.image_save_path) # image save path
        
        self.record_path = os.path.join(self.now_ckpt_path, "records.txt") # records
        
        with open(self.record_path, 'a') as f: # a: add mode (if not exist, create it and add initialization information!)
            f.write(f"####\nRecord Task:\n{task}\n\nRecord Time:\n{time_str}\n####\n\n\n")
        
        self.actor = Actor(actor_config, actor_path)
        
        self.critic = Critic(critic_config, critic_path)
        
        self.obsgenerator = ObsGenerator(obsgenerator_config, obsgenerator_path)
        
        self.summarizer = SumGenerator(summarizer_config, summarizer_path)
        
        self.memory = HistoryBuffer(
            summarizer = self.summarizer,
            max_records = max_records
        )
        
        self.task = task
        self.interactive_objects = interactive_objects
        self.navigation_points = navigation_points
        
        self.env = BridgeEnv(
            obs_generator = self.obsgenerator,
            task = task,
            interactive_objects = interactive_objects,
            navigation_points = navigation_points,
            base64_image = self.base64_image,
            image_save_path = self.image_save_path,
        ) # environment connnect model and 
        
        self.API = APIProcesser(function_filter_list = function_filter_list) # get the API for actor & critic (filter default function)
        
        self.logger = Logger(self.record_path)
        
        self.wo_critic = wo_critic 
        
    def run(self, task : str, debug = True):
        '''
        Main function, run to get the task
        '''
        
        step = 0 # record the step
        plan_call_num = 0 # how many time do you plan
        critic_call_num = 0
        
        if debug:
            print(f"task: {task}")
        
        task, obs = self.env.reset()
        
        if debug:
            print(f"observation:\n{obs}")
        
        feedback = None
        
        record_info = {
            "observation" : obs,
            "action": "", # "" for no record
            "feed_back" : ""
        }
        
        self.memory.insert_history(record_info)
        reflection = "" # reflection from critic
        while True:
            # main loop
            
            belief = self.memory.get_history()
            
            # params for Planner
            if len(self.memory.history_list) <= 1: # No record
                params = {
                    "task": self.task,
                    "knowledge": self.knowledge,
                    "observation": self.env.obs_text,
                    "interactive_objects": self.interactive_objects,
                    "navigation_points": self.navigation_points,
                    "functions": self.API.get_api_description()
                }
            else:
                params = {
                    "task": self.task,
                    "history": belief,
                    "knowledge": self.knowledge,
                    "observation": self.env.obs_text,
                    "interactive_objects": self.interactive_objects,
                    "navigation_points": self.navigation_points,
                    "functions": self.API.get_api_description()
                }
            
            if reflection != "":
                params["reflection"] = reflection # add reflection if have it
        
            
            subgoal, plan, prompt, output = self.actor.get_plan(params)
            
            plan_call_num += 1 # record
            
            reflection = "" # renew the reflection after using it.
            
            prompt_input = prompt[-1]["content"] # for clearer record
            
            self.logger.add_agent_record(prompt_input, output, plan_call_num, role = "Planner") # record the i/o of agent
            
            for action in plan:
                
                belief= self.memory.get_history()
                
                if not self.wo_critic:
                    # with critic
                    if len(self.memory.history_list) <= 1: # wait for long record
                        # params for critic
                        params = {
                            "task": self.task,
                            "subgoal": subgoal,
                            "knowledge": self.knowledge,
                            "functions": self.API.get_api_description(),
                            "interactive_objects": self.interactive_objects,
                            "navigation_points": self.navigation_points,
                            "action": action
                        }
                    else:
                        params = {
                            "task": self.task,
                            "subgoal": subgoal,
                            "history": belief,
                            "knowledge": self.knowledge,
                            "functions": self.API.get_api_description(),
                            "interactive_objects": self.interactive_objects,
                            "navigation_points": self.navigation_points,
                            "action": action
                        }
                    
                    # critic is VLM that have visual ability itself!
                
                    is_proper, reflection, prompt, output = self.critic.get_feed_back(
                        params, 
                        image_paths = [self.env.obs_img],   
                        base64_image = self.base64_image
                    )
                    
                    critic_call_num += 1
                    
                    prompt_input = prompt[-1]["content"][0]["text"] # extract text
                    
                    
                    self.logger.add_agent_record(prompt_input, output, critic_call_num, role = "Critic") # record the i/o of agent
                    
                    if not is_proper:
                        # replan
                        break 
                
                feedback, obs = self.env.step(action, subgoal)
                
                step += 1 # record how many step you have executed
                
                self.logger.add_action_record(action, feedback, step)
                
                record_info = {
                    "observation" : obs,
                    "action": action,
                    "feed_back" : feedback
                }
                
                self.memory.insert_history(record_info)
                
                
        
        
if __name__ == "__main__":
    
    
    # W/O setings:
    
    wo_critic = False
    
    # path settings
    SETTING_PATH = "./settings.yml"
    
    with open(SETTING_PATH, "r") as f:
        settings_str = f.read()
        settings = yaml.safe_load(settings_str)
    
    PROMPT_PATH = settings["paths"]["prompt"]
    KNOWLEDGE_PATH =settings["paths"]["knowledge"]
    API_KEY = settings["API_Provider"]["api_key"]
    BASE_URL = settings["API_Provider"]["base_url"]
    VLM = settings["models"]["VLM"]
    LLM = settings["models"]["LLM"]
    
    
    # task settings (sample)
    
    SEARCH_TASK_LIST = [
        "Find bottol_of_tea and hamburger. Find out where they are and no need any manipulation.",
        "Find vitamin_pile and hamburger. Find out where they are and no need any manipulation.",
        "Find apple and green_medication. Find out where they are and no need any manipulation."
    ]

    OPERATE_TASK_LIST = [
        "Put bottol_of_tea which is in the refrigerator on the table. Then roast hamburger (initially on the table) in oven and after roast it, put it back to the table.",
        "Roast apple (on the table) in oven. Then take green_medication (inside the drawer_top) on table.",
        "Put orange (on the table) in to sink and throw vitamin_pile (inside the drawer_middle) to the trash_bin."
    ]

    Combine_TASK_1_LIST = [
        "Find bottol_of_tea and throw it to the trash bin.",
        "Find apple and roast it with oven. (Put it to table if you finish)",
        "Find vitamin_pile and throw it to the trash bin"
    ]

    Combine_TASK_2_LIST = [
        "Find apple, roast it, and bring it to table. Then find hamburger, roast it, and bring it to table.",
        "Find and throw bottol_of_tea and vitamin_pile to the trash bin",
        "Find orange and put it in the trash_can. Then find hamburger and roast it. After roast the hamburger (put inside the oven)."
    ]
    
    INTERACTIVEOBJECTS = settings["interactive_objects"]
    
    NAVIGATION_POINTS = settings["navigation_points"]
    
    FUNCTION_FILTER_LIST = settings["function_filter_list"]
    
    TASK = settings["task"]
    
    
    # extract prompt paths
    prompt_paths = {
        "actor" : f"{PROMPT_PATH}/TestPlanner.prompt",
        "critic" : f"{PROMPT_PATH}/Critic.prompt",
        "obsgenerator" : f"{PROMPT_PATH}/ObsGenerator.prompt",
        "summarizer" : f"{PROMPT_PATH}/SumGenerator.prompt"
    }
    
    
    config_72_ali = ModelConfig(
        model = LLM,
        base_url = BASE_URL,
        api_key = API_KEY,
        temperature = 0.2
    )

    config_72_vl_ali = ModelConfig(
        model = VLM,
        base_url = BASE_URL,
        api_key = API_KEY,
        temperature = 0.2
    )
    
    agent = CLEAAgent(
        actor_config = config_72_ali,
        critic_config = config_72_vl_ali,
        obsgenerator_config = config_72_vl_ali,
        summarizer_config = config_72_ali,
        actor_path = prompt_paths["actor"],
        critic_path = prompt_paths["critic"],
        obsgenerator_path = prompt_paths["obsgenerator"],
        summarizer_path = prompt_paths["summarizer"],
        knowledge_path=KNOWLEDGE_PATH,
        task = TASK,
        interactive_objects = INTERACTIVEOBJECTS,
        navigation_points = NAVIGATION_POINTS,
        function_filter_list = FUNCTION_FILTER_LIST,
        base64_image = False,
        max_records = 30,
        wo_critic = wo_critic
    )
    
    agent.run(TASK)
        