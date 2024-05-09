import discord
from discord import app_commands
from discord.ext import commands


class Dropdown(discord.ui.Select):
    def __init__(self):

        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label = "Main", description = "Shows the main help page.", emoji = "<:da9b75b5da1ccd5f37c1ab8e9ef232b3:1223944938119630970>"),
            discord.SelectOption(label = "Tickets", description = "Help For Tickets.", emoji = "📩"),
            discord.SelectOption(label = "Anti-Spam", description = "Help For Anti-Spam", emoji = "⛔"),
            discord.SelectOption(label = "Moderation", description = "Help For Moderation", emoji = "⚒️"),
            discord.SelectOption(label = "Artificial Intelligence", description = "Not Available For Now", emoji = "🤖"),
            discord.SelectOption(label = "Actions And RolePlay", description = "Shows commands for rp", emoji = "👌🏻"),
            discord.SelectOption(label = "Games", description = "Help For Games", emoji = "🎮"),
            discord.SelectOption(label = "Utility", description = "Other Utility Commands.", emoji = "🔧"),
            discord.SelectOption(label = "Custom Embeds", description = "Help For Custom Embed Generation", emoji = "⚙️"),
            discord.SelectOption(label = "Fun", description = "Shows fun commands", emoji = "🎉"),
            discord.SelectOption(label = "Custom Buttons", description = "Help For Custom Buttons", emoji = "🔲"),
            discord.SelectOption(label = "Self Roles", description = "Help For Self Roles", emoji = "<:1246476:1223294056575270974>")
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder = "Select category.", min_values = 1, max_values = 1, options = options)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.

        # Check user
        if interaction.user != interaction.message.interaction.user: return await interaction.response.send_message("Use your own help command.", ephemeral = True)

        # Index page
        if self.values[0] == "Main":
            em = discord.Embed(title = "Information On Lo3V <:7664book:1204768405513834576>!",
                           description = """Hello! <a:wave_animated:1204684574802714674> This Is **Lo3V** An Advanced & High Profiled Discord Bot.\n\nTry Saying "Hi Love" or "Hi Lo3V?, You can Directly ask the bot about its features."\nUse `/help <category> <command>` for more info on a command.\nUse the dropdown menu below to select a category.\n<:zdeco16_cc:1223923706707972107> Bot's Still In Beta And Some Features May Not Work As Expected Feel Free To Report Them In [Lo3V's Official Discord](https://discord.gg/UJCw2g4apW)\n\n""",
                           color = 0x2F3136)
        
            em.set_thumbnail(url = "https://media.discordapp.net/attachments/1214985653792669716/1223938182307905607/upklRZO.png?ex=661bac42&is=66093742&hm=14465032a7f6e3699447cc52e0bec881ce7cc08c5a7d19c77138fbed90ae6704&=&format=webp&quality=lossless&width=315&height=314")
            em.add_field(name = "**What's Lo3V? <a:whowhat:1204769940750602290>**", value = "Lo3V or LoVe is a discord application here to add a bit more crisp to your discord server. <:UnityChanClever:1223933619333234778>")
            em.add_field(name = "**What Does Our Application Lo3V Offer? <:UnityChanHuh:1223923070734045316>**", value = "- Custom Buttons And Embeds!\n- 10+ Games To Make Your Server A Bit More Exciting!\n- Anti-Spam System\n- Suggestions System\n- Moderation\n- DropDown SelfRoles\n- And More Utility..., feel free to explore futher :D")
            em.set_footer(text=f"Requested by {interaction.user.display_name} | Use the components below for navigation. This menu shows only the available commands and categories.")
        
            await interaction.message.edit(embed = em)
            await interaction.response.defer()

        # Moderation page
        if self.values[0] == "Moderation":
            embed = discord.Embed(title = "**Moderation**", description = "Moderation commands that helps in moderating the server", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </kick:1017544215586164819> , </multikick:1025865754790350848> , </mute:1017544215586164823> , </multimute:1025855722308784128> , </unmute:1017544215586164824> , </warn:1020339992851140679> , </multiwarn:1025860023001284608> , </unwarn:1020347964528541726> , </warnings:1020339992851140680> , </ban:1017544215586164820> , </multiban:1025871989627424828> , </unban:1022308950579880046> , </unbanall:1024382428359434260> , </timeout:1020114423026810901> , </multitimeout:1025863838001795133> , </clear:1017544215586164817> , </addrole:1081342436112081019> , </removerole:1081342436112081020>")
            embed.set_footer(text = "Use /help moderation <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        # Utility page
        elif self.values[0] == "Utility":
            embed = discord.Embed(title = "**Utility**", description = "Utility commands contains varies types of commands to use", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </poll:1093371959825408075> , </ping:1093371959628283945> , </serverlink:1093371959825408072> , </invite:1093371959825408073> , </vote:1093371959825408074> , </timer:1093371959825408071> , </tax:1093371959825408070> , </nick:1093371959628283953> , </embed:1093371959628283952> , </calculator:1093371959628283951> , </giveaway:1093371959628283954> , </translate:1093371959628283950> , </affirmation:1093371959628283947> , </advice:1093371959628283946>")
            embed.set_footer(text = "Use /help utility <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        # Fun page
        elif self.values[0] == "Fun":
            embed = discord.Embed(title = "**Fun**", description = "Fun commands to have fun", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </meme:1017544215871373393> , </rate:1017544215871373392> , </f:1017544215871373396> , </coinflip:1017544215871373395> , </reverse:1017544215871373397> , </slot:1017544215871373398> , </choose:1017544215871373394> , </emojify:1020114423026810904> , </wyr:1021052870231085106> , </cat:1021770303979917436> , </dog:1032658220730294313> , </dadjoke:1081342436292427877> , </geekjoke:1081342436112081028>")
            embed.set_footer(text = "Use /help fun <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        # Logs page
        elif self.values[0] == "Logging":
            embed = discord.Embed(title = "**Logging**", description = "Log everything in your server", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </log joins:1081342436292427878> , </log leaves:1081342436292427878> , </log message deletes:1081342436292427878> , </log message edits:1081342436292427878> , </log channel create:1081342436292427878> , </log channel delete:1081342436292427878> , </log channel updates:1081342436292427878> , </log role create:1081342436292427878> , </log role delete:1081342436292427878> , </log role updates:1081342436292427878> , </log role given:1081342436292427878> , </log role remove:1081342436292427878> , </log member ban:1081342436292427878> , </log member unban:1081342436292427878> , </log member timeout:1081342436292427878> , </log member nickname:1081342436292427878> , </log server_updates:1081342436292427878> , </log show_settings:1081342436292427878>")
            embed.set_footer(text = "Use /help logs <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        # Tickets page
        elif self.values[0] == "Tickets":
            embed = discord.Embed(title = "**Tickets**", description = "Create and moderate tickets", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </ticket launch:1020114423026810906> , </ticket close:1020114423026810906> , </ticket archive:1020114423026810906> , </ticket add:1020114423026810906> , </ticket remove:1020114423026810906> , </ticket role:1020114423026810906> , </ticket transcript:1020114423026810906>")
            embed.set_footer(text = "Use /help tickets <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        # Anti-Spam page
        elif self.values[0] == "Anti-Spam":
            embed = discord.Embed(title = "**Anti-Spam**", description = "Create an Anti-Spam system", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </antispam enable:1081342436292427879> , </antispam disable:1081342436292427879> , </antispam punishment:1081342436292427879> , </antispam whitelist:1081342436292427879>")
            embed.set_footer(text = "Use /help antispam <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        # Artificial Intelligence page
        elif self.values[0] == "Artificial Intelligence":
            embed = discord.Embed(title = "**Artificial Intelligence**", description = "Create Your Own Character That Becomes The Attire Of Your Server.", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> /Ai_Persona_Add , /Ai_Persona_Remove , /Ai_Persona_List, /Toggle_Active, /Create_Roles, /Create_Channels")
            embed.set_footer(text = "Not Available Temporarily")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        # Anime & Manga page
        elif self.values[0] == "Actions And RolePlay":
            embed = discord.Embed(title = "**Anime & Manga**", description = "Commands for weebs", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </anime:1186399224695361668> , </manga:1186399224695361669> , </character:1186399224695361670> , </aghpb:1182285037043990609>")
            embed.set_footer(text = "Use /help anime <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        # Settings page
        elif self.values[0] == "Custom Embeds":
            embed = discord.Embed(
                    title="✨ **Make Custom Embeds** ✨",
                    description="Easily Create Embeds And Send Them Through Webhook Or The Bot Itself!\n"
                    "Let's Start With the /quickembed command, okay?",
                    color=0x2F3136
                    )
            embed.add_field(
                name="✨ Embed Creation ✨",
                value="> </quickembed:1223750770818814123> - Like, Totally Create Custom Embeds\n"
                "> **:** Heads up, user, if you're adding images or thumbnails, they totally need to be valid links, or the embed might not show up right, you know?\n"
                "> **:** For the deets, you can only pass text for the author and footer, but don't worry, you can totally change 'em later, like, if you wanna.\n"
                "> **:** And for the color, make sure you only pass the RGB value '2F3136', okay? If you send it like '#2F3136', it might mess up the whole embed vibe, you feel me?\n"
                "> **:** There's Another Command For Creating Embeds As Well But It's Kinda Tradional `-cc yourembedname` this will generate an embed for you without needed to pass anything!\n __**Please Note : Other Properties Can Be Edited With Their Parent Commands.**__"
            , inline=False)

            embed.add_field(
                name="✨ Embed Editing ✨",
                value="> </edit:1223750770579476621> Hey there, user! Let's talk about enhancing your embeds with the `ee` or </edit:1223750770579476621> command. It's super handy for tweaking things just the way you like them!\n"
                "> **:** You can use it with the prefix `-ee` followed by the embed name and the property you wanna change, like 'title', 'description', 'thumbnail', 'image', or 'color'. There's also a /command </edit:1223750770579476621> version if you're into that vibe!\n"
                "> **:** Remeber When you're playing around with the color, remember to pass in the RGB value '2F3136'. Oh, and if you're messing with the thumbnail or image, make sure to include the link!\n"
                "> </embed_author:1223959277958336601> - Adds Author To Your Embed. __Note - To Remove Author From Your Embed Just Execute The Command Without Passing Anything!__ `-ea yourembedname`\n"
                "> </embed_footer:1223959277958336600> - Adds Footer To Your Embed. __Note - To Remove Author From Your Embed Just Execute The Command Without Passing Anything!__ `-ea yourembedname`\n"
                
            , inline=False)
            embed.add_field            


            embed.set_footer(text = "Use /help settings <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        # Games page
        elif self.values[0] == "Games":
            embed = discord.Embed(title = "**Games**", description = "Challange others in games", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </connect4:1017544216089468943> , </tictactoe:1020114423026810905> , </rps:1020114423169425429>")
            embed.set_footer(text = "Use /help games <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        # Serverinfo page
        elif self.values[0] == "Custom Buttons":
            embed = discord.Embed(title = "**Server Information**", description = "Know more about your server and members", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </server:1017544215871373400> , </owner:1017544215871373401> , </id:1017544216089468938> , </members:1017544216089468939> , </channels:1081342436112081026> , </user:1017544216089468942> , </icon:1017544216089468941> , </roles:1017544215871373399> , </avatar:1017544215762317326> , </banner:1017544215661649939>")
            embed.set_footer(text = "Use /help serverinformation <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        elif self.values[0] == "Fun":
            embed = discord.Embed(title = "**Server Information**", description = "Know more about your server and members", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </server:1017544215871373400> , </owner:1017544215871373401> , </id:1017544216089468938> , </members:1017544216089468939> , </channels:1081342436112081026> , </user:1017544216089468942> , </icon:1017544216089468941> , </roles:1017544215871373399> , </avatar:1017544215762317326> , </banner:1017544215661649939>")
            embed.set_footer(text = "Use /help serverinformation <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

        elif self.values[0] == "Self Roles":
            embed = discord.Embed(title = "**Server Information**", description = "Know more about your server and members", color = 0x2F3136)
            embed.add_field(name = "**Commands**", value = "> </server:1017544215871373400> , </owner:1017544215871373401> , </id:1017544216089468938> , </members:1017544216089468939> , </channels:1081342436112081026> , </user:1017544216089468942> , </icon:1017544216089468941> , </roles:1017544215871373399> , </avatar:1017544215762317326> , </banner:1017544215661649939>")
            embed.set_footer(text = "Use /help serverinformation <command> for information on a command.")
            await interaction.message.edit(embed = embed)
            await interaction.response.defer()

#dropdown class
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())

#help class
class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    #help start
    @app_commands.command(name = "help", description = "User Guide...!")
    @app_commands.checks.cooldown(1, 5, key = lambda i: (i.user.id))
    async def help(self, interaction: discord.Interaction):
        em = discord.Embed(title = "Information On Lo3V <:7664book:1204768405513834576>!",
                           description = """Hello! <a:wave_animated:1204684574802714674> This Is **Lo3V** An Advanced & High Profiled Discord Bot.\n\nTry Saying "Hi Love" or "Hi Lo3V?, You can Directly ask the bot about its features."\nUse `/help <category> <command>` for more info on a command.\nUse the dropdown menu below to select a category.\n__<:zdeco16_cc:1223923706707972107> Bot's Still In Beta And Some Features May Not Work As Expected Feel Free To Report Them In [Lo3V's Official Discord](https://discord.gg/UJCw2g4apW).__\n\n""",
                           color = 0x2F3136)
        
        em.set_thumbnail(url = "https://media.discordapp.net/attachments/1214985397306794028/1223927091213373631/C5bVHE2.png?ex=661ba1ee&is=66092cee&hm=7e5310ca7b366dc040d088238b5781697927e6e80fa9c4cc30e03fe7c6ad9a06&=&format=webp&quality=lossless&width=507&height=507")
        em.add_field(name = "**What's Lo3V? <a:whowhat:1204769940750602290>**", value = "Uh.. Not That Kinda Love But:.. Lo3V or LoVe is a discord application here to add a bit more crisp to your discord server. <:UnityChanClever:1223933619333234778>")
        em.add_field(name = "**What Does Our Application Lo3V Offer? <:UnityChanHuh:1223923070734045316>**", value = "- Custom Buttons And Embeds!\n- 10+ Games To Make Your Server A Bit More Exciting!\n- Anti-Spam System\n- Suggestions System\n- Moderation\n- DropDown SelfRoles\n- And More Utility..., feel free to explore futher :D")
        em.set_footer(text=f"Requested by {interaction.user.display_name} | Use the components below for navigation. This menu shows only the available commands and categories.")
        view = DropdownView()
        view.add_item(discord.ui.Button(label = "Invite Lo3V?", style = discord.ButtonStyle.link, url = "https://discord.com/oauth2/authorize?client_id=1116981623003561994&permissions=8&scope=applications.commands+bot"))
        view.add_item(discord.ui.Button(label = "Support Server", style = discord.ButtonStyle.link, url = "https://discord.gg/UJCw2g4apW"))
        view.add_item(discord.ui.Button(label = "Vote For Lo3V", style = discord.ButtonStyle.link, url = "https://discord.gg/ku2XcqR8sH", emoji = "💌"))
        await interaction.response.send_message(embed = em, view = view)

#=====================================================================================================================

    #moderation commands help
  
async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))