import gymnasium as gym
from CLEA.API import API
from CLEA.Modules.ObsGenerator import ObsGenerator
import hashlib
import base64
import os
import logging
from io import BytesIO
from PIL import Image

def merge_images_horizontally(base64_image1, base64_image2):
    
    try:
        
        img1_data = base64.b64decode(base64_image1)
        img2_data = base64.b64decode(base64_image2)
        
        
        img1 = Image.open(BytesIO(img1_data)).convert('RGB')
        img2 = Image.open(BytesIO(img2_data)).convert('RGB')
        
        
        width1, height1 = img1.size
        width2, height2 = img2.size
        
       
        new_width = width1 + width2
        new_height = max(height1, height2)
        new_img = Image.new('RGB', (new_width, new_height), (255, 255, 255)) 
        
    
        new_img.paste(img1, (0, (new_height - height1) // 2))  
        new_img.paste(img2, (width1, (new_height - height2) // 2))  
        
        
        buffered = BytesIO()
        new_img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()
        
    except Exception as e:
        return f"Error: {str(e)}"

def generate_image_filename(base64_bytes, length=24, file_type : str = 'jpg'):
    # decode b64 image
    image_data = base64.b64decode(base64_bytes)
    
    # SHA-256
    hash_object = hashlib.sha256(image_data)
    
    # Bin2Hex
    hash_hex = hash_object.hexdigest()
    
    # hash lenth
    file_name = hash_hex[:length]
    
    # jpg file
    file_name_with_extension = file_name + f'.{file_type}'
    
    return file_name_with_extension, image_data

def save_image_from_base64(base64_bytes, save_path, file_type: str = 'jpg') -> str:
    try:
        # Ensure save_path exists
        if not os.path.exists(save_path):
            logging.error(f"Save path does not exist: {save_path}")
            raise ValueError(f"Invalid save path: {save_path}")
        
        # Generate filename and image data
        file_name, image_data = generate_image_filename(base64_bytes, file_type=file_type)
        
        # Combine full file path
        full_path = os.path.join(save_path, file_name)
        
        # Write image to file
        with open(full_path, 'wb') as f:
            f.write(image_data)
        
        logging.info(f"Image saved to {full_path}")
        return full_path
    except Exception as e:
        logging.error(f"Error saving image from base64: {e}")
        raise

    return full_path
class BridgeEnv(gym.Env):
    '''
    This env is a bridge from Robotic to our Agent
    '''
    def __init__(
            self,
            obs_generator : ObsGenerator,
            task : str,
            interactive_objects : list[str],
            navigation_points : list[str],
            base64_image : bool = True,
            image_save_path : str = None, 
        ) -> None:
        super().__init__()
        self.task = task
        self.base64_image = base64_image
        self.image_save_path = image_save_path
        self.obs_generator = obs_generator
        self.interactive_objects = interactive_objects
        self.navigation_points = navigation_points
        self.obs_img = None # store the newest observation image (in base64) 
        self.obs_text = None # store the text (in text)
        
    def __preprocess_image(self, image_base64):
        '''
        preprocess and save image
        '''
        if self.base64_image:
            self.obs_img = image_base64 # save for do not call description redundently
            return image_base64
        else:
            if self.image_save_path == None:
               raise ValueError("If you need to save image, you have to provide image saving path!!!")
            image_name = save_image_from_base64(image_base64, self.image_save_path)
            self.obs_img = image_name

            return image_name

    def __obs(self) -> bytes|str:
        image_base64_1 = API.observe("robot_1")
        image_base64_2 = API.observe("robot_2")
        image_base64 = merge_images_horizontally(image_base64_1, image_base64_2)
        return self.__preprocess_image(image_base64)
        
    def __apply_obs_generator(self, image : bytes|str, subgoal : str) -> str:
        '''
        explain the observed image
        - subgoal: may be needed for further concentration
        '''
        if subgoal != None:
            params = {
                "task" : self.task,
                "subgoal" : subgoal,
                "objects" : self.interactive_objects,
                "navi_points" : self.navigation_points
            }
        else:
            params = {
                "task" : self.task,
                "objects" : self.interactive_objects,
                "navi_points" : self.navigation_points
            }
        # save for remove redundent observation
        self.obs_text = self.obs_generator.get_obs_description(params, image_paths = [image], base64_image = self.base64_image)
        return self.obs_text
    
    def __get_obs(self, subgoal : str = None) -> str:
        '''
        get the observation with description
        '''
        return self.__apply_obs_generator(self.__obs(), subgoal)

    def step(self, fn_call : str, subgoal : str = None) -> tuple:
        '''
        return: feedback, observation
        feedback: string
        observation: image (path or base64)
        '''
        try:
            feedback = eval(f"API.{fn_call}")
            image = self.__obs()
        except:
            # handle error
            error_message = "The action is not valid"
            print(error_message)
            feedback = error_message
            image = self.__obs() # in most of cases!
            
        return feedback, self.__apply_obs_generator(image, subgoal)
    
    def reset(self) -> tuple:
        '''
        return: feedback, observation
        feedback: string, your task
        observation: image (path or base64)
        '''
        return self.task, self.__get_obs()
        
            


            

            