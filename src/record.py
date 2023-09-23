from tempfile import NamedTemporaryFile
from sounddevice import rec as sd_rec, wait as sd_wait
from numpy import int16 as np_int16
from wavio import write as wavwrite
from queue import Queue
from threading import Thread, Event as ThreadEvent
from os import remove as os_remove
from time import sleep

default_params = {
    "seconds": 2.0,
    "sample_rate": 44100,
    "channels": 1,
    "dtype": np_int16
}

class AudioRecorder(Thread):
    
    def _set_params(self, params):
        for key, value in default_params.items():
            setattr(self, key, value)
        
        if params:
            for key, value in params.items():
                setattr(self, key, value)

    def __init__(self, stop_event=None, params=None):
        super().__init__()
        self.stop_event = stop_event
        self.publish_queue = Queue()
        self.temp_files = []

        if stop_event is None:
            self.stop_event = ThreadEvent()
        
        self.pause_event = ThreadEvent()
        self.resume_event = ThreadEvent()

        self._set_params(params)

        print(f"AudioRecorder Initialized")

    def record(self):
        tempfile = NamedTemporaryFile(suffix=".wav", delete=False)
        self.temp_files.append(tempfile.name)
        audio = sd_rec(int(self.seconds * self.sample_rate),
                       samplerate=self.sample_rate, 
                       channels=self.channels, 
                       dtype=self.dtype)
        sd_wait()
        wavwrite(tempfile.name, audio, self.sample_rate, sampwidth=2)
        return tempfile.name

    def run(self):
        while not self.stop_event.is_set():
            if self.pause_event.is_set():
                # print('recorder paused')
                self.resume_event.wait()
                self.resume_event.clear()
                self.pause_event.clear()
                # print('recorder resumed')

            FILENAME = self.record()
            if not self.pause_event.is_set():
                self.publish_queue.put(FILENAME)
        self.publish_queue.put(None)

    def stop(self):
        self.stop_event.set()
        self.join()

    def cleanup(self):
        for filename in self.temp_files:
            os_remove(filename)
        self.temp_files = []

        
        

        
