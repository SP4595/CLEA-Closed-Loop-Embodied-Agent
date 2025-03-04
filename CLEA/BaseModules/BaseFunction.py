from typing import Any, Callable
import inspect # get the description of a function
import re
from CLEA.utils import extract_tag_content

class BaseFunction:
    def __init__(
            self,
            function : Callable[..., Any],  # Specify that this is a callable
        ) -> None:
        self.function = function
        params, function_description = self.__extract_function_infos()
        self.function_description = function_description
        self.function_name = function.__name__
        self.expression = self.__get_function_call_format()
        self.params = params
        
    def __get_function_call_format(self):
      
        signature = inspect.signature(self.function)
        
       
        func_name = self.function_name
        
      
        params = ', '.join(str(param) for param in signature.parameters)
        
      
        callable_str = f"{func_name}({params})"
        
        return callable_str
    
    def __extract_function_infos(self) -> tuple:
        '''
        Get the description of the function should be in the reast format:
        ```python
        """
        <Description>
        ...
        </Description>
        <Params>
        ...
        </Params>
        """
        return: 
        params, description
        '''
        doc_string = self.function.__doc__
        
     
        doc_string = '\n'.join([line.strip() for line in doc_string.split('\n')])
        

        description = extract_tag_content(doc_string, "Description")

       
        params = extract_tag_content(doc_string, "Params")
        
        return params, description
    
    def get_function_infos(self) -> dict:
        '''
        return function's info in Dictionary mode
        '''
        ret_dict = {
            "function_expression": self.expression,
            "description" : self.function_description,
            "params": self.params
        }
        return ret_dict
    
    def __str__(self) -> str:
        return f"function_expression:\n{self.expression}\n\ndescription:\n{self.function_description}\n\nparams:\n{self.params}"
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        '''
        Call the function
        '''
        return self.function(*args, **kwds)
      
if __name__ == "__main__":
    def example_function(alpha, b, c, d : int, e = 114, f : int = 10):
        '''
        This is an example function.
        <Description>
        Adds two numbers.
        </Description>
        <Params>
        None
        </Params>
        '''
        return 114514
    fn = BaseFunction(example_function)
    print(fn)
    print("///////////////")
    infos = fn.get_function_infos()
    print(infos)
    print("///////////////")
    print(fn(1, 2, 3, 4, 5, 6))
        