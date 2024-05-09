import discord
from discord.ext import commands
import aiosqlite
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_path = "db/welcome.db"
        self.bot.loop.create_task(self.setup_db())

    async def setup_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            # Create the table if it does not exist
            await db.execute("""
                CREATE TABLE IF NOT EXISTS welcome_settings (
                    guild_id INTEGER PRIMARY KEY,
                    channel_id INTEGER,
                    welcome_message TEXT,
                    embed_name TEXT,
                    image_url TEXT
                )
            """)
            await db.commit()

    async def set_welcome_message(self, guild_id: int, channel_id: int, welcome_message: str, embed_name: str = None):
        print(f"Setting welcome message: guild_id={guild_id}, channel_id={channel_id}, message='{welcome_message}', embed_name='{embed_name}'")
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO welcome_settings (guild_id, channel_id, welcome_message, embed_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                channel_id = COALESCE(excluded.channel_id, channel_id),
                welcome_message = excluded.welcome_message,
                embed_name = excluded.embed_name
            """, (guild_id, channel_id, welcome_message, embed_name))
            await db.commit()
            print(f"Rows affected: {cursor.rowcount}")

    async def get_welcome_message(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT channel_id, welcome_message, embed_name, image_url FROM welcome_settings WHERE guild_id = ?", (guild_id,)) as cursor:
                return await cursor.fetchone()
            
    @app_commands.command(name="welcome_set")
    @app_commands.describe(channel_name="Channel where welcome messages will be sent")
    async def welcome_set(self, interaction: discord.Interaction, channel_name: discord.abc.GuildChannel):
        # Retrieve existing settings to avoid overwriting the message
        existing_data = await self.get_welcome_message(interaction.guild_id)
        if existing_data:
            _, current_message, current_embed_name, current_image_url = existing_data
        else:
            current_message, current_embed_name, current_image_url = "", None, None

        await self.set_welcome_message(interaction.guild_id, channel_name.id, current_message, current_embed_name, current_image_url)
        await interaction.response.send_message(f"Welcome messages will be sent to {channel_name.mention}", ephemeral=True)

    @app_commands.command(name="set_welcome_image")
    @app_commands.describe(image="Upload the welcome image")
    async def set_welcome_image(self, interaction: discord.Interaction, image: discord.Attachment):
        try:
            # Download the image from the attachment
            response = requests.get(image.url)
            img = Image.open(BytesIO(response.content))
            
            # Process the image (e.g., resize, add text)
            img = img.resize((960, 540), Image.Resampling.LANCZOS)
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            text = "Welcome!"
            
            # Correctly use the textsize method with the font object
            text_width, text_height = draw.textsize(text, font=font)
            
            text_position = (img.width // 2 - text_width // 2, img.height // 2 + 20)
            draw.text(text_position, text, font=font, fill=(255, 255, 255))
            
            # Save the processed image to a buffer
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            
            # Send the image to the dedicated channel
            channel = interaction.guild.get_channel(1237086487598596167)
            message = await channel.send(file=discord.File(fp=buffer, filename="welcome_image.png"))
            
            # Store the URL of the image in the database
            await self.set_welcome_message(interaction.guild_id, None, None, None, message.attachments[0].url)
            
            await interaction.response.send_message("Welcome image set successfully.", ephemeral=True)
        except Exception as e:
            print(f"Failed to process image: {e}")
            await interaction.response.send_message("Failed to process the welcome image.", ephemeral=True)

    @app_commands.command(name="set_custom_welcome_message")
    @app_commands.describe(message="Your custom welcome message", embed_name="Optional: Name of the embed to use")
    async def set_custom_welcome_message(self, interaction: discord.Interaction, message: str, embed_name: str = None):
        if not message.strip():  # Check if the message is empty or whitespace
            await interaction.response.send_message("The welcome message cannot be empty.", ephemeral=True)
            return
        print(f"Received custom message: '{message}', embed_name: '{embed_name}'")
        await self.set_welcome_message(interaction.guild_id, None, message, embed_name)
        await interaction.response.send_message("Custom welcome message set successfully.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        data = await self.get_welcome_message(member.guild.id)
        if data:
            channel_id, message_template, embed_name, image_url = data
            channel = member.guild.get_channel(channel_id)
            if channel:
                # Replace placeholders in the message template
                message = message_template.format(user=member, username=member.display_name, user_name=member.name, user_mention=member.mention)
                if image_url:
                    await channel.send(content=message, file=discord.File(image_url))
                else:
                    await channel.send(message)


async def setup(bot:commands.Bot):
    await bot.add_cog(Welcome(bot))

