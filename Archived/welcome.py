import discord
from discord.ext import commands
import aiosqlite
from discord import app_commands

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__()
    @discord.ui.button(label="Proceed", style=discord.ButtonStyle.green, custom_id="proceed")
    async def proceed_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Done!", ephemeral=True)

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.blurple, custom_id="edit")
    async def edit_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("What Would You Like To Edit?", ephemeral=True, view=Subview())

class Subview(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="Edit Message", style=discord.ButtonStyle.blurple)
    async def edit_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditMessage())
    @discord.ui.button(label="Edit Title", style=discord.ButtonStyle.primary, custom_id="edit_title")
    async def edit_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Pass the stored message_id to EditTitleModal
        await interaction.response.send_modal(EditTitle())
    @discord.ui.button(label="Edit Description", style=discord.ButtonStyle.primary)
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditDescription())
    @discord.ui.button(label="Edit Thumbnail", style=discord.ButtonStyle.primary)
    async def edit_thumbnail(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditThumbnail())
    @discord.ui.button(label="Edit Image", style=discord.ButtonStyle.primary)
    async def edit_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditImage())
    @discord.ui.button(label="Edit Color", style=discord.ButtonStyle.red)
    async def edit_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditColor())

class EditColor(discord.ui.Modal, title='Edit Welcome Color'):
    def __init__(self):
        super().__init__()

    embedcolor = discord.ui.TextInput(
        label='Embed Color',
        style=discord.TextStyle.short,
        placeholder='Enter the new color...',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog("WelcomeCog")
        guild_id = interaction.guild_id
        new_color = self.embedcolor.value

        # Fetch current settings
        current_settings = await cog.get_guild_settings(guild_id)
        if current_settings:
            # Corrected unpacking to match the actual returned values
            welcome_message, welcome_channel_name, webhook_url, current_title, current_description, current_thumbnail, current_image = current_settings

            # Update the message while keeping other settings unchanged
            await cog.set_welcome_message(guild_id, color=new_color, embed_title=current_title, embed_description=current_description, embed_thumbnail=current_thumbnail, embed_image=current_image)

            # Create the updated embed with all current settings
class EditMessage(discord.ui.Modal, title='Edit Welcome Message'):
    def __init__(self):
        super().__init__()

    embedmessage = discord.ui.TextInput(
        label='Embed Message',
        style=discord.TextStyle.long,
        placeholder='Enter the new message...',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog("WelcomeCog")
        guild_id = interaction.guild_id
        new_message = self.embedmessage.value

        current_settings = await cog.get_guild_settings(guild_id)
        if current_settings:
            welcome_message, welcome_channel_name, webhook_url, current_title, current_description, current_thumbnail, current_image, current_color = current_settings

            await cog.set_welcome_message(guild_id, message=new_message, embed_title=current_title, embed_description=current_description, embed_thumbnail=current_thumbnail, embed_image=current_image, embed_color=current_color)

            updated_embed = discord.Embed(title=current_title, description=current_description, color=int(current_color.strip("#"), 16) if current_color else discord.Color.blue())
            if current_thumbnail:
                updated_embed.set_thumbnail(url=current_thumbnail)
            if current_image:
                updated_embed.set_image(url=current_image)

            await interaction.response.send_message("Welcome message updated:", embed=updated_embed, ephemeral=True)
class EditTitle(discord.ui.Modal, title='Edit Welcome Embed'):
    def __init__(self):
        super().__init__()

    embedtitle = discord.ui.TextInput(
        label='Embed Title',
        style=discord.TextStyle.short,
        placeholder='Enter the new title...',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog("WelcomeCog")
        guild_id = interaction.guild_id
        new_title = self.embedtitle.value

        # Fetch current settings
        current_settings = await cog.get_guild_settings(guild_id)
        if current_settings:
            # Corrected unpacking to match the actual returned values
            welcome_message, welcome_channel_name, webhook_url, current_title, current_description, current_thumbnail, current_image, current_color = current_settings

            # Update the title while keeping other settings unchanged
            await cog.set_welcome_message(guild_id, message=None, embed_title=new_title, embed_description=current_description, embed_thumbnail=current_thumbnail, embed_image=current_image)

            # Create the updated embed with all current settings
            updated_embed = discord.Embed(title=new_title, description=current_description, color=int(current_color.strip("#"), 16) if current_color else discord.Color.blue())
            if current_thumbnail:
                updated_embed.set_thumbnail(url=current_thumbnail)
            if current_image:
                updated_embed.set_image(url=current_image)

            if welcome_message and updated_embed:
                await interaction.response.send_message(content=new_message, embed=updated_embed, ephemeral=True)
            elif welcome_message:
                await interaction.response.send_message(content=new_message, ephemeral=True)
            elif updated_embed:
                await interaction.response.send_message(embed=updated_embed, ephemeral=True)

class EditDescription(discord.ui.Modal, title='Edit Welcome Embed'):
    def __init__(self):
        super().__init__()

    embeddescription = discord.ui.TextInput(
        label='Embed Description',
        style=discord.TextStyle.short,
        placeholder='Enter the new description...',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog("WelcomeCog")
        guild_id = interaction.guild_id
        new_description = self.embeddescription.value

        # Fetch current settings
        current_settings = await cog.get_guild_settings(guild_id)
        if current_settings:
            welcome_message, welcome_channel_name, webhook_url, current_title, current_description, current_thumbnail, current_image, current_color = current_settings

            # Update the title while keeping other settings unchanged
            await cog.set_welcome_message(guild_id, message=None, embed_title=current_title, embed_description=new_description, embed_thumbnail=current_thumbnail, embed_image=current_image)

            # Create the updated embed with all current settings
            updated_embed = discord.Embed(title=current_title, description=new_description, color=int(current_color.strip("#"), 16) if current_color else discord.Color.blue())

            # Create the updated embed with all current settings
            updated_embed = discord.Embed(title=current_title, description=new_description, color=discord.Color.blue())
            if current_thumbnail:
                updated_embed.set_thumbnail(url=current_thumbnail)
            if current_image:
                updated_embed.set_image(url=current_image)

            await interaction.response.send_message("Welcome embed updated:", embed=updated_embed, ephemeral=True)
class EditThumbnail(discord.ui.Modal, title='Edit Welcome Embed Thumbnail'):
    def __init__(self):
        super().__init__()

    embedthumbnail = discord.ui.TextInput(
        label='Embed Thumbnail URL',
        style=discord.TextStyle.short,
        placeholder='Enter the new thumbnail URL...',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog("WelcomeCog")
        guild_id = interaction.guild_id
        new_thumbnail = self.embedthumbnail.value

        # Fetch current settings
        current_settings = await cog.get_guild_settings(guild_id)
        if current_settings:
            welcome_message, welcome_channel_name, webhook_url, current_title, current_description, current_thumbnail, current_image, current_color = current_settings

            # Update the title while keeping other settings unchanged
            await cog.set_welcome_message(guild_id, message=None, embed_title=current_title, embed_description=current_description, embed_thumbnail=new_thumbnail, embed_image=current_image)

            # Create the updated embed with all current settings
            updated_embed = discord.Embed(title=current_title, description=current_description, color=int(current_color.strip("#"), 16) if current_color else discord.Color.blue())
            updated_embed.set_thumbnail(url=new_thumbnail)
            if current_image:
                updated_embed.set_image(url=current_image)
        else:
            updated_embed = discord.Embed(color=discord.Color.blue())
            updated_embed.set_thumbnail(url=new_thumbnail)

        await interaction.response.send_message("Welcome embed thumbnail updated:", embed=updated_embed, ephemeral=True)

class EditImage(discord.ui.Modal, title='Edit Welcome Embed Image'):
    def __init__(self):
        super().__init__()

    embedimage = discord.ui.TextInput(
        label='Embed Image URL',
        style=discord.TextStyle.short,
        placeholder='Enter the new image URL...',
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog("WelcomeCog")
        guild_id = interaction.guild_id
        new_image = self.embedimage.value

        # Fetch current settings
        current_settings = await cog.get_guild_settings(guild_id)
        if current_settings:
            welcome_message, welcome_channel_name, webhook_url, current_title, current_description, current_thumbnail, current_image, current_color = current_settings

            # Update the title while keeping other settings unchanged
            await cog.set_welcome_message(guild_id, message=None, embed_title=current_title, embed_description=current_description, embed_thumbnail=current_thumbnail, embed_image=new_image)

            # Create the updated embed with all current settings
            updated_embed = discord.Embed(title=current_title, description=current_description, color=int(current_color.strip("#"), 16) if current_color else discord.Color.blue())
            if current_thumbnail:
                updated_embed.set_thumbnail(url=current_thumbnail)
            updated_embed.set_image(url=new_image)
        else:
            updated_embed = discord.Embed(color=discord.Color.blue())
            updated_embed.set_image(url=new_image)

        await interaction.response.send_message("Welcome embed image updated:", embed=updated_embed, ephemeral=True)


class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_path = "db/welcome_settings.db"
        self.bot.loop.create_task(self.setup_db())

    async def channel_autocomplete(self, interaction: discord.Interaction, current: str):
        channels = [discord.app_commands.Choice(name=channel.name, value=channel.name) for channel in interaction.guild.text_channels]
        return [choice for choice in channels if current.lower() in choice.name.lower()]

    async def setup_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("CREATE TABLE IF NOT EXISTS welcome_settings (guild_id INTEGER PRIMARY KEY, welcome_message TEXT, welcome_channel TEXT, webhook_url TEXT, embed_title TEXT, embed_description TEXT, embed_thumbnail TEXT, embed_image TEXT, embed_color TEXT)")
            await db.commit()
        

    async def set_welcome_message(self, guild_id: int, message: str = None, embed_title: str = None, embed_description: str = None, embed_thumbnail: str = None, embed_image: str = None, embed_color: str = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO welcome_settings (guild_id, welcome_message, embed_title, embed_description, embed_thumbnail, embed_image, embed_color)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                welcome_message = excluded.welcome_message,
                embed_title = excluded.embed_title,
                embed_description = excluded.embed_description,
                embed_thumbnail = excluded.embed_thumbnail,
                embed_image = excluded.embed_image,
                embed_color = excluded.embed_color
            """, (guild_id, message, embed_title, embed_description, embed_thumbnail, embed_image, embed_color))
            await db.commit()

    async def set_welcome_channel(self, guild_id: int, channel_name: str):
        async with aiosqlite.connect(self.db_path) as db:
            # Check if there's an existing setting
            async with db.execute("SELECT guild_id FROM welcome_settings WHERE guild_id = ?", (guild_id,)) as cursor:
                result = await cursor.fetchone()
            if result:
                # Update existing setting
                await db.execute("UPDATE welcome_settings SET welcome_channel = ? WHERE guild_id = ?", (channel_name, guild_id))
            else:
                # Insert new setting with NULL for welcome_message
                await db.execute("INSERT INTO welcome_settings (guild_id, welcome_channel) VALUES (?, ?)", (guild_id, channel_name))
            await db.commit()

    async def get_guild_settings(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT welcome_message, welcome_channel, webhook_url, embed_title, embed_description, embed_thumbnail, embed_image, embed_color FROM welcome_settings WHERE guild_id = ?", (guild_id,)) as cursor:
                return await cursor.fetchone()
    #

    @app_commands.command(name="welcome_set")
    async def welcome_set(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Hi :D", description="this is customization module for your welcome embed...",color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True, view=MainView())

    @app_commands.command(name="welcome_channel_set")
    @app_commands.autocomplete(channel_name=channel_autocomplete)
    async def welcome_channel_set(self, interaction: discord.Interaction, channel_name: str):
        await self.set_welcome_channel(interaction.guild_id, channel_name)
        await interaction.response.send_message(f"Welcome channel set to: {channel_name}", ephemeral=True)

    @app_commands.command(name="test_welcome", description="test welcome message")
    async def test_welcome(self, interaction: discord.Interaction):
        settings = await self.get_guild_settings(interaction.guild_id)
        if settings:
            welcome_message, welcome_channel_name, webhook_url, embed_title, embed_description, embed_thumbnail, embed_image, embed_color = settings
            
            # Convert color from hex to int, default to blue if not set
            color = discord.Color.blue()
            if embed_color:
                color = int(embed_color.strip("#"), 16)
            
            embed = discord.Embed(color=color)
            if embed_title:
                embed.title = embed_title
            if embed_description:
                embed.description = embed_description
            if embed_thumbnail:
                embed.set_thumbnail(url=embed_thumbnail)
            if embed_image:
                embed.set_image(url=embed_image)

            custom_message = welcome_message.replace("[user.mention]", interaction.user.mention).replace("[user.name]", interaction.user.name) if welcome_message else "Welcome to the server!"

            if webhook_url:
                try:
                    webhook = discord.Webhook.from_url(webhook_url, session=self.bot.http._HTTPClient__session)
                    await webhook.send(content=custom_message, username=interaction.guild.name, embed=embed)
                    await interaction.response.send_message(f"Test welcome message sent through webhook.", ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message(f"Failed to send webhook message: {e}", ephemeral=True)
            else:
                welcome_channel = discord.utils.get(interaction.guild.channels, name=welcome_channel_name)
                if welcome_channel:
                    try:
                        await welcome_channel.send(content=custom_message, embed=embed)
                        await interaction.response.send_message(f"Test welcome message sent to {welcome_channel_name}.", ephemeral=True)
                    except Exception as e:
                        await interaction.response.send_message(f"Failed to send message to channel: {e}", ephemeral=True)
                else:
                    await interaction.response.send_message("Welcome channel not found.", ephemeral=True)
        else:
            await interaction.response.send_message("Welcome settings not configured for this guild.", ephemeral=True)

    @app_commands.command(name="set_welcome_webhook")
    @app_commands.autocomplete(channel_name=channel_autocomplete)
    async def set_welcome_webhook(self, interaction: discord.Interaction, channel_name: str, webhook_url: str):
        # Find the channel by name
        channel = discord.utils.get(interaction.guild.channels, name=channel_name)
        if not channel:
            await interaction.response.send_message("Channel not found.", ephemeral=True)
            return

        # Save the webhook URL to the database
        await self.set_welcome_webhook_url(interaction.guild_id, channel.name, webhook_url)
        await interaction.response.send_message(f"Welcome webhook set for channel: {channel_name}", ephemeral=True)

    async def set_welcome_webhook_url(self, guild_id: int, channel_name: str, webhook_url: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO welcome_settings (guild_id, welcome_channel, webhook_url)
                VALUES (?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                welcome_channel = excluded.welcome_channel,
                webhook_url = excluded.webhook_url
            """, (guild_id, channel_name, webhook_url))
            await db.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        settings = await self.get_guild_settings(member.guild.id)
        if settings:
            welcome_message, welcome_channel_name, webhook_url, embed_title, embed_description, embed_thumbnail, embed_image, embed_color = settings
            
            color = discord.Color.blue()
            if embed_color:
                color = int(embed_color.strip("#"), 16)
            
            embed = discord.Embed(title=embed_title, description=embed_description, color=color)
            if embed_thumbnail:
                embed.set_thumbnail(url=embed_thumbnail)
            if embed_image:
                embed.set_image(url=embed_image)

            welcome_message = welcome_message.replace("[user.mention]", member.mention).replace("[user.name]", member.name) if welcome_message else f"Welcome {member.mention} to the server!"

            if webhook_url:
                try:
                    webhook = discord.Webhook.from_url(webhook_url, session=self.bot.http._HTTPClient__session)
                    await webhook.send(content=welcome_message, username=member.guild.name, embed=embed)
                except Exception as e:
                    print(f"Failed to send webhook message: {e}")
            else:
                welcome_channel = discord.utils.get(member.guild.channels, name=welcome_channel_name)
                if welcome_channel:
                    try:
                        await welcome_channel.send(content=welcome_message, embed=embed)
                    except Exception as e:
                        print(f"Failed to send message to channel: {e}")
                else:
                    print(f"Welcome channel named '{welcome_channel_name}' not found.")

async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeCog(bot))