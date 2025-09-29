"""
Forest Survival - Audio Manager
Advanced audio system with spatial sound, mixing, and dynamic music.
"""

import pygame
import pygame.mixer
import os
from pathlib import Path
from typing import Dict, Optional, List, Any
import random
import math

import config


class SoundChannel:
    """Represents an audio channel with properties."""
    
    def __init__(self, channel_id: int):
        """
        Initialize sound channel.
        
        Args:
            channel_id: Pygame mixer channel ID
        """
        self.channel_id = channel_id
        self.channel = pygame.mixer.Channel(channel_id)
        self.volume = 1.0
        self.category = 'sfx'
        self.sound_name = None
        self.looping = False
    
    def play(self, sound: pygame.mixer.Sound, loops: int = 0, volume: float = 1.0):
        """Play sound on this channel."""
        self.channel.play(sound, loops)
        self.set_volume(volume)
        self.looping = loops != 0
    
    def stop(self):
        """Stop sound on this channel."""
        self.channel.stop()
        self.sound_name = None
        self.looping = False
    
    def set_volume(self, volume: float):
        """Set channel volume."""
        self.volume = max(0.0, min(1.0, volume))
        self.channel.set_volume(self.volume)
    
    def is_busy(self) -> bool:
        """Check if channel is playing sound."""
        return self.channel.get_busy()


