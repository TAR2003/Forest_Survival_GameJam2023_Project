"""
Forest Survival - Input Manager
Advanced input handling with rebindable controls and input buffering.
"""

import pygame
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass
from collections import deque
import time

import config


@dataclass
class InputEvent:
    """Represents a buffered input event."""
    action: str
    timestamp: float
    pressed: bool


class InputBuffer:
    """Manages input buffering for responsive controls."""
    
    def __init__(self, buffer_duration: float = 0.1):
        """
        Initialize input buffer.
        
        Args:
            buffer_duration: How long to keep inputs in buffer (seconds)
        """
        self.buffer_duration = buffer_duration
        self.events: deque = deque()
    
    def add_event(self, action: str, pressed: bool):
        """Add an input event to the buffer."""
        event = InputEvent(action, time.time(), pressed)
        self.events.append(event)
    
    def get_buffered_event(self, action: str, max_age: float = None) -> Optional[InputEvent]:
        """
        Get the most recent buffered event for an action.
        
        Args:
            action: Action name to search for
            max_age: Maximum age of event to consider (seconds)
            
        Returns:
            Most recent matching event or None
        """
        max_age = max_age or self.buffer_duration
        current_time = time.time()
        
        # Search from most recent to oldest
        for event in reversed(self.events):
            if event.action == action:
                if current_time - event.timestamp <= max_age:
                    return event
                break  # Found action but too old
        
        return None
    
    def consume_event(self, action: str) -> Optional[InputEvent]:
        """
        Get and remove a buffered event for an action.
        
        Args:
            action: Action name to consume
            
        Returns:
            Most recent matching event or None
        """
        event = self.get_buffered_event(action)
        if event:
            # Remove this specific event from buffer
            try:
                self.events.remove(event)
            except ValueError:
                pass
        return event
    
    def clear_old_events(self):
        """Remove old events from the buffer."""
        current_time = time.time()
        while self.events and current_time - self.events[0].timestamp > self.buffer_duration:
            self.events.popleft()
    
    def clear_action(self, action: str):
        """Clear all events for a specific action."""
        self.events = deque(event for event in self.events if event.action != action)


