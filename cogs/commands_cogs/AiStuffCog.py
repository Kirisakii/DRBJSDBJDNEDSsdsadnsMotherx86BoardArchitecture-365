import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import random
from bot_utilities.response_utils import split_response
from bot_utilities.ai_utils import poly_image_gen, generate_image_prodia
from prodia.constants import Model
from ..common import current_language, blacklisted_words



class Testbuttonview(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    discord.ui.button(label="Test Button", style=discord.ButtonStyle.green, custom_id="test_button")
    async def test_button(self, interaction: discord.Interaction):
        await interaction.response.send_message("Test Button Pressed", ephemeral=True)

class AiStuffCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check Some's Current Latency")
    async def ping(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Pong!", description=f"{round(self.bot.latency * 1000)}ms", color=0xA81C00)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="persistenttest", description="persistenttest")
    async def persistenttest(self, interaction: discord.Interaction):
        await interaction.response.send_message("test persistent Buttons", ephemeral=True, view=Testbuttonview())

async def setup(bot):
    await bot.add_cog(AiStuffCog(bot))
