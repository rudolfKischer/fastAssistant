import numpy as np
import webrtcvad
import tempfile
from ..worker import Worker
import wavio
import os
from ..debug import log

default_params = {
    "seconds": 0.03,
    "sample_rate": 32000,
    "majority_window": 8,
    "min_speech_frames": 5,
    "min_seconds_audio": 1,
    "max_seconds_audio": 10,
    "pre_audio_buffer": 0.02,
    "vad_mode": 3, #0 - 3, 0: lets most things through, 3: lets few things through
    "post_speach_window": 2.5
}

class VoiceDetector(Worker):
    
    def __init__(self, consumption_queue, stop_event=None, params=None):
        super().__init__(default_params, stop_event, params, consumption_queue)

        self.vad = webrtcvad.Vad(self.vad_mode)
        self.vad_buffer = [0] * self.majority_window
        self.pre_audio_buffer = [0] * int(self.pre_audio_buffer * self.seconds * self.sample_rate)
        self.audio_buffer = [0]
        self.capture_audio = False
        self.chunksize = int(self.seconds * self.sample_rate)

        self.temp_files = []
        self.silence_timer = 0.0
    
    def publish_buffer_audio(self):
        audio_data = self.pre_audio_buffer + self.audio_buffer
        audio_data = np.vstack(audio_data)
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        wavio.write(audio_file.name, audio_data, self.sample_rate, sampwidth=2)

        # audio_saves_directory = '/Users/rudolfkischer/Projects/FastAssistant/audio_scraps'
        # date_time = datetime.datetime.now()
        # audio_file_name = f'{audio_saves_directory}/audio_{date_time}.wav'
        # wavio.write( audio_file_name, audio_data, self.sample_rate, sampwidth=2)

        self.temp_files.append(audio_file.name)
        self.publish_queue.put(audio_file.name)
        self.audio_buffer.clear()

    def majority_vote(self):
        return 1 if sum(self.vad_buffer) > len(self.vad_buffer) / 2 else 0

    def detect_voice(self, indata):
        is_speech = self.vad.is_speech(indata.tobytes(), self.sample_rate)
        # print(is_speech)
        self.vad_buffer.append(is_speech)
        self.vad_buffer.pop(0)
        return self.majority_vote()
    
    def check_audio_capture(self, voice_detected):
        if voice_detected == 1:
            self.silence_timer = 0.0
        
        if voice_detected == 0:
            self.silence_timer += self.seconds

        # print(voice_detected)
        if not self.capture_audio and voice_detected == 1:
            log("Listening...")
            self.capture_audio = True


        above_min_audio_threshold = len(self.audio_buffer) > self.min_seconds_audio / self.seconds

        if self.capture_audio and voice_detected == 0 and above_min_audio_threshold and self.silence_timer > self.post_speach_window:
            log("Voice Ended")
            self.capture_audio = False
            self.publish_buffer_audio()

    def perform_audio_capture(self, indata):
        if self.capture_audio:
            self.audio_buffer.append(indata.copy())
        
        if not self.capture_audio:
            self.pre_audio_buffer.append(indata.copy())
            self.pre_audio_buffer.pop(0)

        
        # buffer overflows
        buffer_length = len(self.audio_buffer) * self.seconds
        if buffer_length > self.max_seconds_audio:
            self.publish_buffer_audio()

        
    def run(self):
        while not self.stop_event.is_set():

            indata = self.consumption_queue.get()
            if indata is None:
                break
            
            #if the length of the audio buffer is greater than chunksize
            # break it up into chunks and put it back into the queue
            if len(indata) > self.chunksize:
                for i in range(0, len(indata), self.chunksize):
                    self.consumption_queue.put(indata[i:i+self.chunksize])
                continue
            
            voice_detected = self.detect_voice(indata)
            self.check_audio_capture(voice_detected)
            self.perform_audio_capture(indata)

    
    def cleanup(self):
        for filename in self.temp_files:
            if os.path.exists(filename):
                os.remove(filename)