import numpy as np
import webrtcvad
import tempfile
from .worker import Worker
import wavio
import os

default_params = {
    "seconds": 0.03,
    "sample_rate": 32000,
    "majority_window": 8,
    "min_speech_frames": 5,
    "min_seconds_audio": 1,
    "max_seconds_audio": 4,
    "pre_audio_buffer": 0.02,
    "vad_mode": 3, #0 - 3, 0: lets most things through, 3: lets few things through
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
        self.vad_buffer.append(is_speech)
        self.vad_buffer.pop(0)
        return self.majority_vote()
    
    def check_audio_capture(self, voice_detected):
        if not self.capture_audio and voice_detected == 1:
            print("Voice Detected")
            self.capture_audio = True

        # only end audio capture if longer than min seconds

        if self.capture_audio and voice_detected == 0 and len(self.audio_buffer) > self.min_seconds_audio / self.seconds:
            print("Voice Ended")
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



# # Constants
# RATE = 16000
# FRAME_DURATION = 0.03  # 30ms
# FRAME_SIZE = int(RATE * FRAME_DURATION)
# MAJORITY_WINDOW = 10  # Number of frames for majority voting
# MIN_SPEECH_FRAMES = 4  # Minimum consecutive frames to consider as speech

# # Initialize VAD with the most aggressive mode
# vad = webrtcvad.Vad(3)

# # Buffer to store VAD results and audio data
# vad_buffer = [0] * MAJORITY_WINDOW
# audio_buffer = []

# # Audio callback
# def audio_callback(indata, frames, time, status):
#     is_speech = vad.is_speech(indata.tobytes(), RATE)
#     vad_buffer.append(is_speech)
#     vad_buffer.pop(0)

#     # Majority voting
#     majority_decision = 1 if sum(vad_buffer) > len(vad_buffer) / 2 else 0

#     # Minimum speech length thresholding
#     if majority_decision == 1:
#         audio_buffer.append(majority_decision)
#         if len(audio_buffer) < MIN_SPEECH_FRAMES:
#             majority_decision = 0
#     else:
#         audio_buffer.clear()

#     vad_buffer[0] = majority_decision

# # Setting up the figure, the axis, and the plot elements
# fig, ax = plt.subplots()
# x = np.arange(0, 10, FRAME_DURATION)
# y = np.zeros_like(x)
# line, = ax.plot(x, y, '-o', color='blue')
# ax.set_ylim(0, 1.1)
# ax.set_title('VAD Output (1: Speech, 0: No speech)')

# def init():
#     line.set_ydata(np.ma.array(x, mask=True))
#     return line,

# def update(num):
#     y[:-1] = y[1:]
#     y[-1] = vad_buffer[0]
#     line.set_ydata(y)
#     return line,

# ani = FuncAnimation(fig, update, frames=None, init_func=init, blit=True, interval=FRAME_DURATION*1000)

# # Start audio stream
# stream = sd.InputStream(callback=audio_callback, samplerate=RATE, channels=1, dtype=np.int16, blocksize=FRAME_SIZE)
# with stream:
#     plt.show()

