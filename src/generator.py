from .generators import generator_names

import random

from queue import Queue
from threading import Event as ThreadEvent
from .worker import Worker
from .speaker import Speaker
from huggingface_hub import hf_hub_url, cached_download
from .utils import split_into_sentences, delay_fillers
from threading import Timer
from .config import (
    PARTICPANT_NAME,
    AGENT_NAME,
    SYSTEM_PROMPT,
    DEFAULT_MODEL_PATH,
    ice_breakers


)


participant_name = PARTICPANT_NAME
agent_name = AGENT_NAME

default_params = {
    # 'generator_type': 'chatgpt',
    'generator_type': 'llamacpp',
    'local_model_path': DEFAULT_MODEL_PATH,
    'max_tokens': 200,
    'thinking_fillers': False,
    'stop_strings': [participant_name, agent_name, '[You]'],
    'max_context_length': 512,
    'segment_response': True,
    'self_intro': False,
    'idle_responses': True,
    'idle_response_interval': [35, 150],

}

system_prompt = SYSTEM_PROMPT


class Generator(Worker):

      def _load_model(self):
          self.model = generator_names[self.generator_type](model_path=self.local_model_path)
      
      def __init__(self, consumption_queue, stop_event=None, params=None):
          super().__init__(default_params, stop_event, params, consumption_queue)

          # init conversation
          self.running_conversation = []
          self.last_spoken_participant = agent_name
          
          # Initialize generator
          self.model = generator_names[self.generator_type](
              stop_strings = self.stop_strings,
              max_tokens = self.max_tokens,
              model_path = self.local_model_path
          )
          print(f"Generator Initialized")

          self.idle_response_timer = None
      
      def initiate_conversation(self):
          # ice breakers should be prompts that allow the llm to figure out what to do
          ice_breaker = random.choice(ice_breakers)
          self.running_conversation.append(ice_breaker)
          prompt = self.get_prompt()
          response = self.generate(prompt)
          self.running_conversation.append(f"{agent_name}: {response}")
          if self.segment_response:
              response = self.segment_text(response)
          else:
              response = [response]
          for segment in response:
              self.publish_queue.put(segment)
          
          self.reset_idle_response_timer()

          
          

      def reset_idle_response_timer(self):
          if self.idle_response_timer is not None:
              self.idle_response_timer.cancel()
          self.idle_response_timer = Timer(random.randint(*self.idle_response_interval), self.initiate_conversation)
          self.idle_response_timer.start()
              
      def get_conversation(self):
          return '\n'.join(self.running_conversation)

      def get_prompt(self):
          conversation = self.get_conversation()
          chars_per_token = 2.5 
          window_size = min(int(self.max_context_length * chars_per_token), (len(conversation)))
          context_window = conversation[-window_size:len(conversation)]
          prompt = f'{system_prompt}\n{context_window}\n{agent_name}:'
          return prompt
          
      def listening(self):
          segments = self.consumption_queue.get()
          if segments == None:
              return False
          

          self.reset_idle_response_timer()

          if segments == []:
              return True
          
          for segment in segments:
              print(f"[{participant_name}]: {segment}")
              self.running_conversation.append(f"{participant_name}: {segment}")
          return True

      def stall_for_time(self):
          print('Thinking...')
          filler = random.choice(delay_fillers)
          print(f'[SYSTEM]: {filler}')
          self.publish_queue.put(filler)

      def generate(self, prompt):
          if self.thinking_fillers:
              self.stall_for_time()
          return self.model.generate(prompt)
      
      def segment_text(self, text):
          return split_into_sentences(text)
          
      
      def listen_and_respond(self):
          keep_listening = self.listening()
          if keep_listening:
              prompt = self.get_prompt()
              response = self.generate(prompt)
              self.running_conversation.append(f"{agent_name}: {response}")
              # print(f"[{agent_name}]:", response)
              if self.segment_response:
                  response = self.segment_text(response)
              else:
                  response = [response]
              for segment in response:
                  self.publish_queue.put(segment)

          return keep_listening
  
      def run(self):
          self.reset_idle_response_timer()
          while not self.stop_event.is_set():
              keep_listening = self.listen_and_respond()
              if not keep_listening:
                  break
          self.publish_queue.put(None)
      
      def cleanup(self):
          self.model = None

def main():
    stop_event = ThreadEvent()
    publish_queues = {
            "transcription": Queue(),
            "merged_audio": Queue()
        }
    generator = Generator(publish_queues["transcription"], 
                          stop_event=stop_event, 
                          params={
                              'local_model_path': DEFAULT_MODEL_PATH,
                              'generator_type': 'chatgpt',
                              'max_tokens': 100
                          })
    generator.start()

    elabs = True
    speaker = Speaker(generator.publish_queue,
            recorder_pause_event=None, 
            recorder_resume_event=None,
            stop_event=stop_event,
            params={'elabs': elabs},
            )
    
    speaker_on = False
    if speaker_on:
      speaker.start()

    
    # loop get input
    while True:
        try:
            user_input = input()
            publish_queues["transcription"].put([user_input])
        except Exception:
            break

    try:
        generator.join()
        print("Joined Threads.")
    except KeyboardInterrupt:
        print("Stopping threads...")
        stop_event.set()
        print("Stopped.")

    

if __name__ == "main":
    main()

        