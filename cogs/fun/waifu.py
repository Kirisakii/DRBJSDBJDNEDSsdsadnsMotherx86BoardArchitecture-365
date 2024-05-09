import json
import urllib

import bs4 as bs
import discord
from discord.ext import commands

# Variabals
header = {"User-Agent": "Mozilla"}


class Web(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    def connectParse(self, link: str) -> str:
        req = urllib.request.Request(url=link, headers=header)
        print("Connecting")
        resp = urllib.request.urlopen(req)
        print("Opening")
        parsed = bs.BeautifulSoup(resp, "html.parser")
        print("Parsing")
        return parsed

    @commands.hybrid_command(
        aliases=["waifu"],
        with_app_command=True,
        description="sends amazing pics",
    )
    async def neko(self, ctx, mode: str = "neko") -> None:
        "❤️ キャットガールズは最高です"

        soup = self.connectParse(f"https://nekos.life/api/v2/img/{mode}")
        neko = soup.findAll(text=True)
        nekojson = json.loads(str(neko)[2:-4])
        try:
            nekolink = nekojson["url"]
            await ctx.send(nekolink)
        except KeyError:
            await ctx.send("Tag doesn't exist. Beep.")


async def setup(bot):
    await bot.add_cog(Web(bot))