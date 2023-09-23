from ctransformers import AutoModelForCausalLM


from queue import Queue
from threading import Thread, Event as ThreadEvent


default_params = {
    'model_path': "TheBloke/orca_mini_v3_7B-GGML",
    'model_file': "orca_mini_v3_7b.ggmlv3.q2_K.bin",
    'model_type': "llama",
    'gpu_layers': 50,
    'max_new_tokens': 30
}

participant_name = 'Them:'
agent_name = 'Me:'

system_prompt = f"""
Whenever you see [ {participant_name} ], that means the human has spoken. 
Whenever you see [ {agent_name} ], that means you have spoken.
You are trying to have a conversation with the human.
Be very sarcastic \n
\n
"""



class Generator(Thread):
      
      def _set_params(self, params):
          for key, value in default_params.items():
              setattr(self, key, value)
          
          if params:
              for key, value in params.items():
                  setattr(self, key, value)
      
      def _load_model(self):
          self.model = AutoModelForCausalLM.from_pretrained(
              self.model_path, 
              model_file=self.model_file, 
              model_type=self.model_type, 
              gpu_layers=self.gpu_layers)
      
      def __init__(self, consumption_queue, stop_event=None, params=None):
          super().__init__()
          self.consumption_queue = consumption_queue
          self.stop_event = stop_event
          self.publish_queue = Queue()
          self.running_conversation = [system_prompt]
          self.last_spoken_participant = agent_name
          if stop_event is None:
              self.stop_event = ThreadEvent()
          self._set_params(params)
          self._load_model()
          print(f"Generator Initialized")

      def get_conversation(self):
          return '\n'.join(self.running_conversation)
      
      def listening(self):
          while True:
              segments = self.consumption_queue.get()
              if segments == None:
                  return False

              if segments != []:
                  self.last_spoken_participant = participant_name
                  for segment in segments:
                      self.running_conversation.append(f"{participant_name}: {segment}")
                  continue
              
              if self.last_spoken_participant == participant_name:
                  self.last_spoken_participant = agent_name
                  return True
          
      def generate(self, prompt):
          print('Starting generation')
          generation_output = self.model(prompt, max_new_tokens=self.max_new_tokens , stop="Them:")
          return generation_output
      
      def listen_and_respond(self):
          keep_listening = self.listening()
          if keep_listening:
              conversation = self.get_conversation()
              prompt = f"{conversation}\n{agent_name}: "
              # print()
              # print("Prompt:", prompt)
              # print()
              response = self.generate(prompt)
              self.running_conversation.append(f"{agent_name}: {response}")
              print("Response:", response)
              self.publish_queue.put(response)
          return keep_listening
  
      def run(self):
          while not self.stop_event.is_set():
              keep_listening = self.listen_and_respond()
              if not keep_listening:
                  break
          self.publish_queue.put(None)
  
      def stop(self):
          print(self.running_conversation())
          self.stop_event.set()
          self.join()

      
      def cleanup(self):
          self.model = None


        