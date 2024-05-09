import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'User {member} has been kicked for reason: {reason}')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'User {member} has been banned for reason: {reason}')

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, user: discord.Member, role: discord.Role):
        if role in user.roles:
            await ctx.send(f"{user.mention} already has the role {role.name}.")
        else:
            await user.add_roles(role)
            await ctx.send(f"Added {role.name} to {user.mention}.")
    
    
    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, user: discord.Member, role: discord.Role):
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.send(f"Removed {role.name} from {user.mention}.")
        else:
            await ctx.send(f"{user.mention} does not have the role {role.name}.")


    @commands.command(aliases=['sinfo', 'server'])
    async def serverinfo(ctx):
        embed = discord.Embed(title="server info", description=f"here is the server info on the server, {ctx.guild.name}", color = discord.Color.green(), timestamp = ctx.message.created_at)
        embed.set_thumbnail(url = ctx.guild.icon)
        embed.add_field(name = "members", value = ctx.guild.member_count)
        embed.add_field(name="channels", value= f"(len{ctx.guild.text_channels} text | (len{ctx.guild.voice_channels}voice")
        embed.add_field(name="owner", value = ctx.guild.owner.mention)
        embed.add_field(name="description", value = ctx.guild.description)
        embed.add_field(name = "created at" , value = ctx.guild.created_at.strftime("%a, %B, %#d, %Y, %I:%M %p "))
        await ctx.send(embed=embed)

    @commands.command(aliases=['close', 'stop'])
    @commands.is_owner()
    async def shutdown(self, ctx):
            if ctx.author.guild_permissions.administrator:
                await ctx.send("Shutting down the bot...")
                await self.bot.close()
            else:
                await ctx.send("You do not have permission to shut down the bot.")

async def setup(bot):
    await bot.add_cog(Admin(bot))

