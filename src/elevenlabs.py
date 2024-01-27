import requests
from urllib.parse import urljoin, urlencode
from .config import ELAB_API_KEY

CHUNK_SIZE = 1024
base_url = "https://api.elevenlabs.io/"

# default_voice_id = "21m00Tcm4TlvDq8ikWAM"
default_voice_id = "EXAVITQu4vr4xnSDxMaL"


def elab_request(endpoint, data=None, headers=None, query_params=None):
      if headers is None:
            headers = {
              "Accept": "audio/mpeg",
              "Content-Type": "application/json",
              "xi-api-key": ELAB_API_KEY
            }
      url = urljoin(base_url, endpoint)
      if query_params is not None:
          url = f'{url}?{urlencode(query_params)}'
      # print(url)
      response = requests.post(url, json=data, headers=headers, stream=True)
      # print(response)
      return response


def tts_request(text, voice_id=default_voice_id, audio_format="audio/mpeg"):
      data = {
        "text": text,
        # "model_id": "eleven_monolingual_v1",
        # "model_id": "eleven_multilingual_v2",
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
          "stability": 0.9,
          "similarity_boost": 0.9
        }
      }
      query_params = {
          'optimize_streaming_latency': 4
      }
      response = elab_request(f"v1/text-to-speech/{voice_id}", data=data, query_params=query_params)
      return response

def tts(text, output_file_path):
      try:
          with open(output_file_path, "wb") as f:
            response = tts_request(text)
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
          return True
      except Exception as e:
          print(e)
          return False

def main():
      text = "Bonjour, je m'appelle Eleven, et je suis une voix de synthèse."
      output_file_path = "output.mp3"
      tts(text, output_file_path)

