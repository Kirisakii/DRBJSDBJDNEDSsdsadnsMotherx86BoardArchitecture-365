import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import aiohttp
from bs4 import BeautifulSoup


# FunOther Class
class FunOther(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # dadjoke
    @app_commands.command(name = "dadjoke", description = "Get a random dad joke.")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def dadjoke(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://icanhazdadjoke.com/slack") as response:
                data = await response.json()
                joke = data["attachments"][0]["text"]
            await interaction.response.send_message(joke)

    # dog api
    @app_commands.command(name = "dog", description = "Get a random dog image.")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def dog(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get("https://random.dog/woof.json") as response:
                    data = await response.json()
                    dog_url = data["url"]
                    if ".mp4" in dog_url: continue
                    em = discord.Embed(colour = 0x2F3136)
                    em.set_image(url = dog_url)
                await interaction.response.send_message(embed = em)
                break

    # cat api
    @app_commands.command(name = "cat", description = "Get a random cat image.")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def cat(self, interaction: discord.Interaction):
        cat_tags = ["cute", "says/hello", "cute/says/hello"]
        tag = random.choice(cat_tags)
        em = discord.Embed(colour = 0x2F3136)
        em.set_image(url = f"https://cataas.com/cat/{tag}")
        await interaction.response.send_message(embed = em)

    #wyr command
    @app_commands.command(name = "wyr", description = "Would you rather...")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def wyr(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://would-you-rather-api.abaanshanid.repl.co/") as r:
                response = await r.json()
        e = discord.Embed(title=response["data"], colour = 0x2F3136)
        await interaction.followup.send("Would you rather...")
        msg = await interaction.channel.send(embed = e)
        await msg.add_reaction("🇦")
        await msg.add_reaction("🇧")
        

    #emojify
    @app_commands.command(name = "emojify", description = "Convert your words to emojis!")
    @app_commands.describe(text = "Text you want to transform into emojis.")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def emojify(self, interaction: discord.Interaction, text: str):
        emojis = []
        for s in text.lower():
            if s.isdecimal():
                num2emo = {"0":"zero" , "1":"one" , "2":"two" , "3":"three" , "4":"four" ,
                          "5":"five" , "6":"six" , "7":"seven" , "8":"eight" , "9":"nine"}
                emojis.append(f":{num2emo.get(s)}:")
            elif s.isalpha():
                emojis.append(f":regional_indicator_{s}:")
            else:
                emojis.append(s)
        await interaction.response.send_message(" ".join(emojis))

    #choose command
    @app_commands.command(name = "choose", description = "Chooses. (maximum 5 choices.)")
    @app_commands.describe(choice1 = "Choice 1.", choice2 = "Choice 2.", choice3 = "Choice 3.", choice4 = "Choice 4.", choice5 = "Choice 5.")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def choose(self, interaction: discord.Interaction, choice1: str, choice2: str, choice3: str = None, choice4: str = None, choice5: str = None):
        if choice3 == None:
            opt = [choice1,choice2]
            optext = f"{choice1} and {choice2}"
        elif choice4 == None:
            opt = [choice1,choice2,choice3]
            optext = f"{choice1}, {choice2} and {choice3}"
        elif choice5 == None:
            opt = [choice1,choice2,choice3,choice4]
            optext = f"{choice1}, {choice2}, {choice3} and {choice4}"
        else:
            opt = [choice1, choice2, choice3, choice4, choice5]
            optext = f"{choice1}, {choice2}, {choice3}, {choice4} and {choice5}"
        await interaction.response.send_message(f"Choosing from: {optext}.")
        await asyncio.sleep(0.5)
        await interaction.edit_original_response(content = f"Choosing from: {optext}..")
        await asyncio.sleep(0.5)
        await interaction.edit_original_response(content = f"Choosing from: {optext}...")
        await asyncio.sleep(0.5)
        await interaction.edit_original_response(content = f"Choosing from: {optext}.")
        await asyncio.sleep(0.5)
        await interaction.edit_original_response(content = f"Choosing from: {optext}..")
        await asyncio.sleep(0.5)
        await interaction.edit_original_response(content = f"Choosing from: {optext}...")
        await asyncio.sleep(0.5)
        await interaction.followup.send(content = f"{random.choice(opt)}")

    #reverse
    @app_commands.command(name = "reverse", description = "Reverses your words.")
    @app_commands.describe(your_words = "Words to reverse.")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def reverse(self, interaction: discord.Interaction, your_words: str):
        t_rev = your_words[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await interaction.response.send_message(f"🔁 {t_rev}")

    #timer
    @app_commands.command(name = "timer", description = "A stopwatch for you.")
    @app_commands.describe(time = "The time you want to set.")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def timer(self, interaction: discord.Interaction, time: str):
        get_time = {
        "s": 1, "m": 60, "h": 3600, "d": 86400,
        "w": 604800, "mo": 2592000, "y": 31104000 }
        timer = time
        a = time[-1]
        b = get_time.get(a)
        c = time[:-1]
        try: int(c)
        except: return await interaction.response.send_message("> Type time and time unit [s,m,h,d,w,mo,y] correctly.", ephemeral = True)
        try:
            sleep = int(b) * int(c)
            await interaction.response.send_message(f"> Timer set to {timer}.", ephemeral = True)
        except: return await interaction.response.send_message("> Type time and time unit [s,m,h,d,w,mo,y] correctly.", ephemeral = True)
        await asyncio.sleep(sleep)
        await interaction.response.send_message("**Time over**")
        member_dm = await interaction.user.create_dm()
        #await channel.send("**Time over**")
        emb = discord.Embed(title = "**Time over**", description = f"> Your Timer '{timer}' has been ended", color = discord.Colour.random())
        await member_dm.send(embed = emb)


    @app_commands.command(name = "advice", description = "Trust me you'll need it ;)..")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def advice(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
                async with session.get("https://api.adviceslip.com/advice") as response:
                    data = await response.json(content_type = "text/html")
                    advice = data["slip"]["advice"]
        await interaction.response.send_message(advice)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FunOther(bot))