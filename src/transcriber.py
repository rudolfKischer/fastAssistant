from tempfile import NamedTemporaryFile
from sounddevice import rec as sd_rec, wait as sd_wait
from numpy import int16 as np_int16, vstack as np_vstack
from wavio import write as wavwrite, read as wavread
from queue import Queue
from threading import Thread, Event as ThreadEvent
from os import remove as os_remove, path as os_path
from faster_whisper import WhisperModel
from .debug import log, log1

default_params = {
    'model_size': "tiny",
    'device': 'cpu',
    'compute_type': 'int8',
    'vad_filter': True,
    'vad_parameters': dict(min_silence_duration_ms=500),
    'seconds': 2.0
}

class Transcriber(Thread):
    
    def _set_params(self, params):
        for key, value in default_params.items():
            setattr(self, key, value)
        
        if params:
            for key, value in params.items():
                setattr(self, key, value)
    
    def _load_model(self):
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        
    def __init__(self, consumption_queue, stop_event=None, params=None, audio_pause_event=None, audio_resume_event=None):
        super().__init__()
        self.stop_event = stop_event
        self.consumption_queue = consumption_queue
        self.publish_queues = {
            "transcription": Queue(),
            "merged_audio": Queue()
        }
        self.temp_files = []

        self.audio_pause_event = audio_pause_event
        self.audio_resume_event = audio_resume_event

        if stop_event is None:
            self.stop_event = ThreadEvent()
        
        self._set_params(params)

        self._load_model()

        print(f"Transcriber Initialized: {self.seconds} {self.model_size} {self.device} {self.compute_type}")
    

    
    def transcribe_file(self, filename):
        segments, _ = self.model.transcribe(filename, 
                                            vad_filter=self.vad_filter, 
                                            vad_parameters=self.vad_parameters)
        return list(segments)
    
    def aggregate_audio(self, filenames): 
        """Combines multiple WAV files into a single WAV file."""
        aggregated_audio_file = NamedTemporaryFile(suffix=".wav", delete=False)
        self.temp_files.append(aggregated_audio_file.name)
        aggregated_audio = []
        for filename in filenames:
            wav_obj = wavread(filename)
            aggregated_audio.append(wav_obj.data)
        aggregated_audio = np_vstack(aggregated_audio)
        wavwrite(aggregated_audio_file.name, aggregated_audio, wav_obj.rate, sampwidth=2)
        return aggregated_audio_file.name
    
    def transcribe_audio(self):
        """Transcribes the audio in the consumption queue."""
        aggregated_audio_filename = self.consumption_queue.get()
        self.temp_files.append(aggregated_audio_filename)
        log("Transcribing Started")

        self.audio_pause_event.set()
        log1(f"Audio Length: {wavread(aggregated_audio_filename).data.shape[0] / wavread(aggregated_audio_filename).rate} seconds")
        segments = self.transcribe_file(aggregated_audio_filename)
        log("Transcribing Ended")
        self.audio_resume_event.set()

        segments = [s.text.strip() for s in segments]
        if segments != []:
            self.publish_queues["transcription"].put(segments)
            self.publish_queues["merged_audio"].put(aggregated_audio_filename)
        else:
            log(f'No transcription found')

    def run(self):
        while not self.stop_event.is_set():
            self.transcribe_audio()
        for queue in self.publish_queues.values():
            queue.put(None)

    def purge_files(self, filenames):
        for filename in filenames:
            if os_path.exists(filename):
                os_remove(filename)

    def stop(self):
        self.stop_event.set()
        self.join()

    def cleanup(self):
        self.purge_files(self.temp_files)
        self.temp_files = []
        del self.model
        self.model = None