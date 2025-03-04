import ast
from typing import Any, Callable
import importlib
from CLEA.BaseModules.BaseFunction import BaseFunction
from CLEA.API import API

class APIProcesser:
    def __init__(
            self,
            api_file_path : str = API.__file__,
            function_filter_list : list[str] = None
        ) -> None:
        '''
        filter list: a list of function name. The function in the list will not provided to the agent
        '''
        self.api_file_path = api_file_path
        self.function_filter_list = function_filter_list
        self.function_name_list =self.__get_functions_name_from_file(api_file_path)
        self.function_list = self.__get_all_callable()
        self.basefunction_list = [BaseFunction(func) for func in self.function_list]
        
    def get_base_fn_list(self) -> list:
        '''
        main API for APIProcesser to return basefunction list
        '''
        return self.basefunction_list
    
    def get_api_description(self) -> list[dict]:
        return [function.get_function_infos() for function in self.basefunction_list]
    
    def __get_functions_name_from_file(self, filename: str) -> list:
        """
        Get all function names from a Python file.
        
        Args:
            filename (str): Path to the Python file.
        
        Returns:
            List of function names defined in the file.
        """
        with open(filename, "r") as fp:
            tree = ast.parse(fp.read())
        
 
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        if isinstance(self.function_filter_list, list):
            functions = [fn for fn in functions if fn not in self.function_filter_list]
        
        return functions

    def __get_all_callable(self) -> list:
        '''
        get the list of callable api from the given path (change to BaseFunction)
        '''
        base_func_list = []
        for name in self.function_name_list:
            base_func_list.append(self.__get_callable_from_module(name))
        return base_func_list
            
    
    def __get_callable_from_module(self, callable_name) -> Callable[..., Any]:
        '''
        Get the callable object from module_path based on callable's name
        '''
        try:
            
            
            callable_obj = getattr(API, callable_name)
            
            
            if callable(callable_obj):
                return callable_obj
            else:
                raise ValueError(f"{callable_name} is not callable")
        
        except (ModuleNotFoundError, AttributeError) as e:
            print(f"Error: {e}")
            return None