import asyncio
import datetime
import discord
import json
from discord.ext import commands
from bot_utilities.config_loader import config
from ..common import presences_disabled, current_language, presences
import kaomoji
from colorama import init, Fore, Style
import threading
import curses
from asciimantics import curses_wrapper 
from asciimantics import startup_animation

init(autoreset=True)  # Initialize colorama to auto-reset styles

class OnReady(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def read_fences_painted(self):
        try:
            with open('current.fences.json', 'r') as file:
                data = json.load(file)
                return data.get('fences_painted', 276)
        except FileNotFoundError:
            return 276
        except json.JSONDecodeError:
            return 276

    def update_fences_painted(self, count):
        with open('current.fences.json', 'w') as file:
            json.dump({'fences_painted': count}, file)

    @commands.Cog.listener()
    async def on_ready(self):
        mother_ascii_art = """

        ▪   ▐ ▄ ▪  ▄▄▄▄▄▪   ▄▄▄· ▄▄▌  ▪  ·▄▄▄▄•▪   ▐ ▄  ▄▄ •     • ▌ ▄ ·.       ▄▄▄▄▄ ▄ .▄▄▄▄ .▄▄▄  
        ██ •█▌▐███ •██  ██ ▐█ ▀█ ██•  ██ ▪▀·.█▌██ •█▌▐█▐█ ▀ ▪    ·██ ▐███▪▪     •██  ██▪▐█▀▄.▀·▀▄ █·
        ▐█·▐█▐▐▌▐█· ▐█.▪▐█·▄█▀▀█ ██▪  ▐█·▄█▀▀▀•▐█·▐█▐▐▌▄█ ▀█▄    ▐█ ▌▐▌▐█· ▄█▀▄  ▐█.▪██▀▐█▐▀▀▪▄▐▀▀▄ 
        ▐█▌██▐█▌▐█▌ ▐█▌·▐█▌▐█ ▪▐▌▐█▌▐▌▐█▌█▌▪▄█▀▐█▌██▐█▌▐█▄▪▐█    ██ ██▌▐█▌▐█▌.▐▌ ▐█▌·██▌▐▀▐█▄▄▌▐█•█▌
        ▀▀▀▀▀ █▪▀▀▀ ▀▀▀ ▀▀▀ ▀  ▀ .▀▀▀ ▀▀▀·▀▀▀ •▀▀▀▀▀ █▪·▀▀▀▀     ▀▀  █▪▀▀▀ ▀█▄▀▪ ▀▀▀ ▀▀▀ · ▀▀▀ .▀  ▀
                
                """
        print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + mother_ascii_art)
        print(Fore.CYAN + Style.BRIGHT + f"(^///^) {self.bot.user} aka {self.bot.user.name} has connected to Discord!")
        invite_link = discord.utils.oauth_url(self.bot.user.id, permissions=discord.Permissions(administrator=True), scopes=("bot", "applications.commands"))
        print(Fore.GREEN + f"Invite link: {invite_link}")

        if presences_disabled:
            return

        # Start the animation in a separate thread
        animation_thread = threading.Thread(target=curses.wrapper, args=(curses_wrapper,))
        animation_thread.start()

        fences_painted = self.read_fences_painted()
        while not self.bot.is_closed():
            start_time = datetime.datetime.utcnow()
            try:
                game_activity = discord.Activity(
                    type=discord.ActivityType.playing,
                    application_id=1116981623003561994,
                    name=f"Available Maybe",
                    state=f"https://discord.gg/ncXQSvwPre",
                    small_image_url="https://cdn.discordapp.com/avatars/1116981623003561994/d5b54d0d03e37295933f03724df56de7.webp?size=1024&format=webp&width=0&height=230",
                    small_image_text="Painting",
                    details="Questing through the realm 🌍",
                    url="https://twitch.tv/discord",
                    start=start_time,
                    party={"id": "party1234", "size": [1, 5]},
                    buttons=[{"label": "Join Adventure 🚀", "url": "https://discord.gg/tJKWgqJ"}]
                )
                await self.bot.change_presence(status=discord.Status.idle, activity=game_activity)
            except Exception as e:
                print(Fore.RED + f"Failed to update presence: {e}")

            await asyncio.sleep(20)
            fences_painted += 1
            self.update_fences_painted(fences_painted)

        # Call the ASCII animation function
        from asciimatics.screen import Screen
        Screen.wrapper(startup_animation)

async def setup(bot):
    await bot.add_cog(OnReady(bot))