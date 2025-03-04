"""
Author: Msnakes 1327153842@qq.com
Date: 2024-12-17 11:44:39
LastEditors: Msnakes 1327153842@qq.com
Description: 

"""

import requests
import time

'''
Test Time
'''



URL_1 = "http://192.168.1.186:10002/api"
URL_2 = "http://192.168.1.57:10002/api"


def observe(robot) -> str|bytes:
    """
    <Description>
    Get observation from robot
    </Description>
    <Params>
    </Params>
    """
    if robot == "robot_1":
        url = f"{URL_1}/get_image"
    elif robot == "robot_2":
        url = f"{URL_2}/get_image"
    else:
        raise ValueError("Unknown Robot Name")    
    
    response = requests.get(url)

    if response.status_code == 200:
        print("get observation")
        return response.text
    else:
        raise ValueError("Network ERROR")
    

def open(robot, openable_object) -> str:
    """
    <Description>
    Open a object which support `open/close` action such as `open(robot1, refrigerator)`. Please notice that different robot has different ability to open different objects.
    </Description>
    <Params>
    robot: A string, represent which robot you want to choose. (robot_1/robot_2)
    openable_object: A string, the name of the object you want to open (must be objects in the interactive object list and can be open!)
    </Params>
    """
    if robot == "robot_1":
        url = f"{URL_1}/open"
        get_state_url = f"{URL_1}/get_state"
    elif robot == "robot_2":
        url = f"{URL_2}/open"
        get_state_url = f"{URL_2}/get_state"
    else:
        raise ValueError("Unknown Robot Name") 
    
    params = {"text": f"{openable_object}"}
    
    response = requests.get(url, params = params)
    
    action_success_record = f"{robot} open {openable_object}"
    action_error_record = f"{robot} failed to open {openable_object}"

    if response.status_code == 200:
        print(action_success_record + " start")
        time.sleep(1)
    else:
        raise ValueError("Network ERROR")
    
    if response.text.casefold() != "SUCCESS".casefold():
        return response.text
    
    while True:
        time.sleep(1)
        response = requests.get(get_state_url)
        if response.text != "RUNNING":
            if response.text == "SUCCESS":
                return action_success_record
            else:
                return action_error_record

def close(robot, openable_object) -> str:
    """
    <Description>
    Close a object which support `open/close` action such as `close(robot1, refrigerator)`. Please notice that you have open it first before you close it. You can not close something which is already closed.
    </Description>
    <Params>
    robot: Which robot (robot_1/robot_2)
    openable_object: A string, the name of the object you want to open (must be objects in the interactive object list and can be open/close!)
    </Params>
    """
    if robot == "robot_1":
        url = f"{URL_1}/close"
        get_state_url = f"{URL_1}/get_state"
    elif robot == "robot_2":
        url = f"{URL_2}/close"
        get_state_url = f"{URL_2}/get_state"
    else:
        raise ValueError("Unknown Robot Name") 
    
    params = {"text": f"{openable_object}"}
    
    response = requests.get(url, params = params)
    
    action_success_record = f"{robot} close {openable_object}"
    action_error_record = f"{robot} failed to close {openable_object}"

    if response.status_code == 200:
        print(action_success_record + " start")
        time.sleep(1)
    else:
        raise ValueError("Network ERROR")
    
    if response.text.casefold() != "SUCCESS".casefold():
        return response.text
    
    while True:
        time.sleep(1)
        response = requests.get(get_state_url)
        if response.text != "RUNNING":
            if response.text == "SUCCESS":
                return action_success_record
            else:
                return action_error_record


def pick_from(robot, object, placeable_object) -> str:
    """
    <Description>
    `robot` pick `object`
    </Description>
    <Params>
    robot: Which robot to pick up (robot_1/robot_2)
    object: A string, the name of the object you want to pick up (must be objects in the interactive object list!)
    placeable_object: Objects that robot can put object on. e.g., table, sink, oven etc.
    </Params>
    """
    if robot == "robot_1":
        url = f"{URL_1}/pick"
        get_state_url = f"{URL_1}/get_state"
    elif robot == "robot_2":
        url = f"{URL_2}/pick"
        get_state_url = f"{URL_2}/get_state"
    else:
        raise ValueError("Unknown Robot Name")   
    
    params = {"text": f"{placeable_object},{object}"}
    response = requests.get(url, params = params)

    action_success_record = f"{robot} pick up {object} from {placeable_object}"
    action_error_record = f"{robot} failed to pick up {object} from {placeable_object}"

    if response.status_code == 200:
        print(action_success_record + " start")
        time.sleep(1)
    else:
        raise ValueError("Network ERROR")
    
    if response.text.casefold() != "SUCCESS".casefold():
        return response.text
    
    while True:
        time.sleep(1)
        response = requests.get(get_state_url)
        if response.text != "RUNNING":
            if response.text == "SUCCESS":
                return action_success_record
            else:
                return action_error_record

def release_to(robot, object, placeable_object) -> str:
    """
    <Description>
    `robot` release `object`. Put the object on other object that can handle it such as put object on table or in refrigerator. Besides, throw into the trash_can can also done by calling "release_to  `trash_can`".
    </Description>
    <Params>
    robot: Which robot to release the object on its hand. (robot_1/robot_2)
    object: A string, the name of the object you want to release (must be objects that you have taked!)
    placeable_object: Objects that robot can put object on. e.g., table, sink, oven etc.
    </Params>
    """
    if robot == "robot_1":
        url = f"{URL_1}/release"
        get_state_url = f"{URL_1}/get_state"
    elif robot == "robot_2":
        url = f"{URL_2}/release"
        get_state_url = f"{URL_2}/get_state"
    else:
        raise ValueError("Unknown Robot Name")     
    
    params = {"text": f"{placeable_object},{object}"}
    response = requests.get(url, params)

    action_success_record = f"{robot} release {object} in his hand to {placeable_object}"
    action_error_record = f"{robot} release {object} in his hand to {placeable_object}"

    if response.status_code == 200:
        print(action_success_record + " start")
        time.sleep(1)
    else:
        raise ValueError("Network ERROR")
    
    if response.text.casefold() != "SUCCESS".casefold():
        return response.text
    
    while True:
        time.sleep(1)
        response = requests.get(get_state_url)
        if response.text != "RUNNING":
            if response.text == "SUCCESS":
                return action_success_record
            else:
                return action_error_record


def robot_1_navigate_to(navigation_point) -> str:
    """
    <Description>
    Robot 1 Move to a navidage point. eg: go_to("infront of refrigerator")
    </Description>
    <Params>
    navigation_point: A string, the name of the navigate point you want to goto (must be points that provide you in list!)
    </Params>
    """
    url = f"{URL_1}/navigate_to"
    get_state_url = f"{URL_1}/get_state"
    
    params = {"text": f"{navigation_point}"}
    response = requests.get(url, params = params)

    action_success_record = f"robot_1 navigate to {navigation_point}"
    action_error_record = f"robot_1 failed to navigate to {navigation_point}"

    if response.status_code == 200:
        print(action_success_record + " start")
        time.sleep(1)
    else:
        raise ValueError("Network ERROR")
    
    if response.text.casefold() != "SUCCESS".casefold():
        return response.text
    
    while True:
        time.sleep(1)
        response = requests.get(get_state_url)
        if response.text != "RUNNING":
            if response.text == "SUCCESS":
                return action_success_record
            else:
                return action_error_record
