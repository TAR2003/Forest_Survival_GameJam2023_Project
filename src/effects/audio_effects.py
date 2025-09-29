"""
Forest Survival - Audio Effects System
Enhanced audio system with 3D positioning, effects, and dynamic mixing.
"""

import pygame
import math
import random
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

import config


class AudioLayer(Enum):
    """Audio layer types for mixing."""
    MASTER = "master"
    MUSIC = "music"
    SFX = "sfx"
    AMBIENT = "ambient"
    UI = "ui"
    VOICE = "voice"


class AudioEnvironment(Enum):
    """Environmental audio presets."""
    FOREST = "forest"
    CAVE = "cave"
    WATER = "water"
    MOUNTAIN = "mountain"
    SWAMP = "swamp"
    MEADOW = "meadow"
    INDOOR = "indoor"


@dataclass
class AudioSource:
    """3D positioned audio source."""
    sound: pygame.mixer.Sound
    x: float
    y: float
    z: float = 0.0
    
    # Audio properties
    base_volume: float = 1.0
    pitch: float = 1.0
    loop: bool = False
    
    # 3D properties
    max_distance: float = 1000.0
    rolloff_factor: float = 1.0
    doppler_factor: float = 1.0
    
    # State
    channel: Optional[pygame.mixer.Channel] = None
    is_playing: bool = False
    is_paused: bool = False
    
    # Effects
    reverb_amount: float = 0.0
    echo_amount: float = 0.0
    distortion_amount: float = 0.0


class AudioEffect:
    """Audio effect processor."""
    
    def __init__(self, effect_type: str):
        self.effect_type = effect_type
        self.enabled = True
        
        # Effect parameters
        self.parameters: Dict[str, float] = {}
        
        # Processing
        self.wet_level = 0.5  # Effect mix level
        self.dry_level = 0.5  # Original signal level
    
    def process(self, audio_data: bytes) -> bytes:
        """Process audio data (placeholder for actual DSP)."""
        # In a real implementation, this would apply DSP effects
        # For now, we'll simulate with volume/pitch changes
        return audio_data
    
    def set_parameter(self, name: str, value: float):
        """Set effect parameter."""
        self.parameters[name] = value


class AudioEnvironmentProcessor:
    """Processes environmental audio effects."""
    
    def __init__(self):
        self.current_environment = AudioEnvironment.FOREST
        self.transition_duration = 2.0
        self.transition_timer = 0.0
        self.is_transitioning = False
        
        # Environment presets
        self.environment_settings = {
            AudioEnvironment.FOREST: {
                'reverb': 0.3,
                'echo': 0.1,
                'high_freq_rolloff': 0.8,
                'ambient_volume': 0.6
            },
            AudioEnvironment.CAVE: {
                'reverb': 0.8,
                'echo': 0.6,
                'high_freq_rolloff': 0.5,
                'ambient_volume': 0.3
            },
            AudioEnvironment.WATER: {
                'reverb': 0.4,
                'echo': 0.3,
                'high_freq_rolloff': 0.9,
                'ambient_volume': 0.7
            },
            AudioEnvironment.MOUNTAIN: {
                'reverb': 0.6,
                'echo': 0.4,
                'high_freq_rolloff': 1.0,
                'ambient_volume': 0.4
            },
            AudioEnvironment.SWAMP: {
                'reverb': 0.5,
                'echo': 0.2,
                'high_freq_rolloff': 0.7,
                'ambient_volume': 0.8
            },
            AudioEnvironment.MEADOW: {
                'reverb': 0.2,
                'echo': 0.05,
                'high_freq_rolloff': 1.0,
                'ambient_volume': 0.5
            },
            AudioEnvironment.INDOOR: {
                'reverb': 0.4,
                'echo': 0.1,
                'high_freq_rolloff': 0.6,
                'ambient_volume': 0.2
            }
        }
        
        # Current settings
        self.current_settings = self.environment_settings[self.current_environment].copy()
        self.target_settings = self.current_settings.copy()
    
    def set_environment(self, environment: AudioEnvironment):
        """Change audio environment with smooth transition."""
        if environment != self.current_environment:
            self.target_settings = self.environment_settings[environment].copy()
            self.is_transitioning = True
            self.transition_timer = 0.0
            self.current_environment = environment
    
    def update(self, dt: float):
        """Update environment processing."""
        if self.is_transitioning:
            self.transition_timer += dt
            progress = min(1.0, self.transition_timer / self.transition_duration)
            
            # Interpolate settings
            for key in self.current_settings:
                start_value = self.current_settings[key]
                target_value = self.target_settings[key]
                self.current_settings[key] = start_value + (target_value - start_value) * progress
            
            if progress >= 1.0:
                self.is_transitioning = False
    
    def get_reverb_level(self) -> float:
        """Get current reverb level."""
        return self.current_settings.get('reverb', 0.0)
    
    def get_echo_level(self) -> float:
        """Get current echo level."""
        return self.current_settings.get('echo', 0.0)
    
    def get_ambient_volume(self) -> float:
        """Get current ambient volume."""
        return self.current_settings.get('ambient_volume', 0.5)


