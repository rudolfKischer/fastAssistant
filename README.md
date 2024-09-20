# Fast Assistant

- This is a simple conversational bot that you can chat with

# Plan

- The Goal is to make an assistant that can respond in a converstional manner, that knows when it should talk
- The long term goal is to incrementally add new capabilities over time
 
# Setup

- Create a virtual environment
    - `python3 -m venv venv`
- Activate the virtual environment
    - `source venv/bin/activate`
- Install the requirements
    - `pip install -r requirements.txt`
- Run the program
    - `python3 main.py`
- Download the llm model from hugging face 
    - repo: `TheBloke/orca_mini_3B-GGML`
    - model file: `orca-mini-3b.ggmlv3.q4_0.bin`
    - put it in a `models` folder within this repo


# Planned Features

- Faster Text Generation time
- Inference optimization on with vllm
- Realistic Text to Speach Using 11 labs
- Better transcriptions
    - Using a better a bigger STT
    - continous STT merge from different qualities
    - STT that can handle multiple speakers
    - Take a look at whisper diarise
- The ability for others to interrupt while speaking
- The ability for it to interrupt while speaking
     - Maybe have some continous innner and outer monologue
     - This way the LLM can decide when it thinks its a good time to talk
- Web crawling agent, so it can search things up
- Specialized API LLM so it can use tools, (look at Gorrilla LLM)
- Access to cli to run code and commands
- GUI
      - Could be something simple just to show when it is listening and when its talking
      - Could be a realistic avatar that moves its mouth when it talks (Look at meta human)
- specialized coding llm it can call on (codellama or wizard coder)
- Mechanism for having process intensize tasks run on a server that it calls out to


# NOTES:

- Check the microphone input system settings:
- If its to sensitive, it the system might think your always talking which makes it behave weirdly
