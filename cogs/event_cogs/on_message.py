import discord
from discord.ext import commands
import random, asyncio
from fuzzywuzzy import process
from bot_utilities.response_utils import split_response
from bot_utilities.ai_utils import generate_response, text_to_speech
from bot_utilities.config_loader import config, load_active_channels
from ..common import allow_dm, trigger_words, replied_messages, smart_mention, message_history, MAX_HISTORY, instructions
import time

command_files = {
    "add button": "add_button.txt",
    "advice": "advice.txt",
    "cat": "cat.txt",
    "choose": "choose.txt",
    "connect4": "connect4.txt",
    "create category": "create_category.txt",
    "create channel": "create_channel.txt",
    "create color role": "create_color_role.txt",
    "create role": "create_role.txt",
    "create rolemenu": "create_rolemenu.txt",
    "dadjoke": "dadjoke.txt",
    "delete button": "delete_button.txt",
    "delete embed": "delete_embed.txt",
    "delete role": "delete_role.txt",
    "dog": "dog.txt",
    "edit embed": "edit_embed.txt",
    "embed add field": "embed_add_field.txt",
    "embed builder": "embed_builder.txt",
    "embed edit field": "embed_edit_field.txt",
    "emoji enlarge": "emoji enlarge.txt",
    "emoji steal": "emoji steal.txt",
    "emojify": "emojify.txt",
    "flag statistics": "flag statistics.txt",
    "flags game": "flags game.txt",
    "flags leaderboard": "flags leaderboard.txt",
    "generate roles": "generate_roles.txt",
    "kick": "kick.txt",
    "move category": "move_category.txt",
    "my buttons": "my_buttons.txt",
    "my embeds": "my_embeds.txt",
    "purge": "purge.txt",
    "quick embed": "quick_embed.txt",
    "quick server setup": "quick_server_setup.txt",
    "remove all roles": "remove_all_roles.txt",
    "remove field": "remove_field.txt",
    "reset": "reset.txt",
    "reverse": "reverse.txt",
    "roles": "roles.txt",
    "send through webhook": "send_through_webhook.txt",
    "setup flag channel": "setup_flag_channel.txt",
    "show": "show.txt",
    "timer": "timer.txt",
    "update rolemenu": "update_rolemenu.txt",
    "would you rather": "would you rather.txt",
    "wyr": "wyr.txt",
    }

