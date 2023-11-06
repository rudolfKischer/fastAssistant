import tempfile
from playsound import playsound
from queue import Queue
from threading import Event as ThreadEvent
from .worker import Worker

from pydub import AudioSegment
from pydub.effects import speedup

import os


default_params = {
    'lang': 'en',
    'speed': 1.3
}

class Speaker(Worker):
    
    
    def __init__(self, consumption_queue, recorder_pause_event, recorder_resume_event, stop_event=None, params=None):
        super().__init__(default_params, stop_event, params, consumption_queue)
        self.recorder_pause_event = recorder_pause_event
        self.recorder_resume_event = recorder_resume_event

        print(f"Speaker Initialized")
    
    
    def play_speach(self, input_file_path):
        playsound(input_file_path)
    
    def speak(self, speach_file_path):
        # print('Received speach file', speach_file_path)
        if speach_file_path == None:
            return
        try:
            
            # delete file
            if os.path.exists(speach_file_path):
                self.play_speach(speach_file_path)
                os.remove(speach_file_path)
        except Exception as e:
            print("Error playing speach file")
            print(e)
            return
            
    def run(self):
        while not self.stop_event.is_set():
            speach_file = self.consumption_queue.get()
            if speach_file == None:
                break
            self.recorder_pause_event.set()
            self.speak(speach_file)
            # if the qeue is empty, we resume the recorder
            if self.consumption_queue.empty():
                self.recorder_resume_event.set()
        self.publish_queue.put(None)

def main():
    stop_event = ThreadEvent()
    publish_queues = {
            "inputFiles": Queue()
        }
    elabs = False

    speaker = Speaker(publish_queues["inputFiles"],
                recorder_pause_event=None, 
                recorder_resume_event=None,
                stop_event=stop_event,
                )
    speaker.start()

    test_file = "./test.wav"
    publish_queues["inputFiles"].put(test_file)

if __name__ == "__main__":
    main()
