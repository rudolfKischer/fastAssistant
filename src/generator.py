from .generators import generator_names

import random


from queue import Queue
from threading import Thread, Event as ThreadEvent
from .worker import Worker
from .speaker import Speaker
from huggingface_hub import hf_hub_url, cached_download

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

participant_name = 'YOU'
agent_name = 'ME'

default_params = {
    # 'generator_type': 'chatgpt',
    'generator_type': 'llamacpp',
    # 'local_model_path': './models/q4_0-orca-mini-3b.gguf',
    # 'local_model_path': './models/dolphin-2.1-mistral-7b.Q2_K.gguf',
    # 'local_model_path': './models/Marx-3B-V2-Q4_1-GGUF.gguf',
    'local_model_path': './models/luna-ai-llama2-uncensored.Q2_K.gguf',
    # 'local_model_path': './models/q5_k_m-sheared-llama-2.7b.gguf',
    # 'local_model_path': './models/tinyllama-1.1b-chat-v0.3.Q2_K.gguf',
    'max_tokens': 200,
    'thinking_fillers': False,
    'stop_strings': [participant_name, agent_name, '[You]'],
    'max_context_length': 512
}

system_prompt = f"""
### System Prompt
The human has spoken if it says "{participant_name}:" ,  
You can start speaking once you see "{agent_name}:", 
Be Playful and try to make the human laugh.
Insert natural pauses with "..." or "," or "uhh" or "umm". 
Dont be afraid to ask questions or to bring up interesting topics.
Always end on a question, or something that encourages the human to speak.

### Conversation
 \n
"""


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

          if segments == []:
              return True
          
          for segment in segments:
              print(f"[USER]: {segment}")
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
      
      def listen_and_respond(self):
          keep_listening = self.listening()
          if keep_listening:
              prompt = self.get_prompt()
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
                              'local_model_path': './models/luna-ai-llama2-uncensored.Q2_K.gguf',
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
    
    speaker_on = True
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

        