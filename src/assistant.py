import threading
from .SpeachToText import SpeachToText
from .TextToSpeach import TextToSpeach
from .generator import Generator
from .speaker import Speaker
from .keyboard import Keyboard


from .config import LOCAL_ONLY, aperture_science_logo


class Assistant():
    """
    The Assitant is composed of four threads:
    - AudioRecorder: Records audio from the microphone and publishes it to the Transcriber
    - Transcriber: Transcribes the audio and publishes it to the Generator
    - Generator: Generates a response and publishes it to the Speaker
    - Speaker: Speaks the response
    """    

    def __init__(self):
        
        local = False


        if local:
            elabs = False
            generator_type = 'llamacpp'
            # generator_type = 'chatgpt'
            speach_speed = 1.38
        else:
            elabs = True
            generator_type = 'chatgpt'
            speach_speed = 1.0
        


        self.stop_event = threading.Event()
        speachToText = SpeachToText(stop_event=self.stop_event)

        key_board = Keyboard(stop_event=self.stop_event,
                             publish_queue=speachToText.publish_queue)


        generator = Generator(speachToText.publish_queue,
                          stop_event=self.stop_event,
                          params={
                              'generator_type': generator_type,
                              'max_tokens': 150
                          })
        tts = TextToSpeach(generator.publish_queue,
                    stop_event=self.stop_event,
                    params={'elabs': elabs})
        speaker = Speaker(tts.publish_queue,
                    recorder_pause_event=speachToText.recorder.paused_event,
                    recorder_resume_event=speachToText.recorder.resume_event,
                    stop_event=self.stop_event,
                    params={'speed': speach_speed}
                    )
        

        
        
        self.threads = [speachToText, key_board, generator, tts, speaker]
    
    def start(self):
        print("Starting threads...")
        for thread in self.threads:
            thread.start()
        print("Started.")
        # clear console
        print("\033c", end="")
        print(f'\033[33m{aperture_science_logo}\033[0m')
        # put "hi" on generator queue

    def join(self):
        try:
            for thread in self.threads:
                thread.join()
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
        
