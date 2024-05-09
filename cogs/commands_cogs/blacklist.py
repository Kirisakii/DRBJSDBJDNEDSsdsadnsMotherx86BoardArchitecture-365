import discord
from discord.ext import commands
import aiosqlite, re

class BlacklistCog(commands.Cog):
    DB_PATH = './db/blacklist.db'

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.setup_db())

    async def setup_db(self):
        async with aiosqlite.connect(self.DB_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS blacklist (
                    user_id INTEGER PRIMARY KEY
                )
            ''')
            await db.commit()

    async def add_to_blacklist(self, user_id):
        async with aiosqlite.connect(self.DB_PATH) as db:
            await db.execute('INSERT INTO blacklist (user_id) VALUES (?)', (user_id,))
            await db.commit()

    async def remove_from_blacklist(self, user_id):
        async with aiosqlite.connect(self.DB_PATH) as db:
            await db.execute('DELETE FROM blacklist WHERE user_id = ?', (user_id,))
            await db.commit()

    async def is_user_blacklisted(self, user_id):
        async with aiosqlite.connect(self.DB_PATH) as db:
            async with db.execute('SELECT user_id FROM blacklist WHERE user_id = ?', (user_id,)) as cursor:
                return await cursor.fetchone() is not None
            
    @commands.command(name='unblacklist', help='Removes a user from the blacklist.', aliases=['ul'])
    @commands.is_owner()
    async def unblacklist(self, ctx, user_mention: str):
        # Extract numeric ID from mention
        match = re.match(r'<@!?(\d+)>', user_mention)
        if match:
            user_id = int(match.group(1))
        else:
            try:
                user_id = int(user_mention)  # Try converting directly if it's just a numeric ID
            except ValueError:
                await ctx.send("Couldn't find that user `✍️`(◔◡◔) . Please provide a valid user ID or just mention them. ^_~", delete_after=5)
                return

        if await self.is_user_blacklisted(user_id):
            await self.remove_from_blacklist(user_id)
            await ctx.send(f"User with ID `{user_id}` has been removed from the blacklist. (^///^)", delete_after=5)
        else:
            await ctx.send(f"User with ID `{user_id}` is not on the blacklist. (～﹃～)~zZ", delete_after=5)

    @commands.command(name='blacklist', help='Adds a user to the blacklist.', aliases=['bl'])
    @commands.is_owner()
    async def blacklist(self, ctx, user_mention: str):
        # Extract numeric ID from mention
        match = re.match(r'<@!?(\d+)>', user_mention)
        if match:
            user_id = int(match.group(1))
        else:
            try:
                user_id = int(user_mention)  # Try converting directly if it's just a numeric ID
            except ValueError:
                await ctx.send("Couldn't find that user. Please provide a valid user ID or mention.", delete_after=5)
                return

        if not await self.is_user_blacklisted(user_id):
            await self.add_to_blacklist(user_id)
            await ctx.send(f"User with ID `{user_id}` has been added to the blacklist. (●'◡'●)", delete_after=5)
        else:
            await ctx.send(f"User with ID `{user_id}` is already on the blacklist, no need to add them again. (┬┬﹏┬┬)", delete_after=5)

async def setup(bot):
    await bot.add_cog(BlacklistCog(bot))