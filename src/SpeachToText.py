from .audio_recorder import AudioToTextRecorder
from .worker import Worker
from colorama import Fore, Back, Style
import colorama
import os
from .speaker import Speaker
from threading import Event as ThreadEvent
from .generator import Generator
from .TextToSpeach import TextToSpeach
from .utils import split_into_sentences
from .config import aperture_science_logo, PARTICPANT_NAME

recorder_config = {
    'spinner': False,
    'model': 'base',
    # 'language': 'en',
    'silero_sensitivity': 0.3,
    'webrtc_sensitivity': 2,
    'post_speech_silence_duration': 0.2,
    'min_length_of_recording': 0,
    'min_gap_between_recordings': 0,
    'enable_realtime_transcription': True,
    'realtime_processing_pause': 0.05,
    'realtime_model_type': 'base',
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

    self.all_sentences = []
    self.last_sentences = ""
    self.unfinished_sentence = ""

    recorder_config['on_realtime_transcription_update'] = self.text_detected

    self.recorder = AudioToTextRecorder(**recorder_config)

    self.pause_event = ThreadEvent()
    self.resume_event = ThreadEvent()

    self.recorder.paused_event = self.pause_event
    self.recorder.resume_event = self.resume_event
  
  def clear_console(self):
    os.system('clear' if os.name == 'posix' else 'cls')
  

  def text_detected(self, text):
        

        sentences_with_style = [
            f"{Fore.YELLOW + sentence + Style.RESET_ALL if i % 2 == 0 else Fore.CYAN + sentence + Style.RESET_ALL} "
            for i, sentence in enumerate(self.full_sentences)
        ]
        
        # Display the last two full sentences when there is no new text
        if text == "":
            print("\r\033[K", end="", flush=True)  # Clear the current line
            # Join the last two sentences or the last sentence if there is only one
            last_sentences_display = "".join(sentences_with_style[-1:])
            print(f'[{PARTICPANT_NAME}]: {last_sentences_display}', end="", flush=True)

            

        else:
            # from our text, everytime we detect a new sentence we want to publish it to the queue

            # There is some new text, which may be an incomplete sentence
            joined_sentences = "".join(sentences_with_style).strip()
            new_text = f"{joined_sentences} {text}" if sentences_with_style else text
            incomplete_sentence = new_text[len(joined_sentences):].strip()

            

            # Display the incomplete sentence in a different style (e.g., default no color)
            # if incomplete_sentence:
            #     print("\r\033[K", end="", flush=True)  # Clear the current line
            #     print(f'[{PARTICPANT_NAME}]: {incomplete_sentence}', end="", flush=True)

        # Store the full displayed text including the incomplete sentence, if any
        self.displayed_text = new_text if 'new_text' in locals() else ""

  def process_text(self, text):
      self.full_sentences.append(text)
      self.text_detected("")
      self.publish_queue.put([text])


    # pass
    # sentences_with_style = [
    #     f"{Fore.YELLOW + sentence + Style.RESET_ALL if i % 1 == 0 else Fore.CYAN + sentence + Style.RESET_ALL} "
    #     for i, sentence in enumerate(self.full_sentences)
    # ]
    # if text == "":
    #     print("\r\033[K", end="", flush=True)
    #     # display the last full 2 sentences using join
    #     print(f'[{PARTICPANT_NAME}]: {"".join(sentences_with_style[-2:])}', end="", flush=True)

       

    # joined_sentences = "".join(sentences_with_style).strip()
    # new_text = joined_sentences + " " + text if len(sentences_with_style) > 0 else text

    # #incomplete text is all the text that is not a full sentence
    # incomplete_sentence = new_text[len(joined_sentences):]

    # if len(incomplete_sentence) > 0:
    #     # self.clear_console()
    #     # reset cursor to left
    #     # clear the current line
    #     print("\r\033[K", end="", flush=True)
    #     # display everything in the new sentence
    #     print(f'[{PARTICPANT_NAME}]: {incomplete_sentence}', end="", flush=True)

    # self.displayed_text = new_text

        

  


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


