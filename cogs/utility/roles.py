import discord, asyncio
from discord.ext import commands
from discord import app_commands
import aiosqlite
from typing import Union


async def setup_db():
    async with aiosqlite.connect("db/roles.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS role_menus (
                guild_id INTEGER,
                menu_name TEXT,
                menu_description TEXT,
                placeholder TEXT DEFAULT 'Choose a role...',
                max_values INTEGER DEFAULT 1,
                min_values INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, menu_name)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS menu_roles (
                guild_id INTEGER,
                menu_name TEXT,
                role_id INTEGER,
                emoji TEXT,
                role_description TEXT,
                PRIMARY KEY (guild_id, menu_name, role_id),
                FOREIGN KEY (guild_id, menu_name) REFERENCES role_menus (guild_id, menu_name)
            )
        """)
        await db.commit()

async def add_roles_to_db(guild_id: int, menu_name: str, role_id: int, emoji: str = None, description: str = None):
    async with aiosqlite.connect("db/roles.db") as db:
        # Ensure the role menu exists for the specific guild
        await db.execute("INSERT OR IGNORE INTO role_menus (guild_id, menu_name) VALUES (?, ?)", (guild_id, menu_name))
        # Update or insert the role into the menu with emoji and description
        await db.execute("""
            INSERT INTO menu_roles (guild_id, menu_name, role_id, emoji, role_description)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(guild_id, menu_name, role_id) DO UPDATE SET
            emoji = excluded.emoji,
            role_description = excluded.role_description
        """, (guild_id, menu_name, role_id, emoji, description))
        await db.commit()


class RoleMenuDropdown(discord.ui.Select):
    def __init__(self, roles, placeholder, min_values, max_values):
        options = []
        for role in roles:
            emoji = role[1]
            if emoji and emoji.startswith('<:'):
                emoji = discord.PartialEmoji.from_str(emoji)
            option = discord.SelectOption(label=role[0].name, description=role[2], value=str(role[0].id), emoji=emoji)
            options.append(option)
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)
    async def callback(self, interaction: discord.Interaction):
        selected_role_ids = {int(value) for value in self.values}
        current_role_ids = {role.id for role in interaction.user.roles}

        roles_to_add = selected_role_ids - current_role_ids
        roles_to_remove = current_role_ids - selected_role_ids

        roles_added_names = []
        roles_removed_names = []

        for role_id in roles_to_add:
            if role_id == interaction.guild.default_role.id:  # Skip the @everyone role
                continue
            role = interaction.guild.get_role(role_id)
            if role:
                try:
                    await interaction.user.add_roles(role)
                    roles_added_names.append(role.name)
                except discord.NotFound:
                    if interaction.response.is_done():
                        await interaction.followup.send(f"The role {role.name} could not be found.", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"The role {role.name} could not be found.", ephemeral=True)
                except discord.Forbidden:
                    if interaction.response.is_done():
                        await interaction.followup.send("I do not have permission to add roles.", ephemeral=True)
                    else:
                        await interaction.response.send_message("I do not have permission to add roles.", ephemeral=True)

        for role_id in roles_to_remove:
            if role_id == interaction.guild.default_role.id:  # Skip the @everyone role
                continue
            role = interaction.guild.get_role(role_id)
            if role:
                try:
                    await interaction.user.remove_roles(role)
                    roles_removed_names.append(role.name)
                except discord.NotFound:
                    if interaction.response.is_done():
                        await interaction.followup.send(f"The role {role.name} could not be found.", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"The role {role.name} could not be found.", ephemeral=True)
                except discord.Forbidden:
                    if interaction.response.is_done():
                        await interaction.followup.send("I do not have permission to remove roles.", ephemeral=True)
                    else:
                        await interaction.response.send_message("I do not have permission to remove roles.", ephemeral=True)

        messages = []
        if roles_added_names:
            messages.append(f"Roles added: {', '.join(roles_added_names)}")
        if roles_removed_names:
            messages.append(f"Roles removed: {', '.join(roles_removed_names)}")

        if messages:
            if interaction.response.is_done():
                await interaction.followup.send("\n".join(messages), ephemeral=True)
            else:
                await interaction.response.send_message("\n".join(messages), ephemeral=True)
        else:
            if interaction.response.is_done():
                await interaction.followup.send("No changes to your roles were made.", ephemeral=True)
            else:
                await interaction.response.send_message("No changes to your roles were made.", ephemeral=True)


class RoleMenuView(discord.ui.View):
    def __init__(self, roles, placeholder, min_values, max_values):
        super().__init__()
        self.add_item(RoleMenuDropdown(roles, placeholder, min_values, max_values))

class Roles(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    async def fetch_roles_from_db(self, interaction: discord.Interaction, menu_name: str):
        async with aiosqlite.connect("db/roles.db") as db:
            async with db.execute("SELECT role_id, emoji, role_description FROM menu_roles WHERE menu_name = ?", (menu_name,)) as cursor:
                rows = await cursor.fetchall()
                roles = [(interaction.guild.get_role(int(row[0])), row[1], row[2]) for row in rows if interaction.guild.get_role(int(row[0]))]
            async with db.execute("SELECT placeholder, max_values, min_values FROM role_menus WHERE menu_name = ?", (menu_name,)) as cursor:
                menu_settings = await cursor.fetchone()
                settings = {
                    'placeholder': menu_settings[0],
                    'max_values': menu_settings[1],
                    'min_values': menu_settings[2]
                }
        return roles, settings
    
    async def check_role_menu_exists(self, guild_id: int, role_menu_name: str) -> bool:
        async with aiosqlite.connect("db/roles.db") as db:
            async with db.execute("SELECT 1 FROM role_menus WHERE guild_id = ? AND menu_name = ?", (guild_id, role_menu_name)) as cursor:
                return await cursor.fetchone() is not None
            
    async def autocomplete_menuname(self, interaction: discord.Interaction, current: str):
        async with aiosqlite.connect("db/roles.db") as db:
            async with db.execute("SELECT menu_name FROM role_menus WHERE menu_name LIKE ?", ('%' + current + '%',)) as cursor:
                menus = await cursor.fetchall()
        return [app_commands.Choice(name=menu[0], value=menu[0]) for menu in menus]
    
    @app_commands.command(name="roles")
    @app_commands.describe(menuname="Name of the menu to display")
    @app_commands.autocomplete(menuname=autocomplete_menuname)
    async def roles(self, interaction: discord.Interaction, menuname: str):
        roles, settings = await self.fetch_roles_from_db(interaction, menuname)
        if roles and len(roles) >= settings['max_values']:
            view = RoleMenuView(roles, settings['placeholder'], settings['min_values'], settings['max_values'])
            await interaction.response.send_message(f"Select a role from the {menuname} menu:", view=view, ephemeral=True)
        elif roles and len(roles) < settings['max_values']:
            await interaction.response.send_message(f"The menu '{menuname}' requires at least {settings['max_values']} roles to function properly. Please add more roles.", ephemeral=True)
        else:
            await interaction.response.send_message("No roles found for this menu.", ephemeral=True)

    @app_commands.command(name="create_rolemenu")
    @app_commands.describe(menuname="Name of the menu to create", placeholder="Optional placeholder text for the dropdown", max_values="Maximum number of selectable roles or 'max' for all roles", min_values="Minimum number of selectable roles")
    @app_commands.rename(placeholder="placeholder", max_values="max_values", min_values="min_values")
    async def create_rolemenu(self, interaction: discord.Interaction, menuname: str, placeholder: str = "Choose a role...", max_values: str = "1", min_values: int = 0):
        guild_id = interaction.guild.id
        async with aiosqlite.connect("db/roles.db") as db:
            # Check if the menu name already exists in this guild
            cursor = await db.execute("SELECT 1 FROM role_menus WHERE guild_id = ? AND menu_name = ?", (guild_id, menuname))
            exists = await cursor.fetchone()
            if exists:
                await interaction.response.send_message(f"A role menu with the name '{menuname}' already exists in this guild. Please choose a different name.", ephemeral=True)
                return

            if max_values.lower() == "max":
            # Count all roles for this menu in the guild
                cursor = await db.execute("SELECT COUNT(*) FROM menu_roles WHERE guild_id = ? AND menu_name = ?", (guild_id, menuname))
                count = await cursor.fetchone()
                max_values = count[0] if count else 0  # Set to the count of roles or 0 if none
            else:
                try:
                    max_values = max(1, int(max_values))
                except ValueError:
                    await interaction.response.send_message("Invalid input for max_values. Please enter a positive integer or 'max'.", ephemeral=True)
                    return

            min_values = max(0, min(min_values, max_values))

            await db.execute("INSERT INTO role_menus (guild_id, menu_name, placeholder, max_values, min_values) VALUES (?, ?, ?, ?, ?)", (guild_id, menuname, placeholder, max_values, min_values))
            await db.commit()
        await interaction.response.send_message(f"Role menu '{menuname}' created successfully for this guild with placeholder '{placeholder}', max selectable roles: {max_values}, min selectable roles: {min_values}.", ephemeral=True)
    @app_commands.command(name="update_rolemenu")
    async def update_rolemenu(self, interaction: discord.Interaction, role: discord.Role, menuname: str, description: str = None):
        guild_id = interaction.guild.id
        emoji = None  # Placeholder for emoji, to be updated after user reaction

        async with aiosqlite.connect("db/roles.db") as db:
            # Check current max_values setting
            cursor = await db.execute("SELECT max_values FROM role_menus WHERE guild_id = ? AND menu_name = ?", (guild_id, menuname))
            current_max = await cursor.fetchone()
            if current_max and current_max[0] == 0:  # Indicates 'max' was used
                # Count current roles and update max_values
                cursor = await db.execute("SELECT COUNT(*) FROM menu_roles WHERE guild_id = ? AND menu_name = ?", (guild_id, menuname))
                count = await cursor.fetchone()
                new_max_values = count[0] + 1  # Increment as we are adding a new role
                await db.execute("UPDATE role_menus SET max_values = ? WHERE guild_id = ? AND menu_name = ?", (new_max_values, guild_id, menuname))

            # Proceed to add the role
            await add_roles_to_db(guild_id, menuname, role.id, emoji, description)
            await interaction.response.send_message(f"Role {role.name} updated in {menuname} menu. Please react with the emoji you would like to add to this role.")

            # Wait for the emoji reaction
            message = await interaction.original_response()
            def check(reaction, user):
                return user == interaction.user and reaction.message.id == message.id
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                emoji = str(reaction.emoji)
                await db.execute("UPDATE menu_roles SET emoji = ? WHERE menu_name = ? AND guild_id = ? AND role_id = ?", (emoji, menuname, guild_id, role.id))
                await db.commit()
                await interaction.followup.send(f"Emoji {emoji} added for role {role.name} in {menuname} menu.", ephemeral=True)
            except asyncio.TimeoutError:
                await interaction.followup.send("You did not react with an emoji in time.", ephemeral=True)

async def setup(bot:commands.Bot):
    await bot.add_cog(Roles(bot))
    await setup_db()

