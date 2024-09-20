

from queue import Queue
from threading import Event as ThreadEvent
from .worker import Worker
from .config import (
    PARTICPANT_NAME,
    PARTICIPANT_COLOR,
    AGENT_NAME,
    AGENT_COLOR,
    SYSTEM_PROMPT,
    DEFAULT_MODEL_PATH,
    ice_breakers,
    aperture_science_logo


)

import subprocess

default_params = {
     
}

terminus_command = "[COMMAND EXECUTED]"

class Interpreter(Worker):

  def __init__(self, consumption_queue, stop_event=None, params=None):

          super().__init__(default_params, stop_event, params, consumption_queue)


          self.shell = subprocess.Popen(
              ['bash'],
              stdin=subprocess.PIPE,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE,
              text=True,
              bufsize=1  # Line-buffered
          )
          # self.shell.communicate()
          self.shell.stdin.write('cd ~\n')
          self.shell.stdin.flush()
  

  def read_output(self):
      # read everything from the stdout
      # until the shells command exits its program
      # note that this is a blocking call
      # also note that we are only waiting until the command exits, not the shell itself
      final_output = ""
      while self.shell.poll() is None:
          # print("got here")
          output = self.shell.stdout.readline()
          # print(f'output: {output.strip()}')
          # print("got here after")
          # print()
          if output.strip() == terminus_command:
              # print("terminus command")
              break
          final_output += output
      return final_output
      
  def run_command(self, command):
       
      try:
          # print(f'command: {command}')
          self.shell.stdin.write(command + '\n')
          self.shell.stdin.flush()

          # flush another msg command to indicate that the command has been executed
          self.shell.stdin.write(f'echo "{terminus_command}"\n')
          self.shell.stdin.flush()

      except ValueError as e:
          print(f"Error writing to stdin: {e}")
      
       
       

  def run(self):
      while not self.stop_event.is_set():
          command = self.consumption_queue.get()
          self.run_command(command)
          result = self.read_output()
          self.publish_queue.put(result)

      self.publish_queue.put(None)
  
  def cleanup(self):
      self.shell.stdin.close()
      self.shell.stdout.close()
      self.shell.stderr.close()

      self.shell.terminate()
      try:
          self.shell.wait(timeout=3.0)
      except subprocess.TimeoutExpired:
          self.shell.kill()
          self.shell.wait()


def main():
    
    # interactive user tester
    stop_event = ThreadEvent()
    publish_queue = Queue()
    interpreter = Interpreter(publish_queue, stop_event=stop_event)
    interpreter.start()

    while True:
        try:
            working_dir = interpreter.shell.stdin.write('pwd\n')
            interpreter.shell.stdin.flush()
            working_dir = interpreter.shell.stdout.readline()
            command = input(f"{working_dir.strip()}$:")
            publish_queue.put(command.strip())

            # wait for response on the 
            response = interpreter.publish_queue.get()
            print(response)
        except Exception:
            print("Exiting...")
            break
        

if __name__ == "__main__":
    main()

# import subprocess
# import threading
# import queue

# class TerminalInterpreter(threading.Thread):
#     def __init__(self):
#         super().__init__()
#         # Start a bash shell process
#         self.shell = subprocess.Popen(
#             ['bash'],
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             bufsize=1  # Line-buffered
#         )
#         # change working directory to home
#         self.run_command('cd ~')
#         self.running = True
#         self.output_queue = queue.Queue()

#         # Start a separate thread for reading output
#         self.output_thread = threading.Thread(target=self.read_output)
#         self.output_thread.daemon = True
#         self.output_thread.start()

#     def read_output(self):
#         while self.running:
#             if self.shell.poll() is not None:
#                 break

#             output = self.shell.stdout.readline()
#             if output:
#                 self.output_queue.put(output.strip())

#     def run_command(self, command):
#         if self.shell.poll() is None:  # Check if the process is still running
#             try:
#                 self.shell.stdin.write(command + '\n')
#                 self.shell.stdin.flush()
#             except ValueError as e:
#                 print(f"Error writing to stdin: {e}")
#         else:
#             print("Shell process is not running. Restarting the process.")
#             self.restart_shell()

#     def run(self):
#         waiting = False
#         while self.running:
#             # Print any output from the output queue
#             while not self.output_queue.empty() or waiting:
#                 print(f'{self.output_queue.get()}')
#                 waiting = False
              
#             command = input("$: ")
#             waiting = True
#             if command.lower() == 'exit':
#                 self.running = False
#                 self.shell.terminate()
#                 break
#             self.run_command(command)

# interpreter = TerminalInterpreter()
# interpreter.start()
