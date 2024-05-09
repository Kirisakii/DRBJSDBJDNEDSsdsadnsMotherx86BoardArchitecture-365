import os
from colorama import init, Fore, Style

def fetch_documentation_files(directory="documentation"):
    files = os.listdir(directory)
    command_files = {}
    for file in files:
        # Remove file extension and replace underscores with spaces for the key
        command_key = file.replace(".txt", "").replace("_", " ")
        command_files[command_key] = file
    return command_files

# Usage
documentation_files = fetch_documentation_files()

# Print each item on a new line in a structured format
# for command, filename in documentation_files.items():
#     print(f'"{command}": "{filename}",')


command_files = {
    "add button": "add_button.txt",
    "advice": "advice.txt",
    "cat": "cat.txt",
    "choose": "choose.txt",
    "connect4": "connect4.txt",
    "create category": "create_category.txt",
    "create channel": "create_channel.txt",
    "create color role": "create_color_role.txt",
    "create role": "create_role.txt",
    "create rolemenu": "create_rolemenu.txt",
    "dadjoke": "dadjoke.txt",
    "delete button": "delete_button.txt",
    "delete embed": "delete_embed.txt",
    "delete role": "delete_role.txt",
    "dog": "dog.txt",
    "edit embed": "edit_embed.txt",
    "embed add field": "embed_add_field.txt",
    "embed builder": "embed_builder.txt",
    "embed edit field": "embed_edit_field.txt",
    "emoji enlarge": "emoji enlarge.txt",
    "emoji steal": "emoji steal.txt",
    "emojify": "emojify.txt",
    "flag statistics": "flag statistics.txt",
    "flags game": "flags game.txt",
    "flags leaderboard": "flags leaderboard.txt",
    "generate roles": "generate_roles.txt",
    "kick": "kick.txt",
    "move category": "move_category.txt",
    "my buttons": "my_buttons.txt",
    "my embeds": "my_embeds.txt",
    "purge": "purge.txt",
    "quick embed": "quick_embed.txt",
    "quick server setup": "quick_server_setup.txt",
    "remove all roles": "remove_all_roles.txt",
    "remove field": "remove_field.txt",
    "reset": "reset.txt",
    "reverse": "reverse.txt",
    "roles": "roles.txt",
    "send through webhook": "send_through_webhook.txt",
    "setup flag channel": "setup_flag_channel.txt",
    "show": "show.txt",
    "timer": "timer.txt",
    "update rolemenu": "update_rolemenu.txt",
    "would you rather": "would you rather.txt",
    "wyr": "wyr.txt",
    }

mother_ascii_art = """

▪   ▐ ▄ ▪  ▄▄▄▄▄▪   ▄▄▄· ▄▄▌  ▪  ·▄▄▄▄•▪   ▐ ▄  ▄▄ •     • ▌ ▄ ·.       ▄▄▄▄▄ ▄ .▄▄▄▄ .▄▄▄  
██ •█▌▐███ •██  ██ ▐█ ▀█ ██•  ██ ▪▀·.█▌██ •█▌▐█▐█ ▀ ▪    ·██ ▐███▪▪     •██  ██▪▐█▀▄.▀·▀▄ █·
▐█·▐█▐▐▌▐█· ▐█.▪▐█·▄█▀▀█ ██▪  ▐█·▄█▀▀▀•▐█·▐█▐▐▌▄█ ▀█▄    ▐█ ▌▐▌▐█· ▄█▀▄  ▐█.▪██▀▐█▐▀▀▪▄▐▀▀▄ 
▐█▌██▐█▌▐█▌ ▐█▌·▐█▌▐█ ▪▐▌▐█▌▐▌▐█▌█▌▪▄█▀▐█▌██▐█▌▐█▄▪▐█    ██ ██▌▐█▌▐█▌.▐▌ ▐█▌·██▌▐▀▐█▄▄▌▐█•█▌
▀▀▀▀▀ █▪▀▀▀ ▀▀▀ ▀▀▀ ▀  ▀ .▀▀▀ ▀▀▀·▀▀▀ •▀▀▀▀▀ █▪·▀▀▀▀     ▀▀  █▪▀▀▀ ▀█▄▀▪ ▀▀▀ ▀▀▀ · ▀▀▀ .▀  ▀
        """

from asciimatics.effects import BannerText
from asciimatics.renderers import ColourImageFile
from asciimatics.scene import Scene
from asciimatics.screen import Screen

def demo(screen):
    scenes = []
    effects = [
        BannerText(screen, ColourImageFile(screen, "botpromo.png", screen.height), colour=7),  # 7 represents white color
    ]
    scenes.append(Scene(effects, -1))
    screen.play(scenes, repeat=False)

Screen.wrapper(demo)



