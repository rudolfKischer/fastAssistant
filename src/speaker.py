import tempfile
from gtts import gTTS
from playsound import playsound
from queue import Queue
from threading import Thread, Event as ThreadEvent

# def play_text(text):
#     # Convert text to audio
#     tts = gTTS(text=text, lang='en')

#     # Use a temporary file to save the audio
#     with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
#         tts.save(fp.name)
#         playsound(fp.name)

# play_text("Hello, this is a text to speech conversion using a temporary file.")

default_params = {
    'lang': 'en',
}

class Speaker(Thread):
    
    def _set_params(self, params):
        for key, value in default_params.items():
            setattr(self, key, value)
        
        if params:
            for key, value in params.items():
                setattr(self, key, value)
    
    def __init__(self, consumption_queue, recorder_pause_event, recorder_resume_event, stop_event=None, params=None):
        super().__init__()
        self.stop_event = stop_event
        self.consumption_queue = consumption_queue
        self.publish_queue = Queue()

        if stop_event is None:
            self.stop_event = ThreadEvent()
        
        self._set_params(params)

        self.recorder_pause_event = recorder_pause_event
        self.recorder_resume_event = recorder_resume_event

        print(f"Speaker Initialized")

    def speak(self, text):
        if text == None:
            return
        try:
            tts = gTTS(text=text, lang='en')
        except Exception as e:
            return
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
            tts.save(fp.name)
            self.recorder_pause_event.set()
            playsound(fp.name)
            self.recorder_resume_event.set()
    
    def run(self):
        while not self.stop_event.is_set():
            text = self.consumption_queue.get()
            if text == None:
                break
            self.speak(text)
        self.publish_queue.put(None)

    def stop(self):
        self.stop_event.set()
        self.join()
    
    def cleanup(self):
        pass
