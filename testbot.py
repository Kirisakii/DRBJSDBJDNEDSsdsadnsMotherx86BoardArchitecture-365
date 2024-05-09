import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord import member
import os
from dotenv import load_dotenv
import os


intents = discord.Intents.all()
client = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# for filename in os.listdir('./cogs'): # iterate over the directory and load eachp filename into the list. 
#     if filename.endswith('.py'): # check if file name ends with .py so we only load what's necessary
#         client.load_extension(f'cogs.{filename[:-3]}') #finally load the cog or file into your mainstream process.

@client.event
async def on_ready():
    print("Bot is online and ready.")
    await client.change_presence(status=discord.Status.idle, activity=discord.Game(name=".gg/beetleshelp"))
    for filename in os.listdir('./coogs'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'coogs.{filename[:-3]}')
                print(f"Loaded {filename} successfully.")
            except Exception as e:
                print(f"Failed to load {filename}: {e}")

@client.command()
async def hello(ctx):
    await ctx.send("Hello how are you!")

@client.command()
async def bye(ctx):
    await ctx.send("Goodbye have a good day!")

@client.event
async def on_member_join(member):
    channel = client.get_channel(1233665948083290148)
    await channel.send("Welcome to project Sage!")
@client.event
async def on_message(message, member : discord.Member):
    if message.content == "hello":
        await message.channel.send("Hello There!")
    elif message.content == "Bye"
        await message.channel.send("OK bye!")
    elif message.content == "Dm me"
        await member.send("Hi I dmbed you!")
    elif message.content == "your_name"
        await message.channel.send("hi your_name") # there are various ways to do this this is the simplest one
    await client.process_commands(message) # this just processes the ctx or prefix commands if youre curious

@client.command()
async def embed(ctx):
    embed = discord.Embed(title="Whatever I want", description="description", color=0x4B168C )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name="Header", value="Option 1 description", inline=True)
    embed.set_footer(text="Made by G4lpez")
    await ctx.send(embed=embed)
@client.command(aliases = ['sinfo, server'])
async def serverinfo(ctx):
  embed = discord.Embed(title = "server info", description=f"here is the server info for {ctx.guild.name}", color = discord.Color.green(),timestamp = ctx.message.created_at)
  embed.set_thumbnail(url = ctx.guild.icon)
  embed.addfield(name = "members", value = ctx.guild.member_count)
  embed.addfield(name="channels",  value= f"(len{ctx.guild.text_channels} text | (len{ctx.guild.voice_channels}voice")
  embed.addfield(name="owner", value = ctx.guild.owner.mention)
  embed.addfield(name="description", value = ctx.guild.description)
  embed.addfield(name = "created at" , value = ctx.guild.created_at.strftime("%a, %B, %#d, %Y, %I:%M %p "))
  await ctx.send(embed=embed)

@client.command(aliases=['uinfo', 'who is'])
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    roles = [role for role in member.roles if role.name != "@everyone"]  

    embed = discord.Embed(title="User Info", description=f"Here's the user info for {member.name}", color=discord.Color.green(), timestamp=ctx.message.created_at)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Name", value=f"{member.name}#{member.discriminator}")
    embed.add_field(name="Nickname", value=member.display_name)
    embed.set_thumbnail(url=member.avatar.url)  
    embed.add_field(name="Status", value=str(member.status).title())  
    embed.add_field(name="Account Created", value=member.created_at.strftime("%a, %B %d, %Y, %I:%M %p"))
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%a, %B %d, %Y, %I:%M %p"))
    embed.add_field(name=f"Roles ({len(roles)})", value=" ".join([role.mention for role in roles]))  
    embed.add_field(name="Top Role", value=member.top_role.mention)
    embed.add_field(name="Bot?", value=str(member.bot))  

    await ctx.send(embed=embed)

load_dotenv()

token = os.environ.get("DISCORD_TOKEN")

client.run("MTExNjk4MTYyMzAwMzU2MTk5NA.GPgekK.hmHOy2yWbecIHlYsx4C5WoRG3-04UVA5fAsx4U")
