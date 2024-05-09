import datetime
import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import os

# Ensure the db directory exists
os.makedirs('db', exist_ok=True)
DB_PATH = 'db/snipe.db'

class snipe(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def db_setup(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS Snipes (
                                channel_id INTEGER,
                                guild_id INTEGER,
                                author_id INTEGER,
                                content TEXT
                                )''')
            await db.commit()

    # Other methods remain unchanged

# Replace the setup function with this

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel_id = message.channel.id
        deleted_message = (channel_id, message.guild.id, message.author.id, message.content)
        
        async with aiosqlite.connect(DB_PATH) as db:
            # Check if there's an existing message
            async with db.execute('SELECT * FROM Snipes WHERE channel_id = ?', (channel_id,)) as cursor:
                existing_message = await cursor.fetchone()
                if existing_message:
                    await db.execute('UPDATE Snipes SET guild_id = ?, author_id = ?, content = ? WHERE channel_id = ?', deleted_message[1:] + (channel_id,))
                else:
                    await db.execute('INSERT INTO Snipes (channel_id, guild_id, author_id, content) VALUES (?, ?, ?, ?)', deleted_message)
            await db.commit()

    @app_commands.command(
        name='snipe',
        description='Snipes the most recent deleted message.'
    )
    @app_commands.guild_only()
    async def snipe(self, interaction: discord.Interaction):
        channel_id = interaction.channel.id
        
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('SELECT author_id, content FROM Snipes WHERE channel_id = ?', (channel_id,)) as cursor:
                deleted_message = await cursor.fetchone()
        
        if deleted_message:
            author_id, content = deleted_message

            embed = discord.Embed(
                title='Snipe!',
                description=f'`{content}` - <@{author_id}>',
                color=0x575fcf,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(
                text=f'Requested by {interaction.user.name}',
                icon_url=interaction.user.avatar
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title='Snipe Failed',
                description='It seems like I can\'t snipe any messages on this channel.',
                color=0xff5e57,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(
                text=f'Requested by {interaction.user.name}',
                icon_url=interaction.user.avatar
            )

            await interaction.response.send_message(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(snipe(client))
    await client.get_cog('snipe').db_setup()