import discord, threading , time, os
from discord.ext import commands
from discord import app_commands
from bot_utilities.servergen import generate_response
from discord.ui import Button, View
from typing import Optional
import re, requests


UNICODE_EMOJI_PATTERN = re.compile(
    "[\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"  # Enclosed characters
    "]+")

class ResetConfirmationModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(title="Are you sure?", *args, **kwargs)
        self.add_item(discord.ui.TextInput(label="Type CONFIRM to reset your server", style=discord.TextStyle.short))

    async def on_submit(self, interaction: discord.Interaction):
        # Defer the interaction to ensure the modal closes
        await interaction.response.defer(ephemeral=True)
        if self.children[0].value == "CONFIRM":
            cog = interaction.client.get_cog("AiServerGeneration")
            if cog:
                # Pass the interaction object to reset_server
                await cog.reset_server(interaction.guild, interaction)
                # Send a DM to the user confirming the reset
                await interaction.user.send("Server reset successfully.")
            else:
                # Send a DM to the user if the cog is not found
                await interaction.user.send("Failed to reset the server.")
        else:
            # Send a DM to the user instructing them to type CONFIRM to proceed
            await interaction.user.send("Operation cancelled. You did not type CONFIRM. Please type CONFIRM exactly as shown to reset your server.")

class ResetConfirmationView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        modal = ResetConfirmationModal()
        await interaction.response.send_modal(modal)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Operation cancelled.", ephemeral=True)
        self.stop()


class TestView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Test", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        # Open a modal when this button is clicked
        await interaction.response.send_message("Test passed!", ephemeral=True)

    