class EnhancedAudioManager:
    """
    Enhanced audio manager with 3D positioning, effects, and dynamic mixing.
    """
    
    def __init__(self):
        # Initialize pygame mixer with better quality
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # Audio layers and volumes
        self.layer_volumes = {
            AudioLayer.MASTER: 1.0,
            AudioLayer.MUSIC: 0.7,
            AudioLayer.SFX: 0.8,
            AudioLayer.AMBIENT: 0.5,
            AudioLayer.UI: 0.6,
            AudioLayer.VOICE: 0.9
        }
        
        # Loaded sounds
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, str] = {}  # name -> file path
        
        # Audio sources
        self.audio_sources: List[AudioSource] = []
        self.ambient_sources: List[AudioSource] = []
        
        # Listener (player) position for 3D audio
        self.listener_x = 0.0
        self.listener_y = 0.0
        self.listener_z = 0.0
        self.listener_direction = 0.0  # Facing direction in radians
        
        # Environmental processing
        self.environment_processor = AudioEnvironmentProcessor()
        
        # Music system
        self.current_music = None
        self.music_volume = 1.0
        self.music_fade_speed = 1.0
        self.music_crossfade_duration = 2.0
        
        # Dynamic range compression
        self.compression_enabled = True
        self.compression_threshold = 0.8
        self.compression_ratio = 4.0
        
        # Ambient loops
        self.ambient_loops: Dict[str, AudioSource] = {}
        
        # Performance
        self.max_concurrent_sounds = 32
        
        print("Enhanced audio manager initialized")
    
    def load_sound(self, filename: str, layer: AudioLayer = AudioLayer.SFX) -> bool:
        """Load a sound file."""
        try:
            full_path = f"audio/{filename}"
            sound = pygame.mixer.Sound(full_path)
            
            # Store with layer information
            sound_key = f"{layer.value}_{filename}"
            self.sounds[sound_key] = sound
            
            print(f"Loaded sound: {filename} (layer: {layer.value})")
            return True
            
        except pygame.error as e:
            print(f"Failed to load sound {filename}: {e}")
            return False
    
    def load_music(self, name: str, filename: str) -> bool:
        """Load a music track."""
        try:
            full_path = f"audio/{filename}"
            self.music_tracks[name] = full_path
            print(f"Loaded music track: {name}")
            return True
            
        except Exception as e:
            print(f"Failed to load music {filename}: {e}")
            return False
    
    def play_sound_3d(self, filename: str, x: float, y: float, z: float = 0.0,
                     layer: AudioLayer = AudioLayer.SFX, volume: float = 1.0,
                     pitch: float = 1.0, loop: bool = False) -> Optional[AudioSource]:
        """Play a sound with 3D positioning."""
        sound_key = f"{layer.value}_{filename}"
        
        if sound_key not in self.sounds:
            print(f"Sound not found: {sound_key}")
            return None
        
        # Check concurrent sound limit
        if len(self.audio_sources) >= self.max_concurrent_sounds:
            # Remove oldest source
            self.audio_sources.pop(0)
        
        # Create audio source
        source = AudioSource(
            sound=self.sounds[sound_key],
            x=x, y=y, z=z,
            base_volume=volume,
            pitch=pitch,
            loop=loop
        )
        
        # Calculate 3D audio properties
        self._update_3d_audio(source)
        
        # Play sound
        try:
            loops = -1 if loop else 0
            channel = source.sound.play(loops=loops)
            
            if channel:
                source.channel = channel
                source.is_playing = True
                
                # Apply 3D volume and panning
                self._apply_3d_effects(source)
                
                self.audio_sources.append(source)
                return source
            
        except pygame.error as e:
            print(f"Failed to play sound: {e}")
        
        return None
    
    def play_sound_2d(self, filename: str, layer: AudioLayer = AudioLayer.SFX,
                     volume: float = 1.0, pitch: float = 1.0, loop: bool = False) -> Optional[AudioSource]:
        """Play a 2D sound (no 3D positioning)."""
        return self.play_sound_3d(filename, self.listener_x, self.listener_y, self.listener_z,
                                 layer, volume, pitch, loop)
    
    def play_music(self, name: str, fade_in_time: float = 0.0, loop: bool = True):
        """Play background music with optional crossfade."""
        if name not in self.music_tracks:
            print(f"Music track not found: {name}")
            return
        
        # Stop current music if playing
        if self.current_music:
            if fade_in_time > 0:
                pygame.mixer.music.fadeout(int(fade_in_time * 1000))
            else:
                pygame.mixer.music.stop()
        
        # Load and play new music
        try:
            pygame.mixer.music.load(self.music_tracks[name])
            
            loops = -1 if loop else 0
            
            if fade_in_time > 0:
                pygame.mixer.music.play(loops=loops, fade_ms=int(fade_in_time * 1000))
            else:
                pygame.mixer.music.play(loops=loops)
            
            # Set volume
            final_volume = self.layer_volumes[AudioLayer.MUSIC] * self.layer_volumes[AudioLayer.MASTER]
            pygame.mixer.music.set_volume(final_volume)
            
            self.current_music = name
            print(f"Playing music: {name}")
            
        except pygame.error as e:
            print(f"Failed to play music {name}: {e}")
    
    def start_ambient_loop(self, name: str, filename: str, x: float, y: float,
                          volume: float = 0.5, max_distance: float = 500.0):
        """Start an ambient audio loop."""
        source = self.play_sound_3d(filename, x, y, 0, AudioLayer.AMBIENT, volume, 1.0, True)
        
        if source:
            source.max_distance = max_distance
            self.ambient_loops[name] = source
    
    def stop_ambient_loop(self, name: str, fade_time: float = 1.0):
        """Stop an ambient audio loop."""
        if name in self.ambient_loops:
            source = self.ambient_loops[name]
            
            if fade_time > 0:
                # Implement fade out (simplified)
                if source.channel:
                    source.channel.fadeout(int(fade_time * 1000))
            else:
                if source.channel:
                    source.channel.stop()
            
            del self.ambient_loops[name]
    
    def set_listener_position(self, x: float, y: float, z: float = 0.0, direction: float = 0.0):
        """Set 3D audio listener position and orientation."""
        self.listener_x = x
        self.listener_y = y
        self.listener_z = z
        self.listener_direction = direction
        
        # Update all 3D audio sources
        for source in self.audio_sources:
            self._update_3d_audio(source)
            self._apply_3d_effects(source)
    
    def _update_3d_audio(self, source: AudioSource):
        """Update 3D audio calculations for a source."""
        # Calculate distance
        dx = source.x - self.listener_x
        dy = source.y - self.listener_y
        dz = source.z - self.listener_z
        
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Calculate volume based on distance
        if distance <= source.max_distance:
            # Inverse square law with rolloff factor
            volume_falloff = 1.0 / (1.0 + source.rolloff_factor * (distance / source.max_distance))
            source.calculated_volume = source.base_volume * volume_falloff
        else:
            source.calculated_volume = 0.0
        
        # Calculate stereo panning
        if distance > 0:
            # Angle relative to listener direction
            angle_to_source = math.atan2(dy, dx)
            relative_angle = angle_to_source - self.listener_direction
            
            # Convert to stereo pan (-1.0 to 1.0)
            source.calculated_pan = math.sin(relative_angle)
        else:
            source.calculated_pan = 0.0
    
    def _apply_3d_effects(self, source: AudioSource):
        """Apply 3D audio effects to a source."""
        if not source.channel:
            return
        
        # Calculate final volume with layer mixing
        layer_volume = self.layer_volumes.get(AudioLayer.SFX, 1.0)  # Default to SFX
        master_volume = self.layer_volumes[AudioLayer.MASTER]
        final_volume = source.calculated_volume * layer_volume * master_volume
        
        # Apply volume
        source.channel.set_volume(min(1.0, max(0.0, final_volume)))
        
        # Note: pygame doesn't support panning directly
        # In a full implementation, you'd use a more advanced audio library
    
    def set_layer_volume(self, layer: AudioLayer, volume: float):
        """Set volume for an audio layer."""
        self.layer_volumes[layer] = max(0.0, min(1.0, volume))
        
        # Update music volume if changed
        if layer in [AudioLayer.MUSIC, AudioLayer.MASTER]:
            final_volume = self.layer_volumes[AudioLayer.MUSIC] * self.layer_volumes[AudioLayer.MASTER]
            pygame.mixer.music.set_volume(final_volume)
    
    def get_layer_volume(self, layer: AudioLayer) -> float:
        """Get volume for an audio layer."""
        return self.layer_volumes.get(layer, 1.0)
    
    def set_environment(self, environment: AudioEnvironment):
        """Set audio environment for environmental effects."""
        self.environment_processor.set_environment(environment)
    
    def play_ui_sound(self, filename: str, volume: float = 1.0):
        """Play a UI sound effect."""
        self.play_sound_2d(filename, AudioLayer.UI, volume)
    
    def play_voice(self, filename: str, volume: float = 1.0):
        """Play a voice clip."""
        self.play_sound_2d(filename, AudioLayer.VOICE, volume)
    
    def create_audio_zone(self, name: str, x: float, y: float, radius: float,
                         ambient_sound: str, volume: float = 0.5):
        """Create an audio zone with ambient sound."""
        # Check if listener is in zone
        distance = math.sqrt((x - self.listener_x)**2 + (y - self.listener_y)**2)
        
        if distance <= radius:
            # Calculate volume based on distance to center
            zone_volume = volume * (1.0 - distance / radius)
            
            if name not in self.ambient_loops:
                self.start_ambient_loop(name, ambient_sound, x, y, zone_volume, radius)
            else:
                # Update existing loop volume
                source = self.ambient_loops[name]
                if source.channel:
                    layer_volume = self.layer_volumes[AudioLayer.AMBIENT]
                    master_volume = self.layer_volumes[AudioLayer.MASTER]
                    final_volume = zone_volume * layer_volume * master_volume
                    source.channel.set_volume(min(1.0, max(0.0, final_volume)))
        else:
            # Outside zone - stop ambient loop
            if name in self.ambient_loops:
                self.stop_ambient_loop(name, 1.0)
    
    def update(self, dt: float):
        """Update audio system."""
        # Update environment processor
        self.environment_processor.update(dt)
        
        # Clean up finished audio sources
        for source in self.audio_sources[:]:
            if source.channel and not source.channel.get_busy():
                source.is_playing = False
                self.audio_sources.remove(source)
        
        # Update 3D audio for all sources
        for source in self.audio_sources:
            if source.is_playing:
                self._update_3d_audio(source)
                self._apply_3d_effects(source)
    
    def pause_all(self):
        """Pause all audio."""
        pygame.mixer.pause()
        pygame.mixer.music.pause()
        
        for source in self.audio_sources:
            source.is_paused = True
    
    def resume_all(self):
        """Resume all audio."""
        pygame.mixer.unpause()
        pygame.mixer.music.unpause()
        
        for source in self.audio_sources:
            source.is_paused = False
    
    def stop_all(self):
        """Stop all audio."""
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        
        self.audio_sources.clear()
        self.ambient_loops.clear()
    
    def get_audio_info(self) -> Dict[str, Any]:
        """Get audio system information."""
        return {
            'active_sources': len(self.audio_sources),
            'ambient_loops': len(self.ambient_loops),
            'current_music': self.current_music,
            'environment': self.environment_processor.current_environment.value,
            'layer_volumes': {layer.value: volume for layer, volume in self.layer_volumes.items()}
        }