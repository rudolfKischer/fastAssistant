from .chatgpt import get_response
from llama_cpp import Llama
import openai
from .config import OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY

class Generator():
    
    def set_params(self, params, default_params):
        for key, value in default_params.items():
            setattr(self, key, value)
        if params:
            for key, value in params.items():
                setattr(self, key, value)

    def __init__(self) -> None:
        pass
    
    def generate(self, prompt):
        pass
    


class ChatGPTGenerator(Generator):
    default_params = {
        "model": "gpt-3.5-turbo-instruct",
        "temperature": 0.9,
        "max_tokens": 150,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop_strings": ["\n"]
    }

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.set_params(kwargs, self.default_params)
    
    def generate(self, prompt):
        openai.Completion.create
        response = openai.Completion.create(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop=self.stop_strings
        )
        return response.choices[0].text.strip()
    



class LlamaCPPGenerator(Generator):
    
    default_params = {
        "model_path": "./models/q4_0-orca-mini-3b.gguf",
        "n_gpu_layers": 100,
        "stop_strings": ['\n'],
        "max_context_length": 512
    }

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.set_params(kwargs, self.default_params)
        self.llm = Llama(model_path=self.model_path,
                         n_gpu_layers=self.n_gpu_layers,
                         verbose=False,
                         n_ctx=self.max_context_length)
    
    def generate(self, prompt):
        output = self.llm(prompt,
                          max_tokens=self.max_tokens,
                          stop=self.stop_strings, 
                          )
        return output['choices'][0]['text']



generator_names = {
    'chatgpt': ChatGPTGenerator,
    'llamacpp': LlamaCPPGenerator
}