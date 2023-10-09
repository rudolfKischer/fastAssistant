

from threading import Thread, Event as ThreadEvent
from queue import Queue

class Worker(Thread):
    
    def _set_params(self, params):
        for key, value in self.default_params.items():
            setattr(self, key, value)
        
        if params:
            for key, value in params.items():
                setattr(self, key, value)
    
    def __init__(self, default_params, stop_event=None, params=None, consumption_queue=None):
        super().__init__()
        self.default_params = default_params

        self.publish_queue = Queue()
        self.consumption_queue = consumption_queue

        self.stop_event = stop_event
        if stop_event is None:
            self.stop_event = ThreadEvent()

        self.pause_event = ThreadEvent()
        self.resume_event = ThreadEvent()
        self._set_params(params)
    
    def paused(self):
        return self.pause_event.is_set()
    
    def await_resume(self):
        # print(f'{self.__class__.__name__} paused')
        self.resume_event.wait()
        self.resume_event.clear()
        self.pause_event.clear()
        # print(f'{self.__class__.__name__} unpaused')
    
    def stop(self):
        self.stop_event.set()
        self.join()

