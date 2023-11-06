from .audio_recorder import AudioToTextRecorder
from .worker import Worker
from colorama import Fore, Back, Style
import colorama
import os
from .speaker import Speaker
from threading import Event as ThreadEvent
from .generator import Generator
from .TextToSpeach import TextToSpeach
from .config import aperture_science_logo

recorder_config = {
    'spinner': False,
    'model': 'tiny.en',
    'language': 'en',
    'silero_sensitivity': 0.3,
    'webrtc_sensitivity': 2,
    'post_speech_silence_duration': 0.2,
    'min_length_of_recording': 0,
    'min_gap_between_recordings': 0,
    'enable_realtime_transcription': True,
    'realtime_processing_pause': 0.05,
    'realtime_model_type': 'tiny.en',
    # 'on_realtime_transcription_stabilized': text_detected,
}

default_params = {

}


class SpeachToText(Worker):

  def __init__(self, stop_event=None, params=None, consumption_queue=None):
    super().__init__(default_params, stop_event, params, consumption_queue)
  
    colorama.init()
    self.full_sentences = []
    self.displayed_text = ""

    recorder_config['on_realtime_transcription_update'] = self.text_detected

    self.recorder = AudioToTextRecorder(**recorder_config)

    self.pause_event = ThreadEvent()
    self.resume_event = ThreadEvent()

    self.recorder.paused_event = self.pause_event
    self.recorder.resume_event = self.resume_event
  
  def clear_console(self):
    os.system('clear' if os.name == 'posix' else 'cls')
  

  def text_detected(self, text):
    # pass
    sentences_with_style = [
        f"{Fore.YELLOW + sentence + Style.RESET_ALL if i % 1 == 0 else Fore.CYAN + sentence + Style.RESET_ALL} "
        for i, sentence in enumerate(self.full_sentences)
    ]
    new_text = "".join(sentences_with_style).strip() + " " + text if len(sentences_with_style) > 0 else text

    if new_text != self.displayed_text:
        self.displayed_text = new_text
        self.clear_console()
        print(self.displayed_text, end="", flush=True)
        print(aperture_science_logo, end="", flush=True)
        

  def process_text(self, text):
      self.full_sentences.append(text)
      self.text_detected("")
      print()
      print("text published: ", text)
      self.publish_queue.put([text])


  def run(self):
    while not self.stop_event.is_set():
      self.recorder.text(self.process_text)

def main():
  print("Initializing RealtimeSTT test...")
  stop_event = ThreadEvent()
  speachToText = SpeachToText(stop_event=stop_event)
  speachToText.start()

  generator = Generator(speachToText.publish_queue,
                        stop_event=stop_event,
                        params={
                            'local_model_path': './models/luna-ai-llama2-uncensored.Q2_K.gguf',
                            'generator_type': 'chatgpt',
                            'max_tokens': 100
                        })


  # text to speach
  elabs = False

  tts = TextToSpeach(generator.publish_queue,
              stop_event=stop_event,
              params={'elabs': elabs})




  speaker = Speaker(consumption_queue=tts.publish_queue,
              recorder_pause_event=speachToText.recorder.paused_event,
              recorder_resume_event=speachToText.recorder.resume_event,
              stop_event=stop_event,
              params={'speed': 1.3}
              )
  
  generator.start()
  tts.start()
  speaker.start()


