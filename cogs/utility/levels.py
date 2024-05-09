from discordLevelingSystem import DiscordLevelingSystem, LevelUpAnnouncement, RoleAward
import discord
from discord.ext import commands


class Levels(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot


    @commands.command(name = "commandName",
                    usage="<usage>",
                    description = "description")
    @commands.guild_only()
    @commands.has_permissions()
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def commandName(self, ctx:commands.Context):
        await ctx.send("template command")


async def setup(bot:commands.Bot):
    await bot.add_cog(Levels(bot))