class VerificationView(View):
    def __init__(self, bot, verified_role_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.verified_role_id = verified_role_id

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user
        verified_role = guild.get_role(self.verified_role_id)

        if verified_role in member.roles:
            await interaction.response.send_message("You've already verified.", ephemeral=True)
        else:
            await member.add_roles(verified_role)
            await interaction.response.send_message("You've been verified successfully!", ephemeral=True)


class AfterServerView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Roles", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        # Open a modal when this button is clicked
        modal = AfterServerModal()
        await interaction.response.send_modal(modal)
        self.stop()

class RoleConfirmationView(View):
    def __init__(self, structured_roles: dict):
        super().__init__(timeout=120)
        self.structured_roles = structured_roles

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        cog = interaction.client.get_cog("AiServerGeneration")
        if cog:
            await cog.execute_role_structure(interaction.guild, self.structured_roles)
            await interaction.followup.send("Roles created successfully.")
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Role creation cancelled.", ephemeral=True)
        self.stop()


class AfterServerModal(discord.ui.Modal, title='Tell us about the roles you want to create'):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.TextInput(
            label='Role Descriptions',
            style=discord.TextStyle.paragraph,
            placeholder='Describe your roles following the instructions...',
            required=True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        role_descriptions = self.children[0].value
        cog = interaction.client.get_cog("AiServerGeneration")
        if cog:
            role_template = await cog.generate_role_template(role_descriptions)
            structured_roles = cog.interpret_ai_response_to_role_structure(role_template)
            pretty_roles = cog.prettify_role_structure(structured_roles)
            
            embed = discord.Embed(
                title="Roles to be Created",
                description=pretty_roles,
                color=discord.Color.dark_red()
            )
            embed.set_thumbnail(url=interaction.client.user.avatar.url)
            await interaction.followup.send(embed=embed, view=RoleConfirmationView(structured_roles))


class DreamServerModal(discord.ui.Modal, title="Tell us more about your dream server"):
    new_response = discord.ui.TextInput(label="Describe what changes to make.", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        description = self.new_response.value
        cog = interaction.client.get_cog("AiServerGeneration")
        if cog:
            try:
                new_server_template = await cog.generate_server_structure(description)
                # Use send_message for the initial response
                await interaction.response.send_message(content="Here's an updated server structure based on your input:", embed=discord.Embed(title="Generated Server Structure Template", description=f"```\n{new_server_template}\n```", color=0x00ff00), ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred while generating the server structure: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message("The server generation functionality is currently unavailable.", ephemeral=True)

class ConfirmationView(View):
    def __init__(self, server_structure, cog, *args, **kwargs):
        super().__init__(*args, **kwargs, timeout=120)
        self.server_structure = server_structure
        self.cog = cog
        self.value = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.gray, emoji="<:zdeco22_cc:1226652353592037496>")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        self.value = True
        self.stop()
        await interaction.followup.send("Operation confirmed.")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey, emoji="<:I_TickNo:1226657550879948800>")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        self.value = False
        self.stop()
        await interaction.response.send_message("Operation cancelled.")

    @discord.ui.button(label="Not Satisfied?", style=discord.ButtonStyle.blurple, emoji="<:1246476:1226653161318518834>")
    async def not_satisfied(self, interaction: discord.Interaction, button: Button):
        modal = DreamServerModal()
        await interaction.response.send_modal(modal)

    # @discord.ui.button(label="View Your Server", style=discord.ButtonStyle.green)
    # async def view_server(self, interaction: discord.Interaction, button: Button):
    #     await interaction.response.defer(ephemeral=True)
    #     file_path = self.cog.interpret_server_structure_to_web(self.server_structure)
    #     # Upload the file and get a public URL
    #     public_url = self.cog.upload_to_transfer_sh(file_path)
    #     if public_url:
    #         await interaction.response.send_message(f"Here is your server structure: [View Server Structure]({public_url})", ephemeral=True)
    #     else:
    #         await interaction.response.send_message("Failed to upload the server structure. Please try again later.", ephemeral=True)

    async def on_timeout(self):
        self.value = False
        if self.interaction:  # Check if interaction is stored
            await self.interaction.followup.send("Time's up. Guess you took too long 🤷", ephemeral=True)


class EnableCommunityView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, timeout=120)

    @discord.ui.button(label="Enable Community", style=discord.ButtonStyle.gray, emoji="🏠")
    async def enable_community(self, interaction: discord.Interaction, button: Button):
        # Inform the user about enabling community features manually
        instructions = ("To enable community features, you need to do it manually through the server settings:\n"
                        "1. Go to Server Settings > Enable Community.\n"
                        "2. Follow the prompts to enable community features.\n\n"
                        "Note: This action can only be performed by the server owner or an admin with the necessary permissions.")
        await interaction.response.send_message(instructions, ephemeral=True)


class AiServerGeneration(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_role_permissions_and_color(self, role_type: str):
    # Define default permissions for different role types
        permissions_dict = {
            "default": discord.Permissions(),
            "trial_mod": discord.Permissions(moderate_members=True, mute_members=True, deafen_members=True, move_members=True, attach_files=True, add_reactions=True, use_external_emojis=True, change_nickname=True), 
            "mod": discord.Permissions(kick_members=True, ban_members=True, manage_messages=True, moderate_members=True, mute_members=True, deafen_members=True, move_members=True, attach_files=True, add_reactions=True, use_external_emojis=True, change_nickname=True),
            "admin": discord.Permissions(administrator=True),
            "staff": discord.Permissions(kick_members=True, ban_members=True, manage_roles=True, manage_channels=True, view_audit_log=True, move_members=True, moderate_members=True, manage_messages=True, use_application_commands=True, mute_members=True, deafen_members=True, attach_files=True, add_reactions=True, use_external_emojis=True, change_nickname=True)
        }
        # Define color for different role types
        color_dict = {
            "default": discord.Color.default(),
            "trial_mod": discord.Color.blue(),
            "mod": discord.Color.green(),
            "admin": discord.Color.red(),
            "staff": discord.Color.purple()
        }
        permissions = permissions_dict.get(role_type, discord.Permissions())
        color = color_dict.get(role_type, discord.Color.default())
        return permissions, color

    def prettify_role_structure(self, structured_roles: dict):
        emoji_map = {
            "mod": "<a:instrymenti:1204768290946424852>",
            "trial_mod": "<:8355saturn:1233771388502937670>",
            "admin": "<:neon_pacman:1233761545754771546>",
            "staff": "<:8355saturn:1233771388502937670>",
            "default": "<:5315memberbadge:1233771447026192414>",
            "color": "<:art:1234129587282251796>",
            "level": "<:upvote:1234128418409287722>"
        }
        pretty_roles = ""
        for role_name, details in structured_roles.items():
            role_type = details['permissions']
            emoji = emoji_map.get(role_type, "<:artist_cc:1234126811927941150>")  # Default to color emoji if not found
            color_code = details['hex_color'] if details['hex_color'] else "000000"
            pretty_roles += f"> {emoji} `@{role_name}` `#{color_code}`\n"
        return pretty_roles

    async def execute_role_structure(self, guild: discord.Guild, structured_roles: dict):
        existing_roles = {role.name: role for role in await guild.fetch_roles()}
        for role_name, role_info in structured_roles.items():
            if role_name in existing_roles:
                print(f"Role '{role_name}' already exists.")
                continue

            permissions_str = role_info['permissions']
            hex_color = role_info['hex_color']
            permissions, default_color = self.get_role_permissions_and_color(permissions_str)
            color = discord.Colour(int(hex_color, 16)) if hex_color else default_color

            try:
                await guild.create_role(name=role_name, permissions=permissions, color=color)
            except Exception as e:
                print(f"Failed to create role {role_name}: {e}")

    def interpret_ai_response_to_role_structure(self, ai_response: str):
        roles = {}
        lines = ai_response.split('\n')
        for line in lines:
            if line.startswith('Role:'):
                match = re.match(r"Role: \((.*?)\) (?:\(Hex: #(.*?)\)\s+)?(.+)", line)
                if match:
                    role_type, hex_color, name = match.groups()
                    roles[name.strip()] = {
                        'permissions': role_type.strip(),
                        'hex_color': hex_color.strip() if hex_color else None,
                        'name': name.strip()
                    }
        return roles

    # Make sure to include the get_role_permissions_and_color method and other necessary parts of the cog
    async def reset_server(self, guild: discord.Guild, interaction: discord.Interaction):
    # Use the existing method to delete channels
        await self.delete_existing_structure(guild, None)  # Assuming server_structure is not needed for channel deletion

        # Get the bot's highest role position
        bot_member = guild.get_member(self.bot.user.id)
        bot_highest_role_position = bot_member.top_role.position

        # Delete all roles below the bot's highest role, excluding the @everyone role
        for role in list(guild.roles):
            if role.position < bot_highest_role_position and not role.managed and not role.is_default():
                try:
                    await role.delete()
                except Exception as e:
                    print(f"Failed to delete role {role.name}: {e}")

        # Revoke all active invites
        try:
            invites = await guild.invites()
            for invite in invites:
                try:
                    await invite.delete()
                except Exception as e:
                    print(f"Failed to delete invite {invite.code}: {e}")
        except Exception as e:
            print(f"Failed to retrieve or delete invites: {e}")

        # Create a new general channel after resetting the server
        try:
            general_channel = await guild.create_text_channel('reset-successful')
            await general_channel.send("Server reset successful. Welcome to your new server!")
        except Exception as e:
            await interaction.user.send("There was an error resetting your server. Make sure that my role is at the top of the role list.")
            print(f"Failed to create the general channel: {e}")
    async def generate_role_template(self, role_descriptions: str) -> str:
        # Assuming you have a function to call your AI model
        instructions_path = "roles/roleinstruction.txt"
        with open(instructions_path, "r", encoding="utf-8") as file:
            instructions = file.read().strip()
        full_description = instructions + "\n\n" + role_descriptions
        role_template = await generate_response(full_description, [])
        return role_template

    async def enable_community_embed(self):
        embed = discord.Embed(title="Enable Community", description="Enable the community feature for your server!", color=0x00ff00)
        return embed

    

    async def delete_existing_structure(self, guild: discord.Guild, server_structure):
    # Check if community features are enabled
        if "COMMUNITY" in guild.features:
            # Fetch the current settings or identify the channels that should not be deleted
            community_required_channels = [guild.rules_channel, guild.public_updates_channel]
            community_required_channel_ids = {channel.id for channel in community_required_channels if channel}

            for channel in list(guild.channels):
                try:
                    # Check if the channel ID is in the list of community required channel IDs
                    if channel.id not in community_required_channel_ids:
                        await channel.delete()
                    else:
                        print(f"Skipping deletion of required community channel: {channel.name}")
                except discord.errors.HTTPException as e:
                    print(f"Error deleting channel {channel.name}: {e}")
        else:
            # If community features are not enabled, proceed to delete all channels
            for channel in list(guild.channels):
                try:
                    await channel.delete()
                except discord.errors.HTTPException as e:
                    print(f"Error deleting channel {channel.name}: {e}")

    async def generate_server_structure(self, description: str):
        # Placeholder for AI model integration
        # This function should return a structured format of channels and categories to create
        # For simplicity, let's assume it returns a list of tuples: [('Category', None), ('Channel', 'Category Name')]
        instructions = "Generate a server structure based on the following description: " + description
        history = []  # Assuming no prior context is needed; adjust as necessary
        response = await generate_response(instructions, history)
        # Interpret the AI response to a structured format
        # This is highly dependent on how your AI model structures its responses
        return self.interpret_ai_response_to_structure(response)
            # Inside your generate_server_template method, before sending the confirmation message
        
    async def verification_embed(self):
        embed = discord.Embed(title="Verification", description="Please verify your account by interacting to the verify button!.", color=0x00ff00)
        return embed
    

    def interpret_ai_response_to_structure(self, response):
        lines = response.split('\n')
        server_structure = {}
        current_category = None

        # Define a regex pattern to match invalid characters
        invalid_chars_pattern = re.compile(r'[-_/.\'"]')

        for line in lines:
            line = line.strip()
            if line.startswith('Category:'):
                category_name = line.split(':', 1)[1].strip()
                # Sanitize category name
                category_name = re.sub(invalid_chars_pattern, ' ', category_name)
                current_category = category_name
                server_structure[current_category] = {'TextChannels': [], 'VoiceChannels': [], 'Forums': []}
            elif line.startswith('- Channel:'):
                channel_details = line.split(':', 1)[1].strip()
                channel_name, attributes = channel_details.split(' (', 1) if '(' in channel_details else (channel_details, '')
                # Sanitize channel name
                channel_name = re.sub(invalid_chars_pattern, ' ', channel_name)
                server_structure[current_category]['TextChannels'].append({'name': channel_name, 'attributes': attributes.rstrip(')')})
            elif line.startswith('- Voice:'):
                voice_details = line.split(':', 1)[1].strip()
                voice_name, attributes = voice_details.split(' (', 1) if '(' in voice_details else (voice_details, '')
                # Sanitize voice channel name
                voice_name = re.sub(invalid_chars_pattern, ' ', voice_name)
                server_structure[current_category]['VoiceChannels'].append({'name': voice_name, 'attributes': attributes.rstrip(')')})
            elif line.startswith('- Forum:'):
                forum_details = line.split(':', 1)[1].strip()
                forum_name, forum_attrs = forum_details.split(' (', 1)
                # Sanitize forum name
                forum_name = re.sub(invalid_chars_pattern, ' ', forum_name)
                server_structure[current_category]['Forums'].append({'name': forum_name, 'attributes': forum_attrs.rstrip(')')})

        print("Interpreted Server Structure:", server_structure)
        return server_structure
    
    async def execute_server_structure(self, guild: discord.Guild, server_structure, verification_channel: bool):
        afterserver_channel = await guild.create_text_channel('afterserver')
        role_create_embed = await self.rolecreateembed()
        await afterserver_channel.send(embed=role_create_embed, view=AfterServerView())

        everyone_role = guild.default_role
        overwrites_private = {
            everyone_role: discord.PermissionOverwrite(view_channel=False),
        }
        overwrites_read_only = {
            everyone_role: discord.PermissionOverwrite(view_channel=True, send_messages=False, add_reactions=False, create_public_threads=False, create_private_threads=False),
        }
        overwrites_verified = {
            everyone_role: discord.PermissionOverwrite(view_channel=False)  # Default to not viewable
        }

        verified_role = None
        if verification_channel:
            verified_role = discord.utils.get(guild.roles, name="Verified Member")
            if not verified_role:
                verified_role = await guild.create_role(name="Verified Member")
            overwrites_verified = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                verified_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            verify_channel = await guild.create_text_channel("✅┃verify", overwrites=overwrites_verified)
            verification_embed = await self.verification_embed()

            default_avatar_url = "https://media.discordapp.net/attachments/1118533924470145036/1233428159677075526/YbOMlca.jpg"
            webhook = await verify_channel.create_webhook(name=guild.name)
            webhook_avatar_url = guild.icon.url if guild.icon else default_avatar_url
            await webhook.send(embed=verification_embed, username=guild.name, avatar_url=webhook_avatar_url, view=VerificationView(self.bot, verified_role.id))

        for category_name, category_contents in server_structure.items():
            current_category = await guild.create_category(category_name)
            for channel_type in ['TextChannels', 'VoiceChannels', 'Forums']:
                for channel_info in category_contents.get(channel_type, []):
                    channel_name = channel_info['name']
                    attributes = channel_info['attributes']
                    is_private = "Private" in attributes
                    is_read_only = "Read_Only" in attributes

                    if channel_type == 'TextChannels':
                        if is_private:
                            await guild.create_text_channel(channel_name, category=current_category, overwrites=overwrites_private)
                        elif is_read_only:
                            await guild.create_text_channel(channel_name, category=current_category, overwrites=overwrites_read_only)
                        else:
                            await guild.create_text_channel(channel_name, category=current_category)
                    elif channel_type == 'VoiceChannels':
                        if is_private:
                            await guild.create_voice_channel(channel_name, category=current_category, overwrites=overwrites_private)
                        else:
                            await guild.create_voice_channel(channel_name, category=current_category)
                    elif channel_type == 'Forums':
                        details_dict = self.parse_forum_details(attributes)
                        if isinstance(details_dict, dict):
                            tags = [discord.ForumTag(name=tag.strip()) for tag in details_dict.get('Tags', []) if tag]
                            tags = tags[:5]  # Limit to 5 tags due to Discord's constraints
                            default_reaction_emoji = details_dict.get('Default_reaction', '⭐')
                            if not re.match(r'[\u263a-\U0001f645]', default_reaction_emoji):
                                default_reaction_emoji = '⭐'  # Fallback to a star emoji if invalid
                            await guild.create_forum(
                                name=channel_name,
                                category=current_category,
                                topic=details_dict.get('Post_Guidelines', 'No guidelines provided.'),
                                default_auto_archive_duration=int(details_dict.get('default_auto_archive_duration', 1440)),
                                default_reaction_emoji=default_reaction_emoji,
                                available_tags=tags,
                                overwrites=overwrites_verified if verification_channel else {}
                            )
                    else:
                        print(f"Error: Expected a dictionary for forum details, got {type(details_dict)}")
                       

    def parse_forum_details(self, forum_details):
        details_dict = {}
        details_parts = re.findall(r'(\w+)=("[^"]+"|\[.*?\])', forum_details)
        for key, value in details_parts:
            if value.startswith('['):
                details_dict[key] = [v.strip().strip("'").strip() for v in value.strip('[]').split(',')]
            else:
                details_dict[key] = value.strip('"')
        print(f"Forum details parsed: {details_dict}")
        return details_dict
    
    def interpret_ai_response_user_convention(self, response):
    # This function formats the AI response into a more readable and visually appealing format for the user
        lines = response.split('\n')
        pretty_structure = ""
        category_emoji = "<:4135createcategory:1233770870447804496> "
        text_channel_emoji = "<:3280text:1233770867914440874> "
        voice_channel_emoji = "<:7032voice:1233770862633811979> "
        forum_emoji = "<:4162utilityforum:1233771722180919367> "

        for line in lines:
            if line.startswith('Category'):
                category_name = line.split(':', 1)[1].strip()
                pretty_structure += f"\n{category_emoji} **{category_name}**\n"
            elif line.startswith('- Channel:'):
                channel_details = line.split(':', 1)[1].strip()
                pretty_structure += f"> {text_channel_emoji} **{channel_details}**\n"
            elif line.startswith('- Voice:'):
                voice_details = line.split(':', 1)[1].strip()
                pretty_structure += f"> {voice_channel_emoji} **{voice_details}**\n"
            elif line.startswith('- Forum:'):
                forum_details = line.split(':', 1)[1].strip()
                pretty_structure += f"> {forum_emoji} **{forum_details}**\n"

        return pretty_structure
    
    # def interpret_server_structure_to_web(self, server_structure):
    #     html_content = """
    #     <html>
    #     <head>
    #         <title>Server Structure</title>
    #         <style>
    #             body { font-family: Arial, sans-serif; }
    #             .category { font-weight: bold; margin-top: 20px; }
    #             .channel { margin-left: 20px; }
    #             img { vertical-align: middle; }
    #             .scrollable { max-height: 500px; overflow-y: auto; }
    #         </style>
    #     </head>
    #     <body>
    #     <div class="scrollable">
    #     """

    #     for category, details in server_structure.items():
    #         if category == "No Category":
    #             for channel in details['TextChannels']:
    #                 html_content += f'<div class="channel"><img src="channel.png" width="16" height="16"> {channel["name"]}</div>'
    #             continue
    #         html_content += f'<div class="category"><img src="category.png" width="16" height="16"> {category}</div>'
    #         for channel_type in ['TextChannels', 'VoiceChannels', 'Forums']:
    #             icon = 'channel.png' if channel_type == 'TextChannels' else 'voice.png' if channel_type == 'VoiceChannels' else 'forum.png'
    #             for channel in details[channel_type]:
    #                 html_content += f'<div class="channel" style="margin-left: 20px;"><img src="{icon}" width="16" height="16"> {channel["name"]}</div>'

    #     html_content += """
    #     </div>
    #     </body>
    #     </html>
    #     """

    #     file_path = "server_structure.html"
    #     with open(file_path, "w") as file:
    #         file.write(html_content)

    #     # Schedule the file for deletion after 2 minutes
    #     threading.Timer(120, lambda: os.remove(file_path)).start()

    #     return os.path.abspath(file_path)
    
    # def upload_to_transfer_sh(self, file_path):
    #     with open(file_path, 'rb') as f:
    #         response = requests.post('https://transfer.sh/', files={'file': f})
    #     if response.ok:
    #         return response.text
    #     return None

    async def rolecreateembed(self):
        embed = discord.Embed(title="Role Creation", description="Done! , I hope you like your new server!\n\nThank you for using me!, However one part remains and I can do that for you!.\nReact with the button below and tell me! what roles you want in your server and how will they look like!, I'll Try My best to come up to your expectations!", color=discord.Color.red())
        return embed
    
    @discord.app_commands.command(name="remove_all_roles", description="Removes all roles from the server except bot roles.")
    @discord.app_commands.guild_only()
    async def remove_all_roles(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You need the Manage Roles permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        bot_member = guild.get_member(self.bot.user.id)
        bot_highest_role_position = bot_member.top_role.position

        skipped_roles = []
        deleted_roles = []

        for role in list(guild.roles):
            role_details = f"Role: {role.name}, Managed: {role.managed}, Default: {role.is_default()}, Position: {role.position}"
            if role.position >= bot_highest_role_position or role.managed or role.is_default():
                skipped_roles.append(role_details)
                continue

            try:
                await role.delete(reason="Role removed by /remove_all_roles command.")
                deleted_roles.append(role.name)
            except Exception as e:
                print(f"Failed to delete role {role.name}: {e}")

        print(f"Deleted roles: {deleted_roles}")
        print(f"Skipped roles: {skipped_roles}")

        if deleted_roles:
            message = f"All deletable roles have been removed. Total deleted: {len(deleted_roles)}."
        else:
            message = "No roles were deleted."

        if skipped_roles:
            message += f" Skipped roles (undeletable or higher priority): {', '.join([role.split(',')[0] for role in skipped_roles])}."

        await interaction.followup.send(message)

    @discord.app_commands.command(name="delete_role", description="Deletes a specified role from the server.")
    @discord.app_commands.describe(role="The role to delete")
    @discord.app_commands.guild_only()
    async def delete_role(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You need the Manage Roles permission to use this command.", ephemeral=True)
            return

        # Check if the bot has a higher role position than the role it tries to delete
        bot_member = interaction.guild.get_member(self.bot.user.id)
        if role.position >= bot_member.top_role.position:
            await interaction.response.send_message("I cannot delete a role that is higher or equal to my highest role.", ephemeral=True)
            return

        # Check if the role is managed or is the default @everyone role
        if role.managed or role.is_default():
            await interaction.response.send_message("This role is managed by an integration or is the default @everyone role and cannot be deleted.", ephemeral=True)
            return

        try:
            await role.delete(reason=f"Role deleted by {interaction.user.display_name} via /delete_role command.")
            await interaction.response.send_message(f"The role `{role.name}` has been successfully deleted.")
        except Exception as e:
            await interaction.response.send_message(f"Failed to delete the role `{role.name}`: {str(e)}")


    @discord.app_commands.command(name="quick_server_setup", description="Generate a server structure template based on a description.")
    @discord.app_commands.describe(description="Description of your dream server.", verification_channel="Add a verification channel and Verified Member role.")
    @discord.app_commands.choices(theme=[
        discord.app_commands.Choice(name="Default Theme", value="theme/DefaultTheme.txt"),
        discord.app_commands.Choice(name="Emoji Con Theme", value="theme/EmojiConTheme.txt"),
        discord.app_commands.Choice(name="Community Theme", value="communitythemes/defaultcommunitytheme.txt")
    ])
    @discord.app_commands.guild_only()
    async def quick_server_setup(self, interaction: discord.Interaction, description: str, verification_channel: bool = False, theme: discord.app_commands.Choice[str] = None):
        if not theme:
            await interaction.response.send_message("Please select a theme for the server setup.", ephemeral=True)
            return

        # Check if the selected theme is appropriate for the server's features
        if theme.value.startswith("communitythemes/") and "COMMUNITY" not in interaction.guild.features:
            await interaction.response.send_message("Community Theme is selected but the server does not have community features enabled. Please enable community features or select a different theme.", ephemeral=True)
            return

        await interaction.response.defer()

        # Load the selected theme instructions
        theme_instructions_path = theme.value
        try:
            with open(theme_instructions_path, "r", encoding="utf-8") as file:
                theme_instructions = file.read().strip() + "\n\n" + description
        except FileNotFoundError:
            await interaction.followup.send(f"The selected theme instructions file could not be found at '{theme_instructions_path}'.", ephemeral=True)
            return

        server_structure = await self.generate_server_structure(description)
        server_template = await generate_response(theme_instructions, [])
        pretty_server_structure = self.interpret_ai_response_user_convention(server_template)
        
        embed = discord.Embed(title="**Your Server:**", description=f"\n{pretty_server_structure}\n", color=0x2F3136)
        embed.add_field(name="<:check:1226654546005069924> | **Verification Channel**", value="> __Once this feature is enabled, a special `@Verified Member` role will be created, and a '#verify' channel will be added to the top of the server. Afterward, only members with the '@verified member' role will be able to access other channels.__", inline=False)
        embed.add_field(name="<:PinkModeratorShield:1226653308618276894> | **Paramters and their meanings**", value="> **(Private)** - __This channel is only accessible to the server owner and the adminstrators of the server.__\n> **(ReadOnly)** - __This channel is set to read-only, meaning server members can only view its content.__\n> **(Voice)** - __Indicates that this channel is designated for voice communication.__", inline=False)
        embed.add_field(name="<:Warning:1226652993089441972> | **Warning**", value="**> __If there are any additional text in brackets following the channel names in the server structure, except for the provided parameters, please refrain from executing the command__**", inline= False)
        embed.set_footer(icon_url=self.bot.user.display_avatar.url,text="This is the server structure template that will be generated. Please confirm to proceed | BY USING THIS BOT, YOU AGREE THAT WE ARE NOT LIABLE FOR ANY DATA LOSS INCURRED DURING ITS OPERATION")
        # Initialize the confirmation view
        view = ConfirmationView(server_structure=server_structure, cog=self)
        
        # Send the generated template for confirmation using the embed
        await interaction.followup.send("Please confirm to proceed:", view=view, embed=embed)

        # Wait for the user's confirmation
        await view.wait()
        if view.value is None or view.value is False:
            await interaction.followup.send("Operation cancelled.")
            return

        # Delete existing channels and categories
        await self.delete_existing_structure(interaction.guild, server_structure)

        # Interpret the AI response to a structured format
        server_structure = self.interpret_ai_response_to_structure(server_template)

        # Proceed with creating the server structure
        await self.execute_server_structure(interaction.guild, server_structure, verification_channel)
        await interaction.user.send("Server structure generated and executed successfully.")

    @discord.app_commands.command(name='generate_roles', description="Generate roles based on a description.")
    async def generate_roles(self, interaction: discord.Interaction):
        if interaction.guild.owner_id != interaction.user.id:
                await interaction.response.send_message("This command can only be executed by the server owner.", ephemeral=True)
                return
        role_create_embed = await self.rolecreateembed()
        await interaction.response.send_message(embed=role_create_embed, view=AfterServerView())
    @discord.app_commands.command(name="reset", description="Completely reset your server.")
    @discord.app_commands.guild_only()
    async def reset(self, interaction: discord.Interaction):
        if interaction.guild.owner_id != interaction.user.id:
            await interaction.response.send_message("This command can only be executed by the server owner.", ephemeral=True)
            return

        embed = discord.Embed(title="Server Reset", description="This will delete all channels and roles. Are you sure you want to proceed?", color=0xff0000)
        view = ResetConfirmationView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def category_autocomplete(self, interaction: discord.Interaction, current: str):
        categories = [discord.app_commands.Choice(name=category.name, value=category.name) for category in interaction.guild.categories]
        return [choice for choice in categories if current.lower() in choice.name.lower()]

    @discord.app_commands.command(name="create_channel", description="Create a channel with specified permissions or type.")
    @discord.app_commands.describe(channel_name="Name of the new channel", post_guidelines="Guidelines for posting in the forum", tags="Comma-separated tags for the forum", default_reaction="Default reaction emoji for the forum")
    @discord.app_commands.choices(permissions_type=[
        discord.app_commands.Choice(name="Private", value="private"),
        discord.app_commands.Choice(name="Read Only", value="read_only"),
        discord.app_commands.Choice(name="Category Sync", value="category_sync"),
        discord.app_commands.Choice(name="Voice", value="voice"),
        discord.app_commands.Choice(name="Forum", value="forum"),  # Added forum option
        discord.app_commands.Choice(name="Default", value="default")
    ])
    @discord.app_commands.autocomplete(category_name=category_autocomplete)
    @discord.app_commands.guild_only()
    async def create_channel(self, interaction: discord.Interaction, channel_name: str, permissions_type: discord.app_commands.Choice[str], category_name: str = None, post_guidelines: str = "", tags: str = "", default_reaction: str = ""):
        guild = interaction.guild
        category = None

        if category_name and category_name.lower() != 'no category':
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                await interaction.response.send_message(f"Category '{category_name}' not found.", ephemeral=True)
                return

        overwrites = {}
        if permissions_type.value == 'private':
            overwrites[guild.default_role] = discord.PermissionOverwrite(read_messages=False)
            overwrites[interaction.user] = discord.PermissionOverwrite(read_messages=True)
        elif permissions_type.value == 'read_only':
            overwrites[guild.default_role] = discord.PermissionOverwrite(send_messages=False)
        elif permissions_type.value == 'category_sync':
            if category:
                overwrites = category.overwrites
            else:
                await interaction.response.send_message("A category must be specified for 'Category Sync' permissions.", ephemeral=True)
                return

        if permissions_type.value == 'forum':
            # Parse tags from the comma-separated string to a list
            tag_list = [tag.strip() for tag in tags.split(',')] if tags else []
            # Limit tags to a maximum of 5 as per your requirement
            tag_list = tag_list[:5]

            # Handle default_reaction for both custom and Unicode emojis
            if default_reaction.startswith(':') and default_reaction.endswith(':'):  # Custom emoji format
                default_reaction_emoji = discord.utils.get(guild.emojis, name=default_reaction.strip(':'))
            else:
                default_reaction_emoji = default_reaction  # Assume it's a Unicode emoji or an empty string

            # Create forum channel with the specified attributes
            forum_channel = await guild.create_forum(name=channel_name, category=category, overwrites=overwrites, default_auto_archive_duration=1440, default_reaction_emoji=default_reaction_emoji, available_tags=[discord.ForumTag(name=tag) for tag in tag_list], topic=post_guidelines)
            await interaction.response.send_message(f"Forum '{channel_name}' created successfully.", ephemeral=True)
        elif permissions_type.value == 'voice':
            await guild.create_voice_channel(name=channel_name, category=category, overwrites=overwrites)
            await interaction.response.send_message(f"Voice channel '{channel_name}' created successfully.", ephemeral=True)
        else:  # Default to text channel if not voice or forum
            await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)
            await interaction.response.send_message(f"Text channel '{channel_name}' created successfully.", ephemeral=True)

    @discord.app_commands.command(name="move_category", description="Move a category before or after another category.")
    @discord.app_commands.describe(category_to_move="The category you want to move.", 
                                put_after="The category to place it after. Leave blank if using put_before.",
                                put_before="The category to place it before. Leave blank if using put_after.")
    @discord.app_commands.autocomplete(category_to_move=category_autocomplete, 
                                    put_after=category_autocomplete, 
                                    put_before=category_autocomplete)
    @discord.app_commands.guild_only()
    async def move_category(self, interaction: discord.Interaction, 
                            category_to_move: str, 
                            put_after: str = None, 
                            put_before: str = None):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=category_to_move)
        if not category:
            await interaction.response.send_message(f"Category '{category_to_move}' not found.", ephemeral=True)
            return

        if put_after and put_before:
            await interaction.response.send_message("Please specify only one of 'put_after' or 'put_before'.", ephemeral=True)
            return

        target_category = None
        if put_after:
            target_category = discord.utils.get(guild.categories, name=put_after)
            if not target_category:
                await interaction.response.send_message(f"Category '{put_after}' not found.", ephemeral=True)
                return
            await category.edit(position=target_category.position + 1)
        elif put_before:
            target_category = discord.utils.get(guild.categories, name=put_before)
            if not target_category:
                await interaction.response.send_message(f"Category '{put_before}' not found.", ephemeral=True)
                return
            await category.edit(position=target_category.position)

        await interaction.response.send_message(f"Category '{category_to_move}' moved successfully.", ephemeral=True)

    @discord.app_commands.command(name="create_category", description="Create a new category in the server.")
    @discord.app_commands.describe(category_name="The name of the new category.",
                                    put_after="The category to place it after. Leave blank if using put_before.",
                                    put_before="The category to place it before. Leave blank if using put_after.")
    @discord.app_commands.autocomplete(put_after=category_autocomplete, 
                                        put_before=category_autocomplete)
    @discord.app_commands.guild_only()
    async def create_category(self, interaction: discord.Interaction, 
                            category_name: str, 
                            put_after: str = None, 
                            put_before: str = None):
        guild = interaction.guild

        # Check if the category already exists
        existing_category = discord.utils.get(guild.categories, name=category_name)
        if existing_category:
            await interaction.response.send_message(f"A category with the name '{category_name}' already exists.", ephemeral=True)
            return

        # Create the new category
        new_category = await guild.create_category(name=category_name)

        if put_after and put_before:
            await interaction.response.send_message("Please specify only one of 'put_after' or 'put_before'.", ephemeral=True)
            return

        if put_after:
            target_category = discord.utils.get(guild.categories, name=put_after)
            if not target_category:
                await interaction.response.send_message(f"Category '{put_after}' not found.", ephemeral=True)
                return
            await new_category.edit(position=target_category.position + 1)

        elif put_before:
            target_category = discord.utils.get(guild.categories, name=put_before)
            if not target_category:
                await interaction.response.send_message(f"Category '{put_before}' not found.", ephemeral=True)
                return
            # Discord API positions categories in a way that to place a category before another,
            # you need to set its position to the target category's position.
            await new_category.edit(position=target_category.position)

        await interaction.response.send_message(f"Category '{category_name}' created successfully.", ephemeral=True)


    async def role_autocomplete(self, interaction: discord.Interaction, current: str):
        roles = [discord.app_commands.Choice(name=role.name, value=role.name) for role in interaction.guild.roles]
        return [choice for choice in roles if current.lower() in choice.name.lower()]

    @app_commands.command(name="create_role", description="Creates a role with specified options.")
    @app_commands.describe(rolename="The name of the role to create.",
                           put_after="The role to place the new role after. (Optional)",
                           put_before="The role to place the new role before. (Optional)",
                           roletype="Type of the role with predefined permissions and color.")
    @app_commands.choices(roletype=[
        app_commands.Choice(name="default", value="default"),
        app_commands.Choice(name="trial_mod", value="trial_mod"),
        app_commands.Choice(name="mod", value="mod"),
        app_commands.Choice(name="admin", value="admin"),
        app_commands.Choice(name="staff", value="staff")
    ])
    @app_commands.autocomplete(put_after=role_autocomplete, put_before=role_autocomplete)
    @app_commands.guild_only()
    async def create_role(self, interaction: discord.Interaction, rolename: str, roletype: str, put_after: str = None, put_before: str = None):
        if put_after and put_before:
            await interaction.response.send_message("Please specify only one of 'put_after' or 'put_before'.", ephemeral=True)
            return

        guild = interaction.guild
        bot_member = guild.get_member(self.bot.user.id)
        bot_highest_role_position = bot_member.top_role.position

        permissions, color = self.get_role_permissions_and_color(roletype)

        role_position = None

        if put_after:
            after_role = discord.utils.get(guild.roles, name=put_after)
            if not after_role:
                await interaction.response.send_message(f"Role '{put_after}' not found.", ephemeral=True)
                return
            if after_role.position >= bot_highest_role_position:
                await interaction.response.send_message("Cannot place the new role after a role higher or equal to the bot's highest role.", ephemeral=True)
                return
            role_position = after_role.position + 1

        elif put_before:
            before_role = discord.utils.get(guild.roles, name=put_before)
            if not before_role:
                await interaction.response.send_message(f"Role '{put_before}' not found.", ephemeral=True)
                return
            if before_role.position >= bot_highest_role_position:
                await interaction.response.send_message("Cannot place the new role before a role higher or equal to the bot's highest role.", ephemeral=True)
                return
            role_position = before_role.position

        try:
            new_role = await guild.create_role(name=rolename, color=color, permissions=permissions, reason="Role created via /create_role command.")
            if role_position is not None and role_position < bot_highest_role_position:
                await new_role.edit(position=role_position, reason="Setting role position via /create_role command.")
            await interaction.response.send_message(f"Role '{rolename}' created successfully with {roletype} permissions and color.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to create role: {e}", ephemeral=True)


    @app_commands.command(name="test_webhook_with_buttons")
    @app_commands.describe(webhook_url="The URL of the webhook. If not provided, a webhook will be created for the current channel.")
    async def test_webhook_with_buttons(self, interaction: discord.Interaction, webhook_url: str = None):
        channel = interaction.channel
        guild = interaction.guild
        default_avatar_url = "https://media.discordapp.net/attachments/1118533924470145036/1233428159677075526/YbOMlca.jpg?ex=662d0efd&is=662bbd7d&hm=f7de6f384c75a8961a26ca3ecb9567da7c14eafc54e9f313a3f6240e270c890b&=&format=webp&width=727&height=330"

        # Determine the appropriate avatar URL
        avatar_url = guild.icon.url if guild.icon else default_avatar_url

        if webhook_url:
            webhook = discord.Webhook.from_url(webhook_url, session=self.bot.http._HTTPClient__session)  # Use the bot's session
        else:
            webhooks = await channel.webhooks()
            webhook = webhooks[0] if webhooks else await channel.create_webhook(name="New Webhook")

        embed = await self.verification_embed()
        view = TestView()

        await webhook.send(embed=embed, view=view, username=guild.name, avatar_url=avatar_url)


async def setup(bot:commands.Bot):
    await bot.add_cog(AiServerGeneration(bot))