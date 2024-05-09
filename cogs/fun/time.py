import datetime
import random
import asyncio
import discord
import pytz
from discord import app_commands
from discord.ext import commands
import platform
import psutil


class time(commands.Cog):
    def __init__(self, client: commands.bot):
        self.client = client

    @app_commands.command(
        name = 'time',
        description = 'Returns actual time for the most important timezones.'
    )
    @app_commands.guild_only()
    async def time(self, interaction: discord.Interaction):
        timezones = [
            "UTC",
            "GMT",
            "America/New_York",
            "America/Chicago",
            "America/Los_Angeles",
            "Europe/Berlin",
            "Europe/Athens",
            "Australia/Sydney",
            "Asia/Tokyo"
        ]
        current_time = datetime.datetime.now()

        embed = discord.Embed(
            title = 'Current Time',
            color = 0x575fcf,
            timestamp = datetime.datetime.now()  
        )
        embed.set_footer(
                text = f'Requested by {interaction.user.name}',
                icon_url = interaction.user.avatar
        )

        for timezone in timezones:
            tz = pytz.timezone(timezone)
            time_in_timezone = current_time.astimezone(tz)
            formatted_time = time_in_timezone.strftime("%Y-%m-%d %H:%M")
            embed.add_field(
                name = f'<:fasttime:1223294854596132886>  {timezone}',
                value = formatted_time
            )

        await interaction.response.send_message(embed = embed)

    @app_commands.command(
        name = 'dice',
        description = 'Rolls a six sided dice.'
    )
    @app_commands.guild_only()
    async def dice(self, interaction: discord.Interaction):
        result = random.randint(1, 6)

        embed = discord.Embed(
            title = f'{interaction.user.display_name}\'s Roll Result',
            description = f'You rolled **{result}** :game_die:',
            color = 0x575fcf,
            timestamp = datetime.datetime.now(),  
        )
        embed.set_footer(
                text = f'Requested by {interaction.user.name}',
                icon_url = interaction.user.avatar
        )

        await interaction.response.send_message(embed = embed)

    @app_commands.command(
        name = 'info',
        description = 'Returns all the important and nerdy stuff about Hayate.',
    )
    @app_commands.guild_only()
    async def info(self, interaction: discord.Interaction):
        # cpu & ram usages
        ram_usage = psutil.Process().memory_full_info().rss / 1024 ** 2
        cpu_usage = psutil.cpu_percent()

        # server information
        total_servers = len(self.client.guilds)
        total_channels = sum(len(guild.channels) for guild in self.client.guilds)
        total_members = sum(guild.member_count for guild in self.client.guilds)
        avg_members = sum(g.member_count for g in self.client.guilds) // len(self.client.guilds)
        
        # system information
        python_version = platform.python_version()
        discordpy_version = discord.__version__
        os_info = platform.system()

        # ping
        latency = self.client.latency

        embed = discord.Embed(
            title = 'Hayate Information',
            description = f'Here\'s a handful of information about Hayate! If you need help with comands, use `/help`.',
            color = 0x575fcf,
            timestamp = datetime.datetime.now()  
        )
        embed.set_footer(
                text = f'Requested by {interaction.user.name}',
                icon_url = interaction.user.avatar
        )
        embed.add_field(
            name = 'Current Guild',
            value = f'```md\n<User_ID: {interaction.user.id}>\n<Channel_ID: {interaction.channel.id}>\n<Guild_ID: {interaction.guild.id}>```',
            inline = False
        )
        embed.add_field(
            name = 'Global Statistics',
            value = f'```md\n<Guilds: {total_servers}>\n<Channels: {total_channels}>\n<Users: {total_members}>\n<Avg_Users: {avg_members}>```',
            inline = False
        )
        embed.add_field(
            name = 'Bot Information',
            value = f'```md\n<Ping: {round(latency * 1000)}ms>\n<RAM_Usage: {round(ram_usage, 1)}mb>\n<CPU_Usage: {cpu_usage}>```',
            inline = False
        )
        embed.add_field(
            name = 'Project Information',
            value = f'```md\n<Python: {python_version}>\n<Discord.py: {discordpy_version}>\n<OS: {os_info}>```',
            inline = False
        )

        await interaction.response.send_message(embed = embed)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(time(client))