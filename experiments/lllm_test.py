# from ctransformers import AutoModelForCausalLM
import time
# import llama_cpp

# # Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
# llm = AutoModelForCausalLM.from_pretrained("TheBloke/Mistral-7B-Instruct-v0.1-GGUF", model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf", model_type="mistral", gpu_layers=0)

# print("generating...")
# start_time = time.time()
# print(llm("AI is going to",max_new_tokens=10, threads=4))
# print("time taken: ", time.time() - start_time)

from llama_cpp import Llama

llm = Llama(model_path="./models/q4_0-orca-mini-3b.gguf", n_gpu_layers=100, n_ctx=512, n_batch=32, verbose=False)
# llm = Llama(model_path="./models/mistral-7b-instruct-v0.1.Q2_K.gguf", n_gpu_layers=500, n_ctx=512, n_batch=32, verbose=False)
start_time = time.time()
output = llm("Q: Name the planets in the solar system? A: ", max_tokens=22, stop=["Q:", "\n"])
print("time taken: ", time.time() - start_time)
print(output['choices'][0]['text'])