import openai
from .config import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY


def get_response(prompt):
    response = openai.chat.completion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message['content'].strip()

# def get_response(prompt):
#     openai.Completion.create
#     response = openai.Completion.create(
#         model="gpt-3.5-turbo-instruct",
#         prompt=prompt,
#         temperature=0.9,
#         max_tokens=150,
#         top_p=1,
#         frequency_penalty=0,
#         presence_penalty=0,
#         stop=["\n", " ME:", " YOU:"]
#     )
#     return response.choices[0].text.strip()