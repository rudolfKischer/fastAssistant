from transformers import AutoProcessor, BarkModel

import os

# os.environ["CUDA_VISIBLE_DEVICES"] = ""
# os.environ["SUNO_OFFLOAD_CPU"] = "True"
# os.environ["SUNO_USE_SMALL_MODELS"] = "True"

processor = AutoProcessor.from_pretrained("suno/bark")
model = BarkModel.from_pretrained("suno/bark")

voice_preset = "v2/en_speaker_6"

inputs = processor("Hello, There are alot of - um things I like to do [clears throat]", voice_preset=voice_preset)

print("starting")
audio_array = model.generate(**inputs)
print("ended")

audio_array = audio_array.cpu().numpy().squeeze()

import scipy

sample_rate = model.generation_config.sample_rate
scipy.io.wavfile.write("bark_out.wav", rate=sample_rate, data=audio_array)