import os
from typing import Any
import kaomoji
import discord
from discord.ext import commands
from dotenv import load_dotenv
from cogs import COMMANDS, EVENT_HANDLERS, UTILITIES, FUN
from bot_utilities.config_loader import config
import aiosqlite
from cogs.commands_cogs.serveruiutility import EditEmbedView
# from cogs.commands_cogs.AiStuffCog import Testbuttonview
from cogs.utility.embed import DynamicButtonView
load_dotenv('.env')



class SomeBot(commands.AutoShardedBot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if config['AUTO_SHARDING']:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(shard_count=1, *args, **kwargs)

    async def setup_hook(self) -> None:
        # Emoji for loading
        loading_emoji = "🔄"
        # Emoji for success
        success_emoji = "✅"

        # Load commands
        for cog in COMMANDS:
            cog_name = cog.split('.')[-1]
            discord.client._log.info(f"{loading_emoji} Loading Command {cog_name}...")
            await self.load_extension(f"{cog}")
            discord.client._log.info(f"{success_emoji} Loaded Command {cog_name}")

        # Load utilities
        for cog in UTILITIES:
            cog_name = cog.split('.')[-1]
            discord.client._log.info(f"{loading_emoji} Loading Utility {cog_name}...")
            await self.load_extension(f"{cog}")
            discord.client._log.info(f"{success_emoji} Loaded Utility {cog_name}")

        # Load fun modules
        for cog in FUN:
            cog_name = cog.split('.')[-1]
            discord.client._log.info(f"{loading_emoji} Loading Fun Module {cog_name}...")
            await self.load_extension(f"{cog}")
            discord.client._log.info(f"{success_emoji} Loaded Fun Module {cog_name}")

        # Load event handlers
        for cog in EVENT_HANDLERS:
            cog_name = cog.split('.')[-1]
            discord.client._log.info(f"{loading_emoji} Loading Event Handler {cog_name}...")
            await self.load_extension(f"{cog}")
            discord.client._log.info(f"{success_emoji} Loaded Event Handler {cog_name}")

        # Add views
        self.add_view(DynamicButtonView(self))
        # self.add_view(Testbuttonview())

        # Sync commands
        await self.tree.sync()
        discord.client._log.info(f"{success_emoji} Loaded {len(self.commands)} commands")

bot = SomeBot(command_prefix=[';'], intents=discord.Intents.all(), help_command=None)

TOKEN = os.getenv('DISCORD_TOKEN')


@bot.tree.context_menu(name="Edit Embed")
async def edit_embed(interaction: discord.Interaction, message: discord.Message):
    async with aiosqlite.connect("embeds.db") as db:
        cursor = await db.execute("SELECT embed_name, creator_id FROM embeds WHERE message_id = ?", (message.id,))
        data = await cursor.fetchone()
        if data is None or interaction.user.id != data[1]:  # data[1] is the creator_id
            await interaction.response.send_message("This embed is not yours.", ephemeral=True)
            return
        # Proceed with editing, now passing the message.id to EditEmbedView
        view = EditEmbedView(message_id=message.id)
        await interaction.response.send_message("What would you like to edit?", view=view, ephemeral=True)

bot.run(TOKEN, reconnect=True)
