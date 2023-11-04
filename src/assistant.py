import threading
from .record import AudioRecorder
from .transcriber import Transcriber
from .generator import Generator
from .speaker import Speaker
from .vad import VoiceDetector


class Assistant():
    """
    The Assitant is composed of four threads:
    - AudioRecorder: Records audio from the microphone and publishes it to the Transcriber
    - Transcriber: Transcribes the audio and publishes it to the Generator
    - Generator: Generates a response and publishes it to the Speaker
    - Speaker: Speaks the response
    """    

    def __init__(self):
        
        local = True


        if local:
            elabs = False
            generator_type = 'llamacpp'
        else:
            elabs = True
            generator_type = 'chatgpt'
        


        self.stop_event = threading.Event()

        self.recorder = AudioRecorder(stop_event=self.stop_event)#params={'seconds': min_time})
        self.vad = VoiceDetector(self.recorder.publish_queue, stop_event=self.stop_event)
        self.transcriber = Transcriber(self.vad.publish_queue,
                                      stop_event=self.stop_event,
                                      audio_pause_event=self.recorder.pause_event,
                                      audio_resume_event=self.recorder.resume_event)
        self.generator = Generator(self.transcriber.publish_queues["transcription"], 
                                   stop_event=self.stop_event, 
                                   params={
                                       'max_tokens': 50,
                                       'generator_type': generator_type
                                    })
        self.speaker = Speaker(self.generator.publish_queue, 
                          recorder_pause_event=self.recorder.pause_event, 
                          recorder_resume_event=self.recorder.resume_event,
                          stop_event=self.stop_event,
                          params={'elabs': elabs},
                          )
    
    def start(self):
        print("Starting threads...")
        self.recorder.start()
        self.vad.start()
        self.transcriber.start()
        self.generator.start()
        self.speaker.start()
        print("Started.")

    def join(self):
        try:
            self.recorder.join()
            self.transcriber.join()
            self.generator.join()
            self.speaker.join()
            self.vad.join()
            print("Joined Threads.")
        except KeyboardInterrupt:
            print("Stopping threads...")
            self.stop_event.set()
            print("Stopped.")

def main():
    assistant = Assistant()
    assistant.start()
    assistant.join()

if __name__ == "__main__":
    main()
        
