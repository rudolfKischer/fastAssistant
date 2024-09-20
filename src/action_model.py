
from .terminal_interpreter import TerminalInterpreter
from .worker import Worker
default_params = {}

# the interpreter class has a consumption queue which commands can be sent to
# and a publish queue which the output of the commands will be sent to

# our action model also has a consumption queue
# On the consumption queue we will have high level goals we want accomplished
# When the action model receives a high level goal it will first create a plan
# then it will enter a loop:
# 

class ActionModel(Worker):


  def __init__(self, consumption_queue, stop_event=None, params=None):

          super().__init__(default_params, stop_event, params, consumption_queue)