class AudioManager:
    """
    Advanced audio manager with spatial sound, dynamic mixing, and music layers.
    """
    
    def __init__(self):
        """Initialize the audio manager."""
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init(
                frequency=config.AUDIO_FREQUENCY,
                channels=config.AUDIO_CHANNELS,
                buffer=config.AUDIO_BUFFER_SIZE
            )
        
        # Audio file cache
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, str] = {}  # name -> file path
        
        # Volume controls
        self.master_volume = config.DEFAULT_VOLUMES['master']
        self.music_volume = config.DEFAULT_VOLUMES['music']
        self.sfx_volume = config.DEFAULT_VOLUMES['sfx']
        self.ambient_volume = config.DEFAULT_VOLUMES['ambient']
        self.ui_volume = config.DEFAULT_VOLUMES['ui']
        
        # Music system
        self.current_music = None
        self.music_layers: Dict[str, Any] = {}
        self.music_crossfade = False
        self.crossfade_duration = 2.0
        
        # Sound channels
        self.channels: List[SoundChannel] = []
        self._init_channels()
        
        # Sound variations
        self.sound_variations: Dict[str, List[str]] = {}
        
        # Audio file paths
        self.audio_dir = config.AUDIO_DIR
        
        # Load audio files
        self._load_audio_files()
        
        print("Audio Manager initialized")
    
    def _init_channels(self):
        """Initialize sound channels."""
        pygame.mixer.set_num_channels(32)  # 32 simultaneous sounds
        
        for i in range(32):
            channel = SoundChannel(i)
            self.channels.append(channel)
    
    def _load_audio_files(self):
        """Load all audio files from the audio directory."""
        if not self.audio_dir.exists():
            print(f"Audio directory not found: {self.audio_dir}")
            return
        
        # Load sound effects
        sound_files = [
            'attack.wav', 'bombsound.wav', 'bounce.wav', 'bulletsound.wav',
            'bunce.wav', 'celebrate.wav', 'click.wav', 'fall.wav',
            'jump.wav', 'levelup.wav', 'monshout.wav', 'monstershout.wav',
            'mont.wav', 'move.wav', 'siren.wav', 'slide.wav',
            'string.wav'
        ]
        
        for sound_file in sound_files:
            file_path = self.audio_dir / sound_file
            if file_path.exists():
                try:
                    sound = pygame.mixer.Sound(str(file_path))
                    sound_name = sound_file.replace('.wav', '')
                    self.sounds[sound_name] = sound
                    print(f"Loaded sound: {sound_name}")
                except pygame.error as e:
                    print(f"Failed to load {sound_file}: {e}")
        
        # Load music tracks
        music_files = ['ingame.wav', 'theme.wav']
        
        for music_file in music_files:
            file_path = self.audio_dir / music_file
            if file_path.exists():
                music_name = music_file.replace('.wav', '')
                self.music_tracks[music_name] = str(file_path)
                print(f"Registered music: {music_name}")
        
        # Set up sound variations
        self._setup_sound_variations()
    
    def _setup_sound_variations(self):
        """Set up sound variations for variety."""
        # Group similar sounds for variation
        if 'monshout' in self.sounds and 'monstershout' in self.sounds:
            self.sound_variations['monster_shout'] = ['monshout', 'monstershout']
        
        if 'bounce' in self.sounds and 'bunce' in self.sounds:
            self.sound_variations['bounce'] = ['bounce', 'bunce']
    
    def play_sound(self, sound_name: str, volume: float = 1.0, 
                   category: str = 'sfx', loops: int = 0, 
                   position: Optional[tuple] = None) -> Optional[SoundChannel]:
        """
        Play a sound effect.
        
        Args:
            sound_name: Name of sound to play
            volume: Volume multiplier (0.0 to 1.0)
            category: Sound category ('sfx', 'ui', 'ambient')
            loops: Number of loops (-1 for infinite)
            position: 2D position for spatial audio
            
        Returns:
            SoundChannel if played successfully, None otherwise
        """
        # Check for sound variations
        if sound_name in self.sound_variations:
            sound_name = random.choice(self.sound_variations[sound_name])
        
        if sound_name not in self.sounds:
            print(f"Sound not found: {sound_name}")
            return None
        
        # Find available channel
        channel = self._get_available_channel(category)
        if not channel:
            print("No available audio channels")
            return None
        
        # Calculate final volume
        category_volume = self._get_category_volume(category)
        final_volume = volume * category_volume * self.master_volume
        
        # Apply spatial audio if position provided
        if position:
            final_volume *= self._calculate_spatial_volume(position)
        
        # Add some random pitch variation (if supported)
        sound = self.sounds[sound_name]
        
        # Play sound
        channel.category = category
        channel.sound_name = sound_name
        channel.play(sound, loops, final_volume)
        
        return channel
    
    def _get_available_channel(self, preferred_category: str = None) -> Optional[SoundChannel]:
        """Get an available sound channel."""
        # First try to find a free channel
        for channel in self.channels:
            if not channel.is_busy():
                return channel
        
        # If no free channels, try to interrupt lower priority sounds
        priority_order = ['ui', 'sfx', 'ambient']
        
        if preferred_category in priority_order:
            # Look for channels playing sounds of lower priority
            preferred_priority = priority_order.index(preferred_category)
            
            for channel in self.channels:
                if channel.category in priority_order:
                    channel_priority = priority_order.index(channel.category)
                    if channel_priority > preferred_priority:
                        channel.stop()
                        return channel
        
        # Last resort: take the first channel
        if self.channels:
            self.channels[0].stop()
            return self.channels[0]
        
        return None
    
    def _get_category_volume(self, category: str) -> float:
        """Get volume multiplier for a category."""
        volume_map = {
            'sfx': self.sfx_volume,
            'ui': self.ui_volume,
            'ambient': self.ambient_volume,
            'music': self.music_volume
        }
        return volume_map.get(category, 1.0)
    
    def _calculate_spatial_volume(self, position: tuple) -> float:
        """
        Calculate volume based on spatial position.
        
        Args:
            position: (x, y) position
            
        Returns:
            Volume multiplier based on distance
        """
        # For now, simple distance-based attenuation
        # Assume listener is at screen center
        screen_center = (960, 540)  # Assuming 1920x1080
        
        distance = math.sqrt(
            (position[0] - screen_center[0]) ** 2 +
            (position[1] - screen_center[1]) ** 2
        )
        
        # Maximum audible distance
        max_distance = 1000
        
        if distance >= max_distance:
            return 0.0
        
        # Linear falloff
        volume_multiplier = 1.0 - (distance / max_distance)
        return max(0.0, volume_multiplier)
    
    def stop_sound(self, sound_name: str):
        """Stop all instances of a specific sound."""
        for channel in self.channels:
            if channel.sound_name == sound_name:
                channel.stop()
    
    def stop_category(self, category: str):
        """Stop all sounds in a category."""
        for channel in self.channels:
            if channel.category == category:
                channel.stop()
    
    def stop_all_sounds(self):
        """Stop all sound effects."""
        for channel in self.channels:
            channel.stop()
    
    def play_music(self, music_name: str, loops: int = -1, fade_in: float = 0.0):
        """
        Play background music.
        
        Args:
            music_name: Name of music track
            loops: Number of loops (-1 for infinite)
            fade_in: Fade in duration in seconds
        """
        if music_name not in self.music_tracks:
            print(f"Music track not found: {music_name}")
            return
        
        music_path = self.music_tracks[music_name]
        
        try:
            if self.current_music and pygame.mixer.music.get_busy():
                if fade_in > 0:
                    pygame.mixer.music.fadeout(int(fade_in * 1000))
                else:
                    pygame.mixer.music.stop()
            
            pygame.mixer.music.load(music_path)
            
            # Set music volume
            music_volume = self.music_volume * self.master_volume
            pygame.mixer.music.set_volume(music_volume)
            
            # Play music
            if fade_in > 0:
                pygame.mixer.music.play(loops, fade_ms=int(fade_in * 1000))
            else:
                pygame.mixer.music.play(loops)
            
            self.current_music = music_name
            print(f"Playing music: {music_name}")
            
        except pygame.error as e:
            print(f"Failed to play music {music_name}: {e}")
    
    def stop_music(self, fade_out: float = 0.0):
        """
        Stop background music.
        
        Args:
            fade_out: Fade out duration in seconds
        """
        if pygame.mixer.music.get_busy():
            if fade_out > 0:
                pygame.mixer.music.fadeout(int(fade_out * 1000))
            else:
                pygame.mixer.music.stop()
        
        self.current_music = None
    
    def set_master_volume(self, volume: float):
        """Set master volume (affects all audio)."""
        self.master_volume = max(0.0, min(1.0, volume))
        
        # Update music volume immediately
        if pygame.mixer.music.get_busy():
            music_volume = self.music_volume * self.master_volume
            pygame.mixer.music.set_volume(music_volume)
        
        # Update all active channels
        for channel in self.channels:
            if channel.is_busy():
                category_volume = self._get_category_volume(channel.category)
                final_volume = channel.volume * category_volume * self.master_volume
                channel.channel.set_volume(final_volume)
    
    def set_music_volume(self, volume: float):
        """Set music volume."""
        self.music_volume = max(0.0, min(1.0, volume))
        
        if pygame.mixer.music.get_busy():
            music_volume = self.music_volume * self.master_volume
            pygame.mixer.music.set_volume(music_volume)
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._update_category_volume('sfx')
    
    def set_ambient_volume(self, volume: float):
        """Set ambient sound volume."""
        self.ambient_volume = max(0.0, min(1.0, volume))
        self._update_category_volume('ambient')
    
    def set_ui_volume(self, volume: float):
        """Set UI sound volume."""
        self.ui_volume = max(0.0, min(1.0, volume))
        self._update_category_volume('ui')
    
    def _update_category_volume(self, category: str):
        """Update volume for all channels in a category."""
        category_volume = self._get_category_volume(category)
        
        for channel in self.channels:
            if channel.category == category and channel.is_busy():
                final_volume = channel.volume * category_volume * self.master_volume
                channel.channel.set_volume(final_volume)
    
    def is_music_playing(self) -> bool:
        """Check if music is currently playing."""
        return pygame.mixer.music.get_busy()
    
    def get_music_position(self) -> float:
        """Get current music position (if supported)."""
        return pygame.mixer.music.get_pos() / 1000.0  # Convert to seconds
    
    def pause_music(self):
        """Pause background music."""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """Resume background music."""
        pygame.mixer.music.unpause()
    
    def add_sound_variation(self, base_name: str, variations: List[str]):
        """
        Add sound variations for variety.
        
        Args:
            base_name: Base sound name to use for random selection
            variations: List of actual sound names to choose from
        """
        self.sound_variations[base_name] = variations
    
    def preload_sound(self, sound_name: str, file_path: str) -> bool:
        """
        Preload a sound file.
        
        Args:
            sound_name: Name to assign to the sound
            file_path: Path to sound file
            
        Returns:
            True if loaded successfully
        """
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[sound_name] = sound
            print(f"Preloaded sound: {sound_name}")
            return True
        except pygame.error as e:
            print(f"Failed to preload {sound_name}: {e}")
            return False
    
    def get_audio_info(self) -> Dict:
        """Get audio system information."""
        return {
            'frequency': pygame.mixer.get_init()[0] if pygame.mixer.get_init() else 0,
            'format': pygame.mixer.get_init()[1] if pygame.mixer.get_init() else 0,
            'channels': pygame.mixer.get_init()[2] if pygame.mixer.get_init() else 0,
            'sounds_loaded': len(self.sounds),
            'music_tracks': len(self.music_tracks),
            'active_channels': sum(1 for c in self.channels if c.is_busy()),
            'current_music': self.current_music,
            'master_volume': self.master_volume
        }
    
    def cleanup(self):
        """Clean up audio resources."""
        self.stop_all_sounds()
        self.stop_music()
        
        # Clear sound cache
        self.sounds.clear()
        self.music_tracks.clear()
        
        print("Audio Manager cleaned up")