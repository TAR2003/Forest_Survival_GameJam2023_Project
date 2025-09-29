"""
Forest Survival - Dialogue System
Modern dialogue system with typewriter effects, choices, and character portraits.
"""

import pygame
import math
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum

import config
from src.core.input_manager import InputManager
from src.core.audio_manager import AudioManager
from src.ui.hud_system import HUDElement


class DialogueState(Enum):
    """Dialogue system states."""
    HIDDEN = "hidden"
    TYPING = "typing"
    WAITING = "waiting"
    CHOOSING = "choosing"
    TRANSITIONING = "transitioning"


class DialogueNode:
    """Single dialogue node with text and choices."""
    
    def __init__(self, text: str, speaker: str = "", choices: List[Dict] = None):
        self.text = text
        self.speaker = speaker
        self.choices = choices or []
        
        # Metadata
        self.node_id = ""
        self.conditions: List[Callable] = []
        self.effects: List[Callable] = []
        self.portrait = None
        self.voice_file = None
        
        # Animation properties
        self.typewriter_speed = 50  # Characters per second
        self.auto_advance_delay = 2.0  # Seconds to wait before auto-advance
        self.allow_skip = True
    
    def can_show(self) -> bool:
        """Check if this node can be shown based on conditions."""
        return all(condition() for condition in self.conditions)
    
    def execute_effects(self):
        """Execute node effects."""
        for effect in self.effects:
            effect()


class DialogueChoice:
    """Dialogue choice option."""
    
    def __init__(self, text: str, next_node: str = "", conditions: List[Callable] = None):
        self.text = text
        self.next_node = next_node
        self.conditions = conditions or []
        self.effects: List[Callable] = []
        
        # Visual properties
        self.disabled = False
        self.color_override = None
    
    def can_select(self) -> bool:
        """Check if this choice can be selected."""
        return not self.disabled and all(condition() for condition in self.conditions)


