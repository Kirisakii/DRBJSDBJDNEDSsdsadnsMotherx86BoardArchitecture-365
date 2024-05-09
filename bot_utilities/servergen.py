from openai import AsyncOpenAI
import os


openai_client = AsyncOpenAI(
    api_key = os.getenv('CHIMERA_GPT_KEY'),
    base_url = "https://api.naga.ac/v1"
)

async def generate_response(instructions, history):
    messages = [
            {"role": "system", "name": "instructions", "content": instructions},
            *history,
        ]
    response = await openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    message = response.choices[0].message.content
    return message