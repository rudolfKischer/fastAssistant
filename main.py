from src.assistant import main as assistant_main
from src.generator import main as generator_main
from src.speaker import main as speaker_main
from src.SpeachToText import main as stt_test_main
from src.TextToSpeach import main as tts_test_main

def main():
    assistant_main()
    # generator_main()
    # speaker_main()
    # stt_test_main()
    # tts_test_main()

if __name__ == "__main__":
    main()
