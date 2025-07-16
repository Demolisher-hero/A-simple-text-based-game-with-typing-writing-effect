# -*- coding: utf-8 -*-
"""
A text-based adventure game built with Pygame.

The player navigates a branching story by making choices, with the narrative
displayed using a typewriter effect. The game features a flexible story tree
structure that can be easily expanded.

Controls:
- 1, 2, 3...: Make a choice
- SPACE:      Skip the current text animation
- F4:         Toggle fullscreen mode
- F1 / ESC:   Quit the game
"""

import pygame
import sys
import os

# --- Constants ---
# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 255) # Using a bright cyan for better visibility
GOLD = (255, 215, 0)
GREY = (150, 150, 150)

# Fonts
PRIMARY_FONT = "Courier New"

# --- TypewriterText Class (Handles text display and animation) ---
class TypewriterText:
    """
    Manages rendering text with a typewriter effect, including word wrapping,
    scrolling, sound, and simple text formatting.
    """
    def __init__(self, text, font, pos, max_width, max_height, delay=25, color=WHITE, sound=None):
        """
        Initializes the TypewriterText object.

        Args:
            text (str): The full text to be displayed.
            font (pygame.font.Font): The font used for rendering text.
            pos (tuple): The (x, y) position of the top-left corner of the text area.
            max_width (int): The maximum width for a line of text before wrapping.
            max_height (int): The maximum height of the text display area.
            delay (int): Milliseconds between each character appearing.
            color (tuple): The RGB color of the text.
            sound (pygame.mixer.Sound, optional): Sound to play for each character.
        """
        self.font = font
        self.pos = pos
        self.max_width = max_width
        self.max_height = max_height
        self.delay = delay
        self.color = color
        self.sound = sound
        self.typing_channel = pygame.mixer.Channel(1) if self.sound else None
        self.full_text = ""
        self.current_index = 0
        self.last_update = 0
        self.set_text(text)

    def set_text(self, text):
        """Resets the typewriter with new text."""
        self.full_text = text
        self.current_index = 0
        self.last_update = pygame.time.get_ticks()
        if self.typing_channel:
            self.typing_channel.stop()

    def play_typing_sound(self):
        """Plays the typing sound if it's not already playing."""
        if self.sound and self.typing_channel and not self.typing_channel.get_busy():
            self.typing_channel.play(self.sound)

    def update(self):
        """Updates the visible text based on the time elapsed."""
        now = pygame.time.get_ticks()
        if not self.is_finished() and now - self.last_update > self.delay:
            self.last_update = now
            self.current_index += 1
            self.play_typing_sound()
        if self.is_finished() and self.typing_channel:
            self.typing_channel.stop()

    def wrap_text(self, text):
        """Wraps a string of text to fit within the max_width."""
        wrapped_lines = []
        # Split by explicit newlines first to preserve paragraph breaks
        for paragraph in text.split('\n'):
            if not paragraph.strip():
                wrapped_lines.append("")
                continue

            words = paragraph.split(' ')
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if self.font.size(test_line)[0] <= self.max_width:
                    current_line = test_line
                else:
                    wrapped_lines.append(current_line)
                    current_line = word
            wrapped_lines.append(current_line)
        return wrapped_lines

    def draw_line_with_formatting(self, surface, line, base_x, y, center=False):
        """
        Draws a single line of text, handling special formatting.
        Currently hardcoded to color "14 years" in red.
        """
        if "14 years" in line:
            segments = line.split("14 years")
            rendered_segments = [self.font.render(seg, True, self.color) for seg in segments]
            red_segment = self.font.render("14 years", True, RED)
            
            total_width = sum(seg.get_width() for seg in rendered_segments) + red_segment.get_width() * (len(segments) - 1)
            
            current_x = base_x
            if center:
                current_x = base_x + (self.max_width - total_width) // 2

            for i, seg_surface in enumerate(rendered_segments):
                surface.blit(seg_surface, (current_x, y))
                current_x += seg_surface.get_width()
                if i < len(segments) - 1:
                    surface.blit(red_segment, (current_x, y))
                    current_x += red_segment.get_width()
        else:
            rendered = self.font.render(line, True, self.color)
            x = base_x
            if center:
                x = base_x + (self.max_width - rendered.get_width()) // 2
            surface.blit(rendered, (x, y))

    def draw(self, surface):
        """Renders the typewriter text and cursor onto the given surface."""
        current_text_segment = self.full_text[:self.current_index]
        lines = self.wrap_text(current_text_segment)
        line_spacing = self.font.get_linesize()

        total_text_height = len(lines) * line_spacing
        x, y_start_area = self.pos

        # Calculate starting Y position to create a scrolling effect
        start_y = y_start_area
        if total_text_height > self.max_height:
            start_y = y_start_area + self.max_height - total_text_height

        # Draw each visible line
        for i, line in enumerate(lines):
            line_y = start_y + i * line_spacing
            
            # Only draw lines that are within the visible text area
            if y_start_area <= line_y < y_start_area + self.max_height:
                center_line = (i == 0 and line.strip().startswith("Chapter"))
                self.draw_line_with_formatting(surface, line, x, line_y, center_line)
                
        # Draw blinking cursor at the end of the text
        if not self.is_finished() and (pygame.time.get_ticks() // 500) % 2 == 0:
            last_line_text = lines[-1] if lines else ""
            cursor_x = x + self.font.size(last_line_text)[0]
            cursor_y = start_y + (len(lines) - 1) * line_spacing
            
            if y_start_area <= cursor_y < y_start_area + self.max_height:
                surface.blit(self.font.render('_', True, self.color), (cursor_x, cursor_y))

    def complete(self):
        """Instantly finishes the text animation."""
        self.current_index = len(self.full_text)
        if self.typing_channel:
            self.typing_channel.stop()

    def is_finished(self):
        """Returns True if the entire text has been revealed."""
        return self.current_index >= len(self.full_text)

def main():
    """Main function to initialize Pygame and run the game loop."""
    # --- Game Setup ---
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chapter 1: The Awakening")
    clock = pygame.time.Clock()
    
    # Load fonts
    font = pygame.font.SysFont(PRIMARY_FONT, 24)
    small_font = pygame.font.SysFont(PRIMARY_FONT, 18)

    # Load typing sound (optional)
    # Load typing sound (optional)
    typing_sound = None
    try:
        # Create a reliable path to the sound file relative to the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sound_path = os.path.join(script_dir, "assets", "mixkit-fast-laptop-keyboard-typing-1392.wav")
        if os.path.exists(sound_path):
            typing_sound = pygame.mixer.Sound(sound_path)
        else:
            print(f"Warning: Sound file not found at '{sound_path}'.")
    except pygame.error as e:
        print(f"Warning: Could not load typing sound. Game will run without it. Error: {e}")

    # Define text area dimensions
    text_area_rect = pygame.Rect(10, 30, 780, 300)
    text_margin = 10
    text_max_width = text_area_rect.width - 2 * text_margin
    text_max_height = text_area_rect.height - 2 * text_margin

    # --- Story Data ---
    # The game's story is stored in a dictionary. Each key is a unique node ID.
    # Each node has 'text' and a list of 'choices'.
    # The next node's ID is generated from the current ID and the choice index.
    # e.g., from node '1', choosing the 2nd option leads to node '1_2'.
    # Nodes with an empty 'choices' list are endings.
    initial_story = ("Chapter 1: The Awakening\n\n"
                     "You are playing a newly released game in a dark, silent room. It's your deserved reward after all.\n"
                     "You waited 14 years for it. Now it is finally available in your hand. Enjoying it is your virtue.\n"
                     "But some noise starts coming apart, disturbing your joy in the process.")
    
    choices_tree = {
        "start": {
            "text": initial_story,
            "choices": ["Investigate the noise", "Ignore it"]
        },
        "1": { # Investigate the noise
            "text": "You chose to investigate the noise. It becomes more static, giving eerie vibes and it grows louder.\nDo you really want to investigate the sound or call someone?",
            "choices": ["Yes, these things don't scare me anymore.", "Call someone for help"]
        },
        "2": { # Ignore it
            "text": "You chose to ignore the noise. You enjoy the loading screen and one specific picture.\nNoise from outside starts growing?\nDo you want to investigate the sound or keep playing anyway?",
            "choices": ["Ahh! So irritating", "Keep playing anyway"]
        },
        "1_1": { # Investigate -> Yes, these things don't scare me anymore.
            "text": "You move forward, braver now. After all, it's your home. If you don't protect it, who will? Bracing yourself, you cross the hallway to the door. There you see your coat hanging on a metal hanger.",
            "choices": ["Wear coat", "Wear coat and take metal hanger as weapon", "Just enter"]
        },
        "1_2": { # Investigate -> Call someone for help
            "text": "You try to call someone, but there's no signal. You're confused—the signal is always strong in this room.",
            "choices": ["Investigate the sound by yourself", "Go back and try again with your PC"]
        },
        "2_1": { # Ignore -> Ahh! So irritating
            "text": "You stand up angrily. Irritated by the noise, you grab a nearby flashlight and the beer bottle you were about to enjoy with your game.",
            "choices": ["Rush the hallway", "Walk the hallway in a normal pace"]
        },
        "2_2": { # Ignore -> Keep playing anyway
            "text": "You keep playing. Now you control the playable character.",
            "choices": ["Punch an NPC", "Do a mission in the game"]
        },
        "1_1_1": { # Investigate -> Yes -> Wear coat
            "text": "You wear the coat. It feels heavier than usual, but provides a small sense of security. You grip the doorknob. It's strangely cold, almost unnaturally so as you slowly turn it. The noise on the other side stops abruptly. The silence is now even more terrifying than the noise was.",
            "choices": ["fling the door open.", "Open the door slowly and peek.", "Call out,'Who's there?"]
        },
        "1_1_2": { # Investigate -> Yes -> Wear coat and take metal hanger as weapon
            "text": "You wear the coat and rip the metal hanger off the hook. You bend it into a crude, sharp point. It feels better than nothing. You grip the doorknob. It's strangely cold, almost unnaturally so as you slowly turn it. The noise on the other side stops abruptly.",
            "choices": ["fling the door open.", "Open the door slowly and peek.", "Call out, 'Who's there?'"]
        },
        "1_1_3": { # Investigate -> Yes -> Just enter
            "text": "You decide to face whatever is there with your undies that you were wearing. You slowly, silently, turn the knob slowly which felt strangely cold and the noise beyond the door stop suddenly.",
            "choices": ["Push the door fully open.", "Close the door and reconsider."]
        },
        "1_2_1": { # Investigate -> Call -> Investigate by yourself
            "redirect": "1_1" # This redirect effectively takes you to the content of node "1_1"
        },
        "1_2_2": { # Investigate -> Call -> Go back and try again with your PC
            "text": "You decide this is too strange. You go back to your PC, You cancel the game that you were so desperate to play but you didn't download from offical website so you were redirected to a porn site.",
            "choices": ["Try to close the porn site.", "Enjoy it afterall who is looking?", "Force shutdown the pc"]
        },
        "2_1_1": { # Ignore -> Irritated -> Rush the hallway
            "text": "Fueled by annoyance, you rush down the hallway, flashlight beam bouncing wildly. You round the corner to the hallway and kicks open the door and the light falls on a oddly figure. It's tall, unnaturally thin, and turns its head towards you with an audible crack of neck.",
            "choices": ["Throw the beer bottle at it.", "Freeze and stare in it eyes."]
        },
        "2_1_2": { # Ignore -> Irritated -> Walk the hallway in a normal pace
            "text": "You walk calmly, flashlight off, using the dim moonlight to see. The noise is a rhythmic scraping coming from the outside of hallway room. You open the door and light falls on a oddly figure. It's tall, unnaturally thin, and turns its head towards you with an audible crack of neck.",
            "choices": ["Flick on the flashlight to startle it.", "Quietly back away."]
        },
        "2_2_1": { # Ignore -> Keep playing -> Punch an NPC
            "text": "Every start of a game of Gta,we always punch a npc to celebrate the download of the game and so you did it. Keeping the tradition alive.",
            "choices": ["Punch even more npc?", "Investigate the sound that irritating you?"]
        },
        "2_2_2": { # Ignore -> Keep playing -> Do a mission in the game
            "text": "You ignore the real-world noise and focus on the game. The quest-giver, a mafia, looks at you, but his dialogue box says, 'Gang B is has stolen ours supplies recover it or you dead' The text is bright red",
            "choices": ["Kill the Npc.", "Ask the NPC a question in-game.","Investigate the sound that irritating you?"]
        },
        "1_1_1_1":{ # Investigate -> Yes -> Wear coat -> fling the door open
            "text": "You throw the door open to an empty living room. You hear rough breathing sound towards a certain direction.",
            "choices": ["Flash your flashlight towards it.","throw the flashlight at it.","Scream at it."]
        },
        "1_1_1_2": { # Investigate -> Yes -> Wear coat -> Open the door slowly and peek
            "text":"You peek out. Closing your flashlight so you can be like an assassin. You open the door slowly.",
            "choices": ["Crawl on the surface.","Crouch on the surface and walk","Walk in this situation."]
        },
        "1_1_1_3":{ # Investigate -> Yes -> Wear coat -> 'Who's there?
            "text": "Your voice echoes in the silent house. There is no reply.",
            "choices": ["Flash your flashlight at random direction","Shout once again","Go back inside"]
        },
        "1_1_2_1":{ # Investigate -> Yes -> Wear coat and take metal hanger as weapon ->fling the door open.
            "text": "You burst through the door with a war cry and enters the living room while flashing the light falls on an oddly figure. It's tall, unnaturally thin, and turns its head towards you with an audible crack of neck.",
            "choices": ["Flash your flashlight on it.","Throw the nearby chair at it","Try to talk with it"]
        },
        "1_1_2_2":{ # Investigate -> Yes -> Wear coat and take metal hanger as weapon -> Open the door slowly and peek.
            "text": "Holding your makeshift weapon in your hand you cautiously turn the doorknob, peeking through the door as cautiously as possible.\n\nWhat would you do next?",
            "choices": ["Crawl on the surface.","Crouch on the surface and walk","Walk in this situation."]
        },
        "1_1_2_3": { # Investigate -> Yes -> Wear coat and take metal hanger as weapon -> Call out,'Who's there?
            "text": "After opening the door. You call out by saying, 'Who's there? If you are a thief, you picked the wrong house, mate. I will call the police in a few seconds. You hear me, mate?'",
            "choices": ["Wait for the response","Start calling the police","Step more forward with your flashlight."]
        },
        "1_1_3_1": { # Investigate -> Yes -> Just enter -> Push the door fully open.
            "text": "You push the door open proudly. You don't need a weapon to respond to such danger or anything. Flashing your light, you see an oddly figure. It's tall and unnaturally thin. Turning its head slowly towards the direction of the light.",
            "choices": ["'Who are you?' or 'What are you?'","Give a 'War cry'","Just go back inside"]
        },
        "1_1_3_2": { # Investigate -> Yes -> Just enter -> Close the door and reconsider.
            "text": "You got an awakening and finally your one brain cell thought: 'Is it really okay to fight in my undies?'",
            "choices": ["Wear the coat", "Wear coat and take metal hanger as weapon", "Just enter (again)"]
        }
    }

    # --- Game State Variables ---
    game_state = "narrative"  # Can be 'narrative', 'choice', or 'ending'
    current_node_key = "start"
    
    typewriter = TypewriterText(
        choices_tree[current_node_key]["text"], font,
        (text_area_rect.x + text_margin, text_area_rect.y + text_margin),
        text_max_width, text_max_height,
        delay=30, color=WHITE, sound=typing_sound
    )

    # --- Main Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_F1):
                    running = False
                elif event.key == pygame.K_F4:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_SPACE and game_state == "narrative":
                    typewriter.complete()

                # Handle numeric choices (1-9)
                if game_state == "choice":
                    choice_index = -1
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        choice_index = event.key - pygame.K_1

                    current_choices = choices_tree.get(current_node_key, {}).get("choices", [])
                    if 0 <= choice_index < len(current_choices):
                        # Determine the next node key
                        if current_node_key == "start":
                            next_key = str(choice_index + 1)
                        else:
                            next_key = f"{current_node_key}_{choice_index + 1}"
                        
                        # Find and process the next node
                        if next_key in choices_tree:
                            target_node = choices_tree[next_key]
                            
                            # Handle redirects
                            if "redirect" in target_node:
                                current_node_key = target_node["redirect"]
                            else:
                                current_node_key = next_key
                            
                            # Set new text and state
                            new_text = choices_tree[current_node_key].get("text", "The story ends here.")
                            typewriter.set_text(new_text)
                            
                            if choices_tree[current_node_key].get("choices"):
                                game_state = "narrative"
                            else:
                                game_state = "ending"
                        else:
                            # If key doesn't exist, it's an unwritten ending
                            typewriter.set_text("This path has not been written yet. The story ends here.")
                            game_state = "ending"

        # --- Game Logic / State Transitions ---
        typewriter.update()
        
        if game_state == "narrative" and typewriter.is_finished():
            game_state = "choice"

        # --- Drawing ---
        screen.fill(BLACK)
        typewriter.draw(screen)

        # Draw choices when available
        if game_state == "choice":
            choices = choices_tree.get(current_node_key, {}).get("choices", [])
            if choices:
                header = small_font.render("What will you do?", True, GOLD)
                screen.blit(header, (20, text_area_rect.bottom + 20))
                for i, choice in enumerate(choices):
                    choice_text = f"{i + 1}. {choice}"
                    rendered = small_font.render(choice_text, True, GREEN)
                    screen.blit(rendered, (40, text_area_rect.bottom + 50 + i * 30))

        # Draw ending message
        if game_state == "ending":
            ending_message = "The story has ended. Press F1 or ESC to exit."
            ending_surface = small_font.render(ending_message, True, GREY)
            screen.blit(ending_surface, (WIDTH // 2 - ending_surface.get_width() // 2, HEIGHT - 100))
        
        # Draw instructions at the bottom
        instruction_text = "SPACE to skip | F4 for fullscreen | F1/ESC to exit"
        instruction_surface = small_font.render(instruction_text, True, GREY)
        screen.blit(instruction_surface, (20, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
