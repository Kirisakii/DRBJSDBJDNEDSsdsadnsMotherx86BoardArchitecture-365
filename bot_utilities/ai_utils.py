import aiohttp
import io
import time
import os
import random
import json
from langdetect import detect
from gtts import gTTS
from urllib.parse import quote
from bot_utilities.config_loader import load_current_language, config
from openai import AsyncOpenAI
from duckduckgo_search import AsyncDDGS
from dotenv import load_dotenv

load_dotenv()
# $Rmn@9229288716!Rmk
current_language = load_current_language()
internet_access = config['INTERNET_ACCESS']

client = AsyncOpenAI(
    base_url=config['API_BASE_URL'],
    api_key=os.environ.get("API_KEY"),
)

async def generate_response(instructions, history, command_request=None, user_name=None, user_mention=None):
    messages = [
        {"role": "system", "name": "instructions", "content": instructions},
        *history,
    ]
    if user_name:
        messages.append({"role": "user", "name": "username", "content": f"user_name: {user_name}"})
    if user_mention:
        messages.append({"role": "user", "name": "user_mention", "content": f"user_id : {user_mention} [Ignore, only required for blacklisting or mentioning purposes.]"})

    if command_request:
        messages.append({"role": "system", "name": "command_info", "content": command_request})

    # Call the AI API with the constructed messages
    try:
        response = await client.chat.completions.create(
            model=config['MODEL_ID'],
            messages=messages,
            tools=[],  # Assuming no tools are needed for this example
            tool_choice="auto",
        )
        response_message = response.choices[0].message.content
        return response_message
    except Exception as e:
        error_message = str(e)
        print(f"Failed to generate response: {error_message}")

        # Extract and format the 'failed_generation' content if present
        if "failed_generation" in error_message:
            start_idx = error_message.find("failed_generation") + len("failed_generation") + 3
            end_idx = error_message.find("}'", start_idx)
            failed_generation_content = error_message[start_idx:end_idx]
            # Clean up and format the response
            formatted_response = failed_generation_content.replace("\\n", "\n").strip()
            # Remove the unwanted "or more details" part
            unwanted_substring = """or more details.", 'type': 'invalid_request_error', 'code': 'tool_use_failed', 'failed_generation': '"""
            if unwanted_substring in formatted_response:
                formatted_response = formatted_response.replace(unwanted_substring, "").strip()
            return formatted_response
        return "An error occurred while generating the response. Please try again later."
    return response_message.content

async def duckduckgotool(query) -> str:
    if config['INTERNET_ACCESS']:
        return "internet access has been disabled by user"
    blob = ''
    results = await AsyncDDGS(proxy=None).text(query, max_results=6)
    try:
        for index, result in enumerate(results[:6]):  # Limiting to 6 results
            blob += f'[{index}] Title : {result["title"]}\nSnippet : {result["body"]}\n\n\n Provide a cohesive response base on provided Search results'
    except Exception as e:
        blob += f"Search error: {e}\n"
    return blob


async def poly_image_gen(session, prompt):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    async with session.get(image_url) as response:
        image_data = await response.read()
        return io.BytesIO(image_data)

async def generate_image_prodia(prompt, model, sampler, seed, neg):
    print("\033[1;32m(Prodia) Creating image for :\033[0m", prompt)
    start_time = time.time()
    async def create_job(prompt, model, sampler, seed, neg):
        if neg is None:
            negative = "(nsfw:1.5),verybadimagenegative_v1.3, ng_deepnegative_v1_75t, (ugly face:0.8),cross-eyed,sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, bad anatomy, DeepNegative, facing away, tilted head, {Multiple people}, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worstquality, low quality, normal quality, jpegartifacts, signature, watermark, username, blurry, bad feet, cropped, poorly drawn hands, poorly drawn face, mutation, deformed, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, extra fingers, fewer digits, extra limbs, extra arms,extra legs, malformed limbs, fused fingers, too many fingers, long neck, cross-eyed,mutated hands, polar lowres, bad body, bad proportions, gross proportions, text, error, missing fingers, missing arms, missing legs, extra digit, extra arms, extra leg, extra foot, repeating hair, nsfw, [[[[[bad-artist-anime, sketch by bad-artist]]]]], [[[mutation, lowres, bad hands, [text, signature, watermark, username], blurry, monochrome, grayscale, realistic, simple background, limited palette]]], close-up, (swimsuit, cleavage, armpits, ass, navel, cleavage cutout), (forehead jewel:1.2), (forehead mark:1.5), (bad and mutated hands:1.3), (worst quality:2.0), (low quality:2.0), (blurry:2.0), multiple limbs, bad anatomy, (interlocked fingers:1.2),(interlocked leg:1.2), Ugly Fingers, (extra digit and hands and fingers and legs and arms:1.4), crown braid, (deformed fingers:1.2), (long fingers:1.2)"
        else:
            negative = neg
        url = 'https://api.prodia.com/generate'
        params = {
            'new': 'true',
            'prompt': f'{quote(prompt)}',
            'model': model,
            'negative_prompt': f"{negative}",
            'steps': '100',
            'cfg': '9.5',
            'seed': f'{seed}',
            'sampler': sampler,
            'upscale': 'True',
            'aspect_ratio': 'square'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return data['job']

    job_id = await create_job(prompt, model, sampler, seed, neg)
    url = f'https://api.prodia.com/job/{job_id}'
    headers = {
        'authority': 'api.prodia.com',
        'accept': '*/*',
    }

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers) as response:
                json = await response.json()
                if json['status'] == 'succeeded':
                    async with session.get(f'https://images.prodia.xyz/{job_id}.png?download=1', headers=headers) as response:
                        content = await response.content.read()
                        img_file_obj = io.BytesIO(content)
                        duration = time.time() - start_time
                        print(f"\033[1;34m(Prodia) Finished image creation\n\033[0mJob id : {job_id}  Prompt : ", prompt, "in", duration, "seconds.")
                        return img_file_obj

async def text_to_speech(text):
    return None




# def search_documentation(command_name):
#     with open('documentation.txt', 'r', encoding='utf-8') as file:
#         content = file.read()

#     # Split the document into sections
#     commands = content.split('[Commands and how they work!]:')[1].split('\n\n')
#     for command in commands:
#         if command_name.lower() in command.lower():
#             return command  # Return the command details
#     return "Command not found."


# @commands.Cog.listener()
# async def on_message(self, message):
#     if message.author.bot:
#         return  # Ignore bot messages

#     # Example command trigger
#     if message.content.startswith('!help'):
#         command_name = message.content.split(' ')[1] if len(message.content.split(' ')) > 1 else ''
#         if command_name:
#             command_info = search_documentation(command_name)
#             await message.channel.send(command_info)
#         else:
#             await message.channel.send("Please specify a command to get help on.")