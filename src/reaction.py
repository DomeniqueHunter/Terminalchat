import inspect

EXCEPTION_REACTION_HANDLER = "__EXCEPTION__"


class Reaction():
        
    def __init__(self, defaultExceptionFunction=None):
        self.actions = {}
        if defaultExceptionFunction and (inspect.isfunction(defaultExceptionFunction) or inspect.ismethod(defaultExceptionFunction)):
            self.__add_action(EXCEPTION_REACTION_HANDLER, defaultExceptionFunction)
        else:
            self.__add_action(EXCEPTION_REACTION_HANDLER, self.__defaultException)
            
    def add_action(self, handler, function):
        return self.__add_action(handler, function)
    
    def __add_action(self, handler, function):
        if inspect.isfunction(function):
            self.actions[handler] = function
            self.actions[handler].__dict__['len'] = function.__code__.co_argcount
            print(f"+ set action for function: {handler} ({self.actions[handler].len})")
            
        elif inspect.ismethod(function): 
            self.actions[handler] = function
            self.actions[handler].__dict__['len'] = function.__code__.co_argcount - 1                   
            print(f"+ set action for method: {handler} ({self.actions[handler].len})")
            
        else:
            self.react(EXCEPTION_REACTION_HANDLER, handler, 'is not a function or method')
        
    def react(self, handler, *args):
        try:
            if handler in self.actions:
                return self.actions[handler](*args[:self.actions[handler].len])
            return self.react(EXCEPTION_REACTION_HANDLER, handler)
        except:
            return self.react(EXCEPTION_REACTION_HANDLER, handler)
        
    def __defaultException(self, handler, message='handler not found!'):
        """
            The default Exception, should be replaced!
        """
        return f"EXCEPTION: {handler} {message}"
        