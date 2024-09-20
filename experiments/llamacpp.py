from llama_cpp import Llama #import for GGML models
llm = Llama(model_path="./models/orca-mini-3b.ggmlv3.q4_0.bin", n_ctx=512, n_batch=32, verbose=False)
instruction = input("User: ")
# put together the instruction in the prompt template for Orca models
system = 'You are an AI assistant that follows instruction extremely well. Help as much as you can.'
prompt = f"### System:\n{system}\n\n### User:\n{instruction}\n\n### Response:\n"
output = llm(prompt,temperature  = 0.7,max_tokens=512,top_k=20, top_p=0.9,
                    repeat_penalty=1.15)
res = output['choices'][0]['text'].strip()
print('Orca3b: '+ res)