class DialogueBox(HUDElement):
    """Main dialogue display box."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y, width, height, anchor="bottom_left")
        
        # Visual properties
        self.background_color = config.COLORS['black']
        self.border_color = config.COLORS['cyan']
        self.text_color = config.COLORS['white']
        self.speaker_color = config.COLORS['yellow']
        
        # Text rendering
        self.font = pygame.font.Font(None, 24)
        self.speaker_font = pygame.font.Font(None, 28)
        self.text_margin = 20
        
        # Current display
        self.current_text = ""
        self.displayed_text = ""
        self.speaker_name = ""
        
        # Typewriter effect
        self.typewriter_timer = 0.0
        self.typewriter_speed = 50.0  # Characters per second
        self.typing_complete = False
        
        # Animation
        self.appear_timer = 0.0
        self.slide_offset = 0.0
        self.glow_pulse = 0.0
        
        # Effects
        self.text_shake = 0.0
        self.character_effects: Dict[int, Dict] = {}  # Per-character effects
    
    def set_text(self, text: str, speaker: str = "", typewriter_speed: float = 50.0):
        """Set new text to display with typewriter effect."""
        self.current_text = text
        self.speaker_name = speaker
        self.displayed_text = ""
        self.typewriter_speed = typewriter_speed
        self.typewriter_timer = 0.0
        self.typing_complete = False
        self.character_effects.clear()
        
        # Reset animations
        self.appear_timer = 0.0
        self.slide_offset = self.height
    
    def skip_typing(self):
        """Skip to end of typing animation."""
        if not self.typing_complete:
            self.displayed_text = self.current_text
            self.typing_complete = True
    
    def is_typing(self) -> bool:
        """Check if currently typing."""
        return not self.typing_complete
    
    def _update_animations(self, dt: float):
        """Update dialogue box animations."""
        self.appear_timer += dt
        self.glow_pulse += dt * 2
        
        # Slide in animation
        if self.slide_offset > 0:
            self.slide_offset = max(0, self.slide_offset - 800 * dt)
        
        # Typewriter effect
        if not self.typing_complete:
            self.typewriter_timer += dt
            chars_to_show = int(self.typewriter_timer * self.typewriter_speed)
            
            if chars_to_show >= len(self.current_text):
                self.displayed_text = self.current_text
                self.typing_complete = True
            else:
                self.displayed_text = self.current_text[:chars_to_show]
                
                # Add character effects for special characters
                if chars_to_show > 0:
                    self._add_character_effects(chars_to_show - 1)
        
        # Update character effects
        self._update_character_effects(dt)
        
        # Text shake
        self.text_shake = max(0.0, self.text_shake - dt * 5)
    
    def _add_character_effects(self, char_index: int):
        """Add visual effects for newly typed characters."""
        if char_index >= len(self.current_text):
            return
        
        char = self.current_text[char_index]
        
        # Add bounce effect for punctuation
        if char in "!?.,;:":
            self.character_effects[char_index] = {
                'type': 'bounce',
                'timer': 0.0,
                'intensity': 1.0
            }
        
        # Add glow effect for emphasized text (would be marked up)
        # For now, just add to random characters occasionally
        import random
        if random.random() < 0.1:
            self.character_effects[char_index] = {
                'type': 'glow',
                'timer': 0.0,
                'intensity': 0.8
            }
    
    def _update_character_effects(self, dt: float):
        """Update per-character visual effects."""
        for char_index in list(self.character_effects.keys()):
            effect = self.character_effects[char_index]
            effect['timer'] += dt
            effect['intensity'] = max(0.0, effect['intensity'] - dt * 2)
            
            # Remove expired effects
            if effect['intensity'] <= 0:
                del self.character_effects[char_index]
    
    def add_text_effect(self, effect_type: str, intensity: float = 1.0):
        """Add effect to entire text."""
        if effect_type == "shake":
            self.text_shake = intensity
    
    def render(self, surface: pygame.Surface):
        """Render the dialogue box."""
        if not self.visible:
            return
        
        # Calculate render position with slide animation
        render_rect = self.get_render_rect()
        render_rect.y += self.slide_offset
        
        # Don't render if completely off-screen
        if render_rect.y >= surface.get_height():
            return
        
        # Draw background with transparency
        bg_alpha = int(220 * min(1.0, self.appear_timer / 0.5))
        bg_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
        bg_surface.fill((*self.background_color, bg_alpha))
        surface.blit(bg_surface, render_rect.topleft)
        
        # Draw border with glow
        border_intensity = (math.sin(self.glow_pulse) + 1) / 2
        border_alpha = int(255 * (0.7 + 0.3 * border_intensity))
        border_color = (*self.border_color, border_alpha)
        
        # Create border surface for alpha blending
        border_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, border_color, 
                        pygame.Rect(0, 0, render_rect.width, render_rect.height), 3)
        surface.blit(border_surface, render_rect.topleft)
        
        # Draw speaker name
        if self.speaker_name:
            speaker_y = render_rect.y + 10
            self._draw_speaker_name(surface, render_rect.x + self.text_margin, speaker_y)
        
        # Draw main text
        text_y = render_rect.y + (50 if self.speaker_name else 20)
        self._draw_text(surface, render_rect.x + self.text_margin, text_y, 
                       render_rect.width - self.text_margin * 2, 
                       render_rect.height - text_y + render_rect.y - 20)
        
        # Draw typing indicator
        if self.is_typing():
            self._draw_typing_indicator(surface, render_rect)
        else:
            self._draw_continue_indicator(surface, render_rect)
    
    def _draw_speaker_name(self, surface: pygame.Surface, x: int, y: int):
        """Draw speaker name."""
        speaker_text = f"{self.speaker_name}:"
        speaker_surface = self.speaker_font.render(speaker_text, True, self.speaker_color)
        
        # Add shadow
        shadow_surface = self.speaker_font.render(speaker_text, True, config.COLORS['black'])
        surface.blit(shadow_surface, (x + 2, y + 2))
        surface.blit(speaker_surface, (x, y))
    
    def _draw_text(self, surface: pygame.Surface, x: int, y: int, max_width: int, max_height: int):
        """Draw main dialogue text with word wrapping and effects."""
        if not self.displayed_text:
            return
        
        # Word wrap the text
        wrapped_lines = self._wrap_text(self.displayed_text, max_width)
        
        line_height = self.font.get_height() + 5
        current_y = y
        char_index = 0
        
        for line in wrapped_lines:
            if current_y + line_height > y + max_height:
                break  # Don't draw beyond box
            
            self._draw_text_line(surface, line, x, current_y, char_index)
            current_y += line_height
            char_index += len(line) + 1  # +1 for space/newline
    
    def _draw_text_line(self, surface: pygame.Surface, line: str, x: int, y: int, start_char_index: int):
        """Draw a single line of text with character effects."""
        current_x = x
        
        for i, char in enumerate(line):
            char_index = start_char_index + i
            
            # Calculate shake offset
            shake_x = 0
            shake_y = 0
            if self.text_shake > 0:
                import random
                shake_amount = self.text_shake * 2
                shake_x = random.uniform(-shake_amount, shake_amount)
                shake_y = random.uniform(-shake_amount, shake_amount)
            
            # Check for character-specific effects
            char_offset_y = 0
            char_color = self.text_color
            char_alpha = 255
            
            if char_index in self.character_effects:
                effect = self.character_effects[char_index]
                
                if effect['type'] == 'bounce':
                    bounce_progress = min(1.0, effect['timer'] / 0.3)
                    char_offset_y = -int(10 * math.sin(bounce_progress * math.pi) * effect['intensity'])
                
                elif effect['type'] == 'glow':
                    glow_intensity = effect['intensity']
                    char_color = self._blend_colors(char_color, config.COLORS['yellow'], glow_intensity * 0.5)
            
            # Render character
            char_surface = self.font.render(char, True, char_color)
            char_surface.set_alpha(char_alpha)
            
            # Add shadow for better readability
            shadow_surface = self.font.render(char, True, config.COLORS['black'])
            shadow_surface.set_alpha(char_alpha // 2)
            
            char_x = int(current_x + shake_x)
            char_y = int(y + char_offset_y + shake_y)
            
            surface.blit(shadow_surface, (char_x + 1, char_y + 1))
            surface.blit(char_surface, (char_x, char_y))
            
            current_x += char_surface.get_width()
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_width = self.font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _draw_typing_indicator(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw typing indicator animation."""
        indicator_size = 6
        indicator_x = rect.right - 30
        indicator_y = rect.bottom - 20
        
        # Animated dots
        for i in range(3):
            dot_alpha = int(255 * (math.sin(self.appear_timer * 4 + i * 0.5) + 1) / 2)
            dot_color = (*config.COLORS['cyan'], dot_alpha)
            
            dot_surface = pygame.Surface((indicator_size, indicator_size), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, dot_color, (indicator_size // 2, indicator_size // 2), indicator_size // 2)
            
            surface.blit(dot_surface, (indicator_x + i * (indicator_size + 3), indicator_y))
    
    def _draw_continue_indicator(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw continue indicator."""
        indicator_text = "▼"
        indicator_surface = self.font.render(indicator_text, True, self.border_color)
        
        # Pulsing animation
        pulse_scale = 0.8 + 0.2 * (math.sin(self.appear_timer * 6) + 1) / 2
        if pulse_scale != 1.0:
            scaled_width = int(indicator_surface.get_width() * pulse_scale)
            scaled_height = int(indicator_surface.get_height() * pulse_scale)
            indicator_surface = pygame.transform.scale(indicator_surface, (scaled_width, scaled_height))
        
        indicator_rect = indicator_surface.get_rect()
        indicator_rect.centerx = rect.centerx
        indicator_rect.bottom = rect.bottom - 10
        
        surface.blit(indicator_surface, indicator_rect)
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     progress: float) -> Tuple[int, int, int]:
        """Blend two colors based on progress."""
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)


class ChoicePanel(HUDElement):
    """Panel displaying dialogue choices."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y, width, height, anchor="bottom_right")
        
        # Choices
        self.choices: List[DialogueChoice] = []
        self.selected_index = 0
        self.choice_height = 40
        self.choice_spacing = 5
        
        # Visual properties
        self.background_color = config.COLORS['dark_blue']
        self.border_color = config.COLORS['cyan']
        self.text_color = config.COLORS['white']
        self.selected_color = config.COLORS['yellow']
        self.disabled_color = config.COLORS['gray']
        
        # Font
        self.font = pygame.font.Font(None, 22)
        
        # Animation
        self.slide_timer = 0.0
        self.selection_pulse = 0.0
        self.choice_animations: List[float] = []
    
    def set_choices(self, choices: List[DialogueChoice]):
        """Set the choices to display."""
        self.choices = choices
        self.selected_index = 0
        self.slide_timer = 0.0
        
        # Initialize choice animations
        self.choice_animations = [0.0] * len(choices)
        
        # Adjust height based on number of choices
        total_height = len(choices) * (self.choice_height + self.choice_spacing) + 20
        self.height = total_height
    
    def select_previous(self):
        """Select previous choice."""
        if self.choices:
            old_index = self.selected_index
            self.selected_index = (self.selected_index - 1) % len(self.choices)
            
            # Skip disabled choices
            attempts = 0
            while not self.choices[self.selected_index].can_select() and attempts < len(self.choices):
                self.selected_index = (self.selected_index - 1) % len(self.choices)
                attempts += 1
            
            if old_index != self.selected_index:
                # Play selection sound
                pass
    
    def select_next(self):
        """Select next choice."""
        if self.choices:
            old_index = self.selected_index
            self.selected_index = (self.selected_index + 1) % len(self.choices)
            
            # Skip disabled choices
            attempts = 0
            while not self.choices[self.selected_index].can_select() and attempts < len(self.choices):
                self.selected_index = (self.selected_index + 1) % len(self.choices)
                attempts += 1
            
            if old_index != self.selected_index:
                # Play selection sound
                pass
    
    def get_selected_choice(self) -> Optional[DialogueChoice]:
        """Get currently selected choice."""
        if 0 <= self.selected_index < len(self.choices):
            return self.choices[self.selected_index]
        return None
    
    def _update_animations(self, dt: float):
        """Update choice panel animations."""
        self.slide_timer += dt
        self.selection_pulse += dt * 4
        
        # Update choice slide-in animations
        for i in range(len(self.choice_animations)):
            start_delay = i * 0.1
            if self.slide_timer > start_delay:
                progress = min(1.0, (self.slide_timer - start_delay) / 0.3)
                self.choice_animations[i] = progress
    
    def render(self, surface: pygame.Surface):
        """Render the choice panel."""
        if not self.visible or not self.choices:
            return
        
        render_rect = self.get_render_rect()
        
        # Draw background
        bg_alpha = int(200 * min(1.0, self.slide_timer / 0.5))
        bg_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
        bg_surface.fill((*self.background_color, bg_alpha))
        surface.blit(bg_surface, render_rect.topleft)
        
        # Draw border
        border_alpha = int(255 * min(1.0, self.slide_timer / 0.5))
        pygame.draw.rect(surface, (*self.border_color, border_alpha), render_rect, 2)
        
        # Draw choices
        choice_y = render_rect.y + 10
        
        for i, choice in enumerate(self.choices):
            if i >= len(self.choice_animations):
                continue
            
            # Apply slide animation
            slide_progress = self.choice_animations[i]
            choice_x = render_rect.x + (1.0 - slide_progress) * render_rect.width
            
            choice_rect = pygame.Rect(choice_x, choice_y, render_rect.width, self.choice_height)
            
            # Draw choice background
            if i == self.selected_index:
                # Pulsing selection background
                pulse_alpha = int(100 + 50 * (math.sin(self.selection_pulse) + 1) / 2)
                selected_surface = pygame.Surface((choice_rect.width, choice_rect.height), pygame.SRCALPHA)
                selected_surface.fill((*self.selected_color, pulse_alpha))
                surface.blit(selected_surface, choice_rect.topleft)
            
            # Determine text color
            if not choice.can_select():
                text_color = self.disabled_color
            elif i == self.selected_index:
                text_color = config.COLORS['black']  # Contrast with selected background
            else:
                text_color = self.text_color
            
            # Draw choice text
            choice_text = f"{i + 1}. {choice.text}"
            text_surface = self.font.render(choice_text, True, text_color)
            text_surface.set_alpha(int(255 * slide_progress))
            
            text_rect = text_surface.get_rect()
            text_rect.x = choice_rect.x + 10
            text_rect.centery = choice_rect.centery
            
            surface.blit(text_surface, text_rect)
            
            # Draw selection indicator
            if i == self.selected_index:
                indicator = "►"
                indicator_surface = self.font.render(indicator, True, self.selected_color)
                indicator_surface.set_alpha(int(255 * slide_progress))
                
                indicator_rect = indicator_surface.get_rect()
                indicator_rect.right = choice_rect.right - 10
                indicator_rect.centery = choice_rect.centery
                
                surface.blit(indicator_surface, indicator_rect)
            
            choice_y += self.choice_height + self.choice_spacing


class CharacterPortrait(HUDElement):
    """Character portrait display."""
    
    def __init__(self, x: float, y: float, size: float):
        super().__init__(x, y, size, size, anchor="bottom_left")
        
        # Portrait data
        self.character_name = ""
        self.portrait_image = None
        self.emotion = "neutral"
        
        # Visual properties
        self.background_color = config.COLORS['dark_gray']
        self.border_color = config.COLORS['cyan']
        
        # Animation
        self.emotion_transition = 0.0
        self.speaking_animation = 0.0
        self.is_speaking = False
    
    def set_character(self, name: str, portrait_image=None, emotion: str = "neutral"):
        """Set the character to display."""
        self.character_name = name
        self.portrait_image = portrait_image
        self.emotion = emotion
        self.emotion_transition = 0.0
    
    def set_speaking(self, speaking: bool):
        """Set whether character is currently speaking."""
        self.is_speaking = speaking
    
    def _update_animations(self, dt: float):
        """Update portrait animations."""
        # Speaking animation (subtle movement)
        if self.is_speaking:
            self.speaking_animation += dt * 8
        else:
            self.speaking_animation = 0.0
        
        # Emotion transition
        self.emotion_transition = min(1.0, self.emotion_transition + dt * 3)
    
    def render(self, surface: pygame.Surface):
        """Render the character portrait."""
        if not self.visible:
            return
        
        render_rect = self.get_render_rect()
        
        # Speaking animation offset
        speak_offset = 0
        if self.is_speaking:
            speak_offset = int(2 * math.sin(self.speaking_animation))
        
        render_rect.y += speak_offset
        
        # Draw background
        pygame.draw.rect(surface, self.background_color, render_rect)
        pygame.draw.rect(surface, self.border_color, render_rect, 3)
        
        # Draw portrait image (placeholder for now)
        if self.portrait_image:
            # Would draw actual portrait image here
            pass
        else:
            # Draw placeholder
            placeholder_color = config.COLORS['gray']
            placeholder_rect = render_rect.inflate(-20, -20)
            pygame.draw.rect(surface, placeholder_color, placeholder_rect)
            
            # Draw character initial
            if self.character_name:
                initial = self.character_name[0].upper()
                font = pygame.font.Font(None, 48)
                initial_surface = font.render(initial, True, config.COLORS['white'])
                initial_rect = initial_surface.get_rect(center=placeholder_rect.center)
                surface.blit(initial_surface, initial_rect)
        
        # Draw character name
        if self.character_name:
            name_font = pygame.font.Font(None, 20)
            name_surface = name_font.render(self.character_name, True, config.COLORS['white'])
            name_rect = name_surface.get_rect()
            name_rect.centerx = render_rect.centerx
            name_rect.y = render_rect.bottom + 5
            
            # Name background
            name_bg = name_rect.inflate(10, 4)
            pygame.draw.rect(surface, self.background_color, name_bg)
            pygame.draw.rect(surface, self.border_color, name_bg, 1)
            
            surface.blit(name_surface, name_rect)


class DialogueSystem:
    """
    Main dialogue system managing conversation flow.
    """
    
    def __init__(self, input_manager: InputManager, audio_manager: AudioManager):
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        
        # System state
        self.state = DialogueState.HIDDEN
        self.current_node: Optional[DialogueNode] = None
        self.dialogue_tree: Dict[str, DialogueNode] = {}
        
        # UI Components
        dialogue_box_height = 150
        self.dialogue_box = DialogueBox(20, -dialogue_box_height - 20, 
                                      config.SCREEN_WIDTH - 300, dialogue_box_height)
        
        choice_panel_width = 300
        self.choice_panel = ChoicePanel(-choice_panel_width - 20, -200, 
                                      choice_panel_width, 200)
        
        self.portrait = CharacterPortrait(20, -dialogue_box_height - 140, 100)
        
        # Callbacks
        self.on_dialogue_end: Optional[Callable] = None
        self.on_choice_selected: Optional[Callable] = None
        
        # Settings
        self.auto_advance = False
        self.skip_typing_on_input = True
        
        print("Dialogue system initialized")
    
    def load_dialogue_tree(self, dialogue_data: Dict[str, Any]):
        """Load dialogue tree from data."""
        self.dialogue_tree.clear()
        
        for node_id, node_data in dialogue_data.items():
            node = DialogueNode(
                text=node_data.get('text', ''),
                speaker=node_data.get('speaker', ''),
                choices=node_data.get('choices', [])
            )
            node.node_id = node_id
            
            # Set properties
            node.typewriter_speed = node_data.get('typewriter_speed', 50)
            node.auto_advance_delay = node_data.get('auto_advance_delay', 2.0)
            node.allow_skip = node_data.get('allow_skip', True)
            
            self.dialogue_tree[node_id] = node
    
    def start_dialogue(self, start_node_id: str):
        """Start dialogue from specified node."""
        if start_node_id not in self.dialogue_tree:
            print(f"Warning: Dialogue node '{start_node_id}' not found")
            return
        
        self.current_node = self.dialogue_tree[start_node_id]
        self.state = DialogueState.TYPING
        
        # Show dialogue UI
        self.dialogue_box.visible = True
        self.portrait.visible = True
        
        # Set initial text
        self.dialogue_box.set_text(
            self.current_node.text, 
            self.current_node.speaker,
            self.current_node.typewriter_speed
        )
        
        # Set portrait
        self.portrait.set_character(self.current_node.speaker)
        self.portrait.set_speaking(True)
        
        # Play dialogue start sound
        self.audio_manager.play_sound('dialogue_start', 0, 0, volume=0.6)
        
        # Execute node effects
        self.current_node.execute_effects()
        
        print(f"Started dialogue: {start_node_id}")
    
    def end_dialogue(self):
        """End current dialogue."""
        self.state = DialogueState.HIDDEN
        self.current_node = None
        
        # Hide UI elements
        self.dialogue_box.visible = False
        self.choice_panel.visible = False
        self.portrait.visible = False
        
        # Stop speaking animation
        self.portrait.set_speaking(False)
        
        # Play dialogue end sound
        self.audio_manager.play_sound('dialogue_end', 0, 0, volume=0.4)
        
        # Call callback
        if self.on_dialogue_end:
            self.on_dialogue_end()
        
        print("Dialogue ended")
    
    def advance_dialogue(self):
        """Advance to next part of dialogue."""
        if not self.current_node:
            return
        
        if self.state == DialogueState.TYPING:
            if self.dialogue_box.is_typing() and self.current_node.allow_skip:
                # Skip typing
                self.dialogue_box.skip_typing()
                self.audio_manager.play_sound('click', 0, 0, volume=0.3)
            else:
                # Move to waiting/choosing state
                self._transition_to_next_state()
        
        elif self.state == DialogueState.WAITING:
            self._transition_to_next_state()
        
        elif self.state == DialogueState.CHOOSING:
            # Select current choice
            selected_choice = self.choice_panel.get_selected_choice()
            if selected_choice and selected_choice.can_select():
                self._select_choice(selected_choice)
    
    def _transition_to_next_state(self):
        """Transition to the next dialogue state."""
        if not self.current_node:
            return
        
        if self.current_node.choices:
            # Show choices
            self.state = DialogueState.CHOOSING
            self.choice_panel.set_choices([
                DialogueChoice(choice['text'], choice.get('next_node', ''))
                for choice in self.current_node.choices
            ])
            self.choice_panel.visible = True
            self.portrait.set_speaking(False)
        else:
            # No choices - end dialogue
            self.end_dialogue()
    
    def _select_choice(self, choice: DialogueChoice):
        """Select a dialogue choice."""
        # Execute choice effects
        for effect in choice.effects:
            effect()
        
        # Call callback
        if self.on_choice_selected:
            self.on_choice_selected(choice)
        
        # Play selection sound
        self.audio_manager.play_sound('click', 0, 0, volume=0.5)
        
        # Move to next node or end dialogue
        if choice.next_node and choice.next_node in self.dialogue_tree:
            self._transition_to_node(choice.next_node)
        else:
            self.end_dialogue()
    
    def _transition_to_node(self, node_id: str):
        """Transition to a specific dialogue node."""
        if node_id not in self.dialogue_tree:
            print(f"Warning: Dialogue node '{node_id}' not found")
            self.end_dialogue()
            return
        
        # Hide choices
        self.choice_panel.visible = False
        
        # Set new node
        self.current_node = self.dialogue_tree[node_id]
        self.state = DialogueState.TYPING
        
        # Update dialogue box
        self.dialogue_box.set_text(
            self.current_node.text,
            self.current_node.speaker,
            self.current_node.typewriter_speed
        )
        
        # Update portrait
        self.portrait.set_character(self.current_node.speaker)
        self.portrait.set_speaking(True)
        
        # Execute node effects
        self.current_node.execute_effects()
    
    def navigate_choices(self, direction: int):
        """Navigate dialogue choices (direction: -1 for up, 1 for down)."""
        if self.state != DialogueState.CHOOSING:
            return
        
        if direction < 0:
            self.choice_panel.select_previous()
        else:
            self.choice_panel.select_next()
        
        self.audio_manager.play_sound('ui_move', 0, 0, volume=0.3)
    
    def update(self, dt: float):
        """Update dialogue system."""
        if self.state == DialogueState.HIDDEN:
            return
        
        # Update UI components
        self.dialogue_box.update(dt, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.choice_panel.update(dt, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.portrait.update(dt, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        
        # Auto-advance logic
        if (self.state == DialogueState.WAITING and self.auto_advance and 
            self.current_node and not self.dialogue_box.is_typing()):
            # Auto advance after delay
            if self.dialogue_box.appear_timer > self.current_node.auto_advance_delay:
                self.advance_dialogue()
        
        # Transition from typing to waiting
        if (self.state == DialogueState.TYPING and not self.dialogue_box.is_typing() 
            and not self.current_node.choices):
            self.state = DialogueState.WAITING
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if self.state == DialogueState.HIDDEN:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                self.advance_dialogue()
                return True
            
            elif event.key == pygame.K_ESCAPE:
                self.end_dialogue()
                return True
            
            elif self.state == DialogueState.CHOOSING:
                if event.key == pygame.K_UP:
                    self.navigate_choices(-1)
                    return True
                elif event.key == pygame.K_DOWN:
                    self.navigate_choices(1)
                    return True
                elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                    # Direct choice selection
                    choice_index = event.key - pygame.K_1
                    if 0 <= choice_index < len(self.choice_panel.choices):
                        choice = self.choice_panel.choices[choice_index]
                        if choice.can_select():
                            self.choice_panel.selected_index = choice_index
                            self._select_choice(choice)
                    return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.state in [DialogueState.TYPING, DialogueState.WAITING]:
                    self.advance_dialogue()
                    return True
                elif self.state == DialogueState.CHOOSING:
                    # Check if clicked on a choice
                    # This would need proper mouse hit detection
                    self.advance_dialogue()
                    return True
        
        return False
    
    def render(self, surface: pygame.Surface):
        """Render dialogue system."""
        if self.state == DialogueState.HIDDEN:
            return
        
        # Render components
        self.portrait.render(surface)
        self.dialogue_box.render(surface)
        self.choice_panel.render(surface)
    
    def is_active(self) -> bool:
        """Check if dialogue is currently active."""
        return self.state != DialogueState.HIDDEN
    
    def add_text_effect(self, effect_type: str, intensity: float = 1.0):
        """Add visual effect to dialogue text."""
        self.dialogue_box.add_text_effect(effect_type, intensity)
    
    def set_auto_advance(self, enabled: bool):
        """Enable/disable auto-advance."""
        self.auto_advance = enabled