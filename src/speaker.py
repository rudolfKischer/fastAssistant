import tempfile
from gtts import gTTS
from playsound import playsound
from queue import Queue
from threading import Thread, Event as ThreadEvent
from .elevenlabs import tts as elab_tts
from .worker import Worker

default_params = {
    'lang': 'en',
    'elabs': False
}

class Speaker(Worker):
    
    
    def __init__(self, consumption_queue, recorder_pause_event, recorder_resume_event, stop_event=None, params=None):
        super().__init__(default_params, stop_event, params, consumption_queue)
        
        self.recorder_pause_event = recorder_pause_event
        self.recorder_resume_event = recorder_resume_event



        self.tts_function = self.save_gtts

        if self.elabs:
            self.tts_function = elab_tts

        print(f"Speaker Initialized")

    def save_gtts(self, text, output_file_path):
        try:
            tts = gTTS(text=text, lang=self.lang)
        except Exception as e:
            return False
        tts.save(output_file_path)
        return True
    
    def play_speach(self, input_file_path):
        
        if (self.recorder_pause_event != None):
          self.recorder_pause_event.set()
          playsound(input_file_path)
          self.recorder_resume_event.set()
        else:
          playsound(input_file_path)
        
    
    def speak(self, text):
        if text == None:
            return
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
            if not self.tts_function(text, fp.name):
                return
            self.play_speach(fp.name)
            
    def run(self):
        while not self.stop_event.is_set():
            text = self.consumption_queue.get()
            if text == None:
                break
            self.speak(text)
        self.publish_queue.put(None)

def main():
    stop_event = ThreadEvent()
    publish_queues = {
            "inputText": Queue()
        }
    elabs = True

    speaker = Speaker(publish_queues["inputText"], 
                recorder_pause_event=None, 
                recorder_resume_event=None,
                stop_event=stop_event,
                params={'elabs': elabs},
                )
    speaker.start()

    
    # loop get input
    while True:
        try:
            user_input = input()
            publish_queues["inputText"].put(user_input)
        except Exception:
            break

    try:
        speaker.join()
        print("Joined Threads.")
    except KeyboardInterrupt:
        print("Stopping threads...")
        stop_event.set()
        print("Stopped.")

if __name__ == "__main__":
    main()