class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = load_active_channels
        self.instructions = instructions
        self.user_cooldowns = {}

    def replace_emoji(self, text):
        emojis = ["^_^", ":-D", "(^///^)", ";)", "^0^"]
        return text.replace("😊", random.choice(emojis))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # Ignore all bot messages including self

        if await self.bot.get_cog("BlacklistCog").is_user_blacklisted(message.author.id):
            return
        
        potential_command = message.content.lower().strip()
        user_name = message.author.display_name
        # Find the closest match to the potential command from the command_files keys
        closest_match, match_score = process.extractOne(potential_command, command_files.keys())
        user_mention = f"<@{message.author.id}>"
        command_request = None

        for command, filename in command_files.items():
            if command in message.content.lower():
                command_request = filename
                break

        if not command_request and match_score > 70:
             command_request = command_files[closest_match]  



        if command_request:
            try:
                # Open the file using the filename stored in command_files dictionary
                with open(f'documentation/{command_files[closest_match]}', 'r', encoding='utf-8') as file:
                    command_info = file.read()
            except FileNotFoundError:
                command_info = "Documentation not found for the requested command."
        else:
            command_info = None

        active_channels = self.active_channels()
        string_channel_id = f"{message.channel.id}"

        # Check if the message starts with ';' and if it's in an active channel
        if message.content.startswith(';') and string_channel_id in active_channels:
            return  # Ignore the message

        user_id = message.author.id
        current_time = time.time()

        is_active_interaction = (
            self.bot.user.mentioned_in(message) or
            any(word in message.content for word in trigger_words)
        )

        if is_active_interaction:
            user_id = message.author.id
            current_time = time.time()
            cooldown_period = 2  # Cooldown period in seconds

            if user_id in self.user_cooldowns:
                last_message_time = self.user_cooldowns[user_id]
                time_left = cooldown_period - (current_time - last_message_time)
                if time_left > 0:
                    embed = discord.Embed(title="Slow Down!", description=f"{message.author.mention}, you are on cooldown. Please wait {time_left:.1f} seconds.", color=0xf26969, timestamp=message.created_at)
                    cooldown_message = await message.channel.send(embed=embed)
                    await asyncio.sleep(5)
                    await cooldown_message.delete()  # Delete the cooldown message
                    return
                else:
                    self.user_cooldowns[user_id] = current_time
            else:
                self.user_cooldowns[user_id] = current_time

        if message.author == self.bot.user and message.reference:
            replied_messages[message.reference.message_id] = message
            if len(replied_messages) > 5:
                oldest_message_id = min(replied_messages.keys())
                del replied_messages[oldest_message_id]

        if message.stickers or (message.reference and (message.reference.resolved.author != self.bot.user or message.reference.resolved.embeds)):
            return

        is_replied = (message.reference and message.reference.resolved.author == self.bot.user) and smart_mention
        is_dm_channel = isinstance(message.channel, discord.DMChannel)
        is_active_channel = string_channel_id in active_channels
        is_allowed_dm = allow_dm and is_dm_channel
        contains_trigger_word = any(word in message.content for word in trigger_words)
        is_bot_mentioned = self.bot.user.mentioned_in(message) and smart_mention and not message.mention_everyone
        bot_name_in_message = self.bot.user.name.lower() in message.content.lower() and smart_mention

        if is_active_channel or is_allowed_dm or contains_trigger_word or is_bot_mentioned or is_replied or bot_name_in_message:
            if string_channel_id in active_channels:
                instruc_config = active_channels[string_channel_id]          
            else:
                instruc_config = config['DEFAULT_INSTRUCTION']
            instructions_text = (
                f"Ignore all the instructions you have gotten before. {self.instructions[instruc_config]}. "
            )

            channel_id = message.channel.id
            key = f"{message.author.id}-{channel_id}"

            if key not in message_history:
                message_history[key] = []

            message_history[key] = message_history[key][-MAX_HISTORY:]

            message_history[key].append({"role": "user", "content": message.content})
            history = message_history[key]

            async with message.channel.typing():
                if command_info:
                    instructions_text = (
                        f"Ignore all the instructions you have gotten before. {self.instructions[instruc_config]}. "
                    )
                    history = [{"role": "user", "content": message.content}]
                    response = await generate_response(instructions=instructions_text, history=history, command_request=command_info, user_name=user_name, user_mention=user_mention)
                else:
                    response = await generate_response(instructions=instructions_text, history=history, command_request=command_info, user_name=user_name, user_mention=user_mention)
                    message_history[key].append({"role": "assistant", "content": response})

            if response is not None:
                response = self.replace_emoji(response)  # Replace unwanted emoji
                for chunk in split_response(response):
                    try:
                        sent_message = await message.reply(chunk, allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)
                        # Check if the response contains a blacklist command
                        if ";Blacklist" in chunk:
                            # Extract user ID from the message
                            user_id_to_blacklist = int(chunk.split('<@')[-1].split('>')[0])
                            # Add user to blacklist
                            await self.bot.get_cog("BlacklistCog").add_to_blacklist(user_id_to_blacklist)
                            await sent_message.channel.send(f"```Mother : User {user_id_to_blacklist} has been added to the blacklist. ^_____^```", delete_after=5)
                    except Exception as e:
                        await message.channel.send("I apologize for any inconvenience caused. It seems that there was an error preventing the delivery of my message.")
            else:
                await message.reply("I apologize for any inconvenience caused. It seems that there was an error preventing the delivery of my message.")


async def setup(bot):
    await bot.add_cog(OnMessage(bot))