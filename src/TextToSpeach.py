import tempfile
from gtts import gTTS
from queue import Queue
from threading import Event as ThreadEvent
from .elevenlabs import tts as elab_tts
from .worker import Worker
from .debug import log
from .speaker import Speaker
from .glados_tts.glados import tts_runner
import sys
import contextlib
import os
import time
from .config import PARTICPANT_NAME, AGENT_NAME




default_params = {
    'tts_mode': 'elabs',
}


tts_modes = {
    'default': gTTS,
    'elabs': elab_tts,
    'glados': tts_runner(use_p1=False, log=False).gltts
}

    


class TextToSpeach(Worker):


    def __init__(self, consumption_queue, stop_event=None, params=None):
      super().__init__(default_params, stop_event, params, consumption_queue)
      
      # self.tts_function = self.save_gtts

      # if self.elabs:
      #     self.tts_function = elab_tts
      
      # if self.glados:
      #     glados_tts = tts_runner(use_p1=False, log=False)
      #     self.tts_function = glados_tts.gltts
      self.tts_function = tts_modes[self.tts_mode]


      print(f"tts Initialized")
    
    def save_gtts(self, text, output_file_path):
        try:
            tts = gTTS(text=text, 
                        tld='com.au',
                       lang=self.lang)
        except Exception as e:
            return False
        tts.save(output_file_path)
        return True
    
    def create_speach(self, text):
        if text == None:
            return None
        if len(text) == 0 or text == "" or text == " " or text == "\n":
            return None
        
        ansi_orange = "\033[94m"
        reset = "\033[0m"
        
        
        log(f"{ansi_orange}[{AGENT_NAME}]{reset}: {text}")
        _, temp_file_path = tempfile.mkstemp(suffix='.wav')
        
        # with silence_stdout():
        self.tts_function(text, temp_file_path)
        # local save file
        
        # current time in seconds
        # current_time = time.time()
        # file_name = f"{current_time}.wav"

        # file_name = os.path.basename(file_name)
        # self.tts_function(text, file_name)


        return temp_file_path
    
    def run(self):
        while not self.stop_event.is_set():
            text = self.consumption_queue.get()
            if text is None:
                break
            try:
                speach_file = self.create_speach(text)
                if speach_file == None:
                    continue
                self.publish_queue.put(speach_file)
            except Exception as e:
                print(e)
                continue
        self.cleanup()

def main():
    
    stop_event = ThreadEvent()
    publish_queues = {
        "inputText": Queue()
    }
    tts_mode = 'glados'


    
    tts = TextToSpeach(publish_queues["inputText"],
                stop_event=stop_event,
                params={'tts_mode': tts_mode})
    
    tts.start()

    speaker = Speaker(tts.publish_queue,
                recorder_pause_event=ThreadEvent(),
                recorder_resume_event=ThreadEvent(),
                stop_event=stop_event,
                )
    speaker.start()

    while True:
        try:
            user_input = input()
            if user_input == "exit":
                break
            tts.consumption_queue.put(user_input)
        except Exception as e:
            print(e)
            break
    try:
        stop_event.set()
        tts.join()
        speaker.join()
    except Exception as e:
        print(e)
        pass
    
                      
    
