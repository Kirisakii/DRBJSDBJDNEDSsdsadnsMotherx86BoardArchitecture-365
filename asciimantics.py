import sys
import curses
import time
from random import randint, choice
from asciimatics.screen import Screen
from asciimatics.effects import Print, Stars, Matrix
from asciimatics.particles import RingFirework, SerpentFirework, StarFirework, PalmFirework
from asciimatics.renderers import FigletText
from asciimatics.scene import Scene
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.event import KeyboardEvent

def startup_animation(screen):
    start_from_final = False  # Flag to determine starting point after resize

    def play_scenes():
        scenes = []
        messages = ["Loading Commands...", "Loading Utilities...", "Loading Fun Modules...", "Loading Event Handlers..."]
        effects = [Matrix(screen, stop_frame=300)]

        # Add a background of stars
        effects.append(Stars(screen, (screen.width * screen.height) // 20, start_frame=0))

        if not start_from_final:
            for i, message in enumerate(messages):
                effects.append(
                    Print(screen,
                          FigletText(message, font='kban'),
                          y=screen.height // 3,
                          start_frame=i * 30,
                          stop_frame=(i + 1) * 30 - 10,
                          clear=True,
                          colour=Screen.COLOUR_YELLOW)
                )

        final_message = "Mother is Ready!"
        final_text = FigletText(final_message, font='big')
        effects.append(
            Print(screen,
                  final_text,
                  y=(screen.height - final_text.max_height) // 2,
                  x=(screen.width - final_text.max_width) // 2,
                  start_frame=(len(messages) + 1) * 30 if not start_from_final else 0,
                  clear=True,
                  colour=Screen.COLOUR_MAGENTA)
        )

        # Add Fireworks effect in a loop
        fireworks = [
            (PalmFirework, 25, 30),
            (StarFirework, 25, 35),
            (RingFirework, 20, 30),
            (SerpentFirework, 30, 35),
        ]
        for start_frame in range((len(messages) + 1) * 30 if not start_from_final else 0, 1000, 50):
            firework, start, stop = choice(fireworks)
            effects.append(
                firework(screen,
                         randint(0, screen.width),
                         randint(int(screen.height // 8), int(screen.height * 3 / 4)),
                         randint(start, stop),
                         start_frame=start_frame,
                         stop_frame=start_frame + 50)
            )

        scenes.append(Scene(effects, -1))
        screen.play(scenes, stop_on_resize=True, repeat=False)

    while True:
        try:
            play_scenes()
            break  # Exit the loop if play_scenes completes without a ResizeScreenError
        except ResizeScreenError:
            screen.clear()
            screen.refresh()  # Refresh the screen setup before replaying
            start_from_final = True  # Set flag to start from final message

def curses_wrapper(stdscr):
    # Initialize curses settings
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Make getch non-blocking
    stdscr.timeout(100)  # Timeout for getch

    # Run asciimatics animation within the curses window
    Screen.wrapper(startup_animation)

if __name__ == "__main__":
    curses.wrapper(curses_wrapper)