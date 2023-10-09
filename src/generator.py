from ctransformers import AutoModelForCausalLM
from llama_cpp import Llama
from .chatgpt import get_response

import random


from queue import Queue
from threading import Thread, Event as ThreadEvent

import time

delay_fillers = [
    "Hmm, give me a moment...",
    "Let me think on that for a sec...",
    "Ah, let's see here...",
    "Interesting, let me ponder that...",
    "Hold on, thinking...",
    "Hmm, let me gather my thoughts...",
    "Bear with me a moment...",
    "Just a bit... I'm sorting it out.",
    "Hmm, need a second to process that...",
    "Oh? Let me mull over that...",
    "I see... give me a short pause...",
    "Hold that thought...",
    "Let me dive into that for a moment...",
    "Ah, let me sift through my thoughts...",
    "Just piecing it together...",
    "Hmm, let it marinate for a second...",
    "Hold on, it's coming to me...",
    "I'm drawing it up, just a sec...",
    "Almost there, give me a moment...",
    "Let me reflect on that briefly..."
]


default_params = {
    'local_model_path': './models/orca_mini_v3_7B-GGML/orca_mini_v3_7b.ggmlv3.q2_K.bin',
    'model_path': "TheBloke/orca_mini_v3_7B-GGML",
    'model_file': "orca_mini_v3_7b.ggmlv3.q2_K.bin",
    'model_type': "llama",
    'gpu_layers': 5,
    'max_new_tokens': 30
}

participant_name = 'YOU'
agent_name = 'ME'

system_prompt = f"""
If it says {participant_name}: , that means the human has spoken. 
Once you see {agent_name}:, you can start speaking.
After you see {participant_name}, you can stop speaking."
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
          pass
          # self.model = Llama(model_path="./models/orca-mini-3b.ggmlv3.q4_0.bin", n_ctx=512, n_batch=32, verbose=False)
          # self.model = AutoModelForCausalLM.from_pretrained(
          #     self.model_path, 
          #     model_file=self.model_file, 
          #     model_type=self.model_type, 
          #     gpu_layers=self.gpu_layers
          #     )
      
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
                  return True
              
              if self.last_spoken_participant == participant_name:
                  self.last_spoken_participant = agent_name
                  return True
          
      def generate(self, prompt):
          return get_response(prompt)
          print('Thinking...')
          self.publish_queue.put(random.choice(delay_fillers))
          # start_time = time.time()
          output = self.model(prompt,
                        temperature  = 0.7,
                        max_tokens=80,
                        top_k=20, 
                        top_p=0.9,
                        repeat_penalty=1.15,
                        stop=participant_name)
          generation_output = output['choices'][0]['text'].strip()
          # generation_output = self.model(prompt, max_new_tokens=self.max_new_tokens , stop="YOU")
          # print('Generation took', time.time() - start_time)
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
              print("[SYSTEM]:", response)
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


        