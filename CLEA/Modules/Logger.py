class Logger():
    def __init__(
            self,
            record_path : str = None,
            debug : bool = True
        ):
        self.record_path = record_path
        self.debug = debug
    
    def add_agent_record(
            self, 
            prompt : str, 
            output : str, 
            call_num : int, # How many time called
            role : str
        ) -> None:
        '''
        record the prompt and return of agent
        '''
        if self.debug:
                print(f"\n//////////////////////// {role} ////////////////////////")
                print(prompt)
                print("\n//////////////////////\n")
                print(output)
                print("//////////////////////////////////////////////////////\n")
        with open(self.record_path, 'a') as f:
            f.write(f"\n\n\n////////////////\nRole: {role}\n{role} call times: {call_num}\n\nprompt:\n{prompt}\n\noutput:\n{output}\n\n////////////////\n\n\n")
    
    def add_action_record(
            self,
            action : str,
            feedback : str,
            step : int
        ) -> None:
        '''
        record the action and feedback
        '''
        if self.debug:
                    print(f"\nstep: {step}\naction: {action}\nfeedback:\n{feedback}\n")
        with open(self.record_path, 'a') as f:
            f.write(f"\n\n*****\nstep: {step}\nAction: {action}\nfeedback: {feedback}\n*****\n\n")