class InputManager:
    """
    Advanced input manager with rebindable controls, input buffering, and multi-input support.
    """
    
    def __init__(self):
        """Initialize the input manager."""
        # Key bindings
        self.keybinds: Dict[str, int] = config.DEFAULT_KEYBINDS.copy()
        self.reverse_keybinds: Dict[int, str] = {v: k for k, v in self.keybinds.items()}
        
        # Input state tracking
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()
        
        # Action state tracking
        self.actions_pressed: Set[str] = set()
        self.actions_just_pressed: Set[str] = set()
        self.actions_just_released: Set[str] = set()
        
        # Input buffering
        self.input_buffer = InputBuffer(config.JUMP_BUFFER_TIME)
        
        # Mouse state
        self.mouse_pos = (0, 0)
        self.mouse_buttons = [False, False, False]
        self.mouse_just_pressed = [False, False, False]
        self.mouse_just_released = [False, False, False]
        self.mouse_wheel = 0
        
        # Controller support
        self.controllers: List[pygame.joystick.Joystick] = []
        self.controller_enabled = False
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # Timing for held actions
        self.action_hold_times: Dict[str, float] = {}
        
        print("Input Manager initialized")
    
    def set_keybinds(self, keybinds: Dict[str, int]):
        """
        Set new key bindings.
        
        Args:
            keybinds: Dictionary mapping action names to pygame key constants
        """
        self.keybinds = keybinds.copy()
        self.reverse_keybinds = {v: k for k, v in self.keybinds.items()}
        print("Key bindings updated")
    
    def set_keybind(self, action: str, key: int) -> bool:
        """
        Set a single key binding.
        
        Args:
            action: Action name
            key: Pygame key constant
            
        Returns:
            True if binding was set successfully
        """
        if action in self.keybinds:
            # Remove old binding
            old_key = self.keybinds[action]
            if old_key in self.reverse_keybinds:
                del self.reverse_keybinds[old_key]
            
            # Set new binding
            self.keybinds[action] = key
            self.reverse_keybinds[key] = action
            print(f"Rebound {action} to {pygame.key.name(key)}")
            return True
        
        print(f"Unknown action: {action}")
        return False
    
    def get_keybind(self, action: str) -> Optional[int]:
        """Get key binding for an action."""
        return self.keybinds.get(action)
    
    def get_action_for_key(self, key: int) -> Optional[str]:
        """Get action name for a key."""
        return self.reverse_keybinds.get(key)
    
    def handle_event(self, event: pygame.event.Event):
        """
        Handle pygame events and update input state.
        
        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            self._handle_key_down(event.key)
        
        elif event.type == pygame.KEYUP:
            self._handle_key_up(event.key)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_down(event.button)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self._handle_mouse_up(event.button)
        
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        
        elif event.type == pygame.MOUSEWHEEL:
            self.mouse_wheel = event.y
        
        elif event.type == pygame.JOYBUTTONDOWN:
            self._handle_controller_button_down(event.joy, event.button)
        
        elif event.type == pygame.JOYBUTTONUP:
            self._handle_controller_button_up(event.joy, event.button)
        
        # Trigger event callbacks
        self._trigger_event_callbacks(event)
    
    def _handle_key_down(self, key: int):
        """Handle key press."""
        if key not in self.keys_pressed:
            self.keys_just_pressed.add(key)
            self.keys_pressed.add(key)
            
            # Handle action mapping
            action = self.get_action_for_key(key)
            if action:
                self.actions_just_pressed.add(action)
                self.actions_pressed.add(action)
                self.action_hold_times[action] = time.time()
                
                # Add to input buffer
                self.input_buffer.add_event(action, True)
    
    def _handle_key_up(self, key: int):
        """Handle key release."""
        self.keys_pressed.discard(key)
        self.keys_just_released.add(key)
        
        # Handle action mapping
        action = self.get_action_for_key(key)
        if action:
            self.actions_pressed.discard(action)
            self.actions_just_released.add(action)
            self.action_hold_times.pop(action, None)
            
            # Add to input buffer
            self.input_buffer.add_event(action, False)
    
    def _handle_mouse_down(self, button: int):
        """Handle mouse button press."""
        if 1 <= button <= 3:
            index = button - 1
            if not self.mouse_buttons[index]:
                self.mouse_just_pressed[index] = True
                self.mouse_buttons[index] = True
    
    def _handle_mouse_up(self, button: int):
        """Handle mouse button release."""
        if 1 <= button <= 3:
            index = button - 1
            self.mouse_buttons[index] = False
            self.mouse_just_released[index] = True
    
    def _handle_controller_button_down(self, joy_id: int, button: int):
        """Handle controller button press."""
        if self.controller_enabled and joy_id < len(self.controllers):
            # Map controller buttons to actions (simplified)
            action_map = {
                0: 'jump',      # A button
                1: 'slide',     # B button  
                2: 'attack',    # X button
                3: 'shield_toggle'  # Y button
            }
            
            action = action_map.get(button)
            if action:
                self.actions_just_pressed.add(action)
                self.actions_pressed.add(action)
                self.input_buffer.add_event(action, True)
    
    def _handle_controller_button_up(self, joy_id: int, button: int):
        """Handle controller button release."""
        if self.controller_enabled and joy_id < len(self.controllers):
            # Map controller buttons to actions (simplified)
            action_map = {
                0: 'jump',
                1: 'slide',
                2: 'attack',
                3: 'shield_toggle'
            }
            
            action = action_map.get(button)
            if action:
                self.actions_pressed.discard(action)
                self.actions_just_released.add(action)
                self.input_buffer.add_event(action, False)
    
    def _trigger_event_callbacks(self, event: pygame.event.Event):
        """Trigger registered event callbacks."""
        event_type = pygame.event.event_name(event.type)
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")
    
    def update(self, delta_time: float):
        """
        Update input manager state.
        
        Args:
            delta_time: Time since last frame in seconds
        """
        # Clear "just pressed/released" states
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.actions_just_pressed.clear()
        self.actions_just_released.clear()
        
        # Clear mouse "just" states
        self.mouse_just_pressed = [False, False, False]
        self.mouse_just_released = [False, False, False]
        self.mouse_wheel = 0
        
        # Clean up old buffered events
        self.input_buffer.clear_old_events()
    
    def is_action_pressed(self, action: str) -> bool:
        """Check if action is currently pressed."""
        return action in self.actions_pressed
    
    def is_action_just_pressed(self, action: str) -> bool:
        """Check if action was just pressed this frame."""
        return action in self.actions_just_pressed
    
    def is_action_just_released(self, action: str) -> bool:
        """Check if action was just released this frame."""
        return action in self.actions_just_released
    
    def get_action_hold_time(self, action: str) -> float:
        """Get how long an action has been held."""
        if action in self.action_hold_times:
            return time.time() - self.action_hold_times[action]
        return 0.0
    
    def is_buffered_action_available(self, action: str) -> bool:
        """Check if action is available in input buffer."""
        return self.input_buffer.get_buffered_event(action) is not None
    
    def consume_buffered_action(self, action: str) -> bool:
        """
        Consume a buffered action.
        
        Args:
            action: Action to consume
            
        Returns:
            True if action was available and consumed
        """
        event = self.input_buffer.consume_event(action)
        return event is not None and event.pressed
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if key is currently pressed."""
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key: int) -> bool:
        """Check if key was just pressed this frame."""
        return key in self.keys_just_pressed
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if mouse button is pressed (1=left, 2=middle, 3=right)."""
        if 1 <= button <= 3:
            return self.mouse_buttons[button - 1]
        return False
    
    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """Check if mouse button was just pressed."""
        if 1 <= button <= 3:
            return self.mouse_just_pressed[button - 1]
        return False
    
    def get_mouse_position(self) -> tuple:
        """Get current mouse position."""
        return self.mouse_pos
    
    def get_mouse_wheel(self) -> int:
        """Get mouse wheel scroll direction (positive=up, negative=down)."""
        return self.mouse_wheel
    
    def register_event_callback(self, event_type: str, callback: Callable):
        """
        Register callback for specific event type.
        
        Args:
            event_type: Pygame event type name
            callback: Callback function
        """
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    def unregister_event_callback(self, event_type: str, callback: Callable):
        """Unregister event callback."""
        if event_type in self.event_callbacks:
            try:
                self.event_callbacks[event_type].remove(callback)
            except ValueError:
                pass
    
    def enable_controller_support(self):
        """Enable and initialize controller support."""
        pygame.joystick.init()
        self.controllers.clear()
        
        for i in range(pygame.joystick.get_count()):
            try:
                controller = pygame.joystick.Joystick(i)
                controller.init()
                self.controllers.append(controller)
                print(f"Controller {i} connected: {controller.get_name()}")
            except pygame.error as e:
                print(f"Failed to initialize controller {i}: {e}")
        
        self.controller_enabled = len(self.controllers) > 0
        return self.controller_enabled
    
    def disable_controller_support(self):
        """Disable controller support."""
        for controller in self.controllers:
            controller.quit()
        self.controllers.clear()
        self.controller_enabled = False
        pygame.joystick.quit()
    
    def clear_input_buffer(self):
        """Clear all buffered inputs."""
        self.input_buffer = InputBuffer(config.JUMP_BUFFER_TIME)
    
    def get_input_summary(self) -> Dict:
        """Get current input state summary for debugging."""
        return {
            'keys_pressed': len(self.keys_pressed),
            'actions_pressed': list(self.actions_pressed),
            'buffered_events': len(self.input_buffer.events),
            'mouse_pos': self.mouse_pos,
            'controllers': len(self.controllers),
            'controller_enabled': self.controller_enabled
        }