import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import json
import asyncio
import uuid


class EditEmbedView(discord.ui.View):
    def __init__(self, message_id):
        super().__init__()
        self.message_id = message_id
        unique_id = uuid.uuid4()  # Generate a unique ID for this instance of the view
        # Pass the message_id to the modals
        self.add_item(discord.ui.Button(label="Edit Title", custom_id=f"edit_title_{unique_id}", style=discord.ButtonStyle.primary))
        self.add_item(discord.ui.Button(label="Edit Description", custom_id=f"edit_desc_{unique_id}", style=discord.ButtonStyle.primary))

    # Define the callback methods here if needed, ensuring they match the custom_id patterns

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Here, you can add checks to ensure the user interacting is the one who initiated the edit
        return True

    @discord.ui.button(label="Edit Title", style=discord.ButtonStyle.primary, custom_id="edit_title")
    async def edit_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Pass the stored message_id to EditTitleModal
        await interaction.response.send_modal(EditTitleModal(message_id=self.message_id))

    @discord.ui.button(label="Edit Description", style=discord.ButtonStyle.primary, custom_id="edit_desc")
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Pass the stored message_id to EditDescriptionModal
        await interaction.response.send_modal(EditDescriptionModal(message_id=self.message_id))

class EditTitleModal(discord.ui.Modal, title="Edit Title"):
    def __init__(self, message_id):
        super().__init__()
        self.message_id = message_id
        self.new_title = discord.ui.TextInput(label="New Title", style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.channel
        try:
            message = await channel.fetch_message(self.message_id)
            embed = message.embeds[0]
            embed.title = self.new_title.value
            await message.edit(embed=embed)
            await interaction.response.send_message("Embed title updated successfully.", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("Original message not found.", ephemeral=True)

class EditDescriptionModal(discord.ui.Modal, title="Edit Description"):
    def __init__(self, message_id):
        super().__init__()
        self.message_id = message_id
        # Initialize the TextInput component and add it to the modal
        self.new_description = discord.ui.TextInput(label="New Description", style=discord.TextStyle.paragraph)
        self.add_item(self.new_description)  # This line is crucial

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.channel
        try:
            message = await channel.fetch_message(self.message_id)
            embed = message.embeds[0]
            embed.description = self.new_description.value  # Assuming you want to update the description
            await message.edit(embed=embed)
            await interaction.response.send_message("Embed description updated successfully.", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("Original message not found.", ephemeral=True)



class EmbedCreationSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Schedule the setup_db to run
        bot.loop.create_task(self.setup_db())

    async def setup_db(self):
        async with aiosqlite.connect("embeds.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS embeds (embed_name TEXT, message_id INTEGER, creator_id INTEGER)")
            await db.commit()

    # The rest of your cog code...

    @app_commands.command(name="send_embed", description="Send a premade embed.")
    async def send_embed(self, interaction: discord.Interaction, embed_name: str):
        embed = discord.Embed(title="Default Title", description="Default Description", color=0x00ff00)
        await interaction.response.defer()
        message = await interaction.followup.send(embed=embed, wait=True)
        async with aiosqlite.connect("embeds.db") as db:
            await db.execute("INSERT INTO embeds (embed_name, message_id, creator_id) VALUES (?, ?, ?)", (embed_name, message.id, interaction.user.id))
            await db.commit()


async def setup(bot:commands.Bot):
    await bot.add_cog(EmbedCreationSystem(bot))

