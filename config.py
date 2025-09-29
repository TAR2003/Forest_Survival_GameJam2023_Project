"""
Forest Survival - Game Configuration
Central configuration file for all game constants and settings.
"""

import pygame
from pathlib import Path
from typing import Tuple, Dict, Any

# ===== GAME METADATA =====
GAME_TITLE = "Forest Survival"
VERSION = "2.0.0"
DEVELOPER = "Forest Studios"
DESCRIPTION = "A production-ready 2D action-survival platformer"

# ===== DISPLAY SETTINGS =====
DEFAULT_RESOLUTION = (1920, 1080)
MIN_RESOLUTION = (1280, 720)
SUPPORTED_RESOLUTIONS = [
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
    (2560, 1440),
    (3840, 2160)
]

FPS_TARGET = 60
VSYNC_DEFAULT = True

# ===== GAME MECHANICS =====
PLAYER_START_HEALTH = 3
PLAYER_MAX_HEALTH = 5
PLAYER_START_POSITION = (200, 670)
GRAVITY = 2
JUMP_STRENGTH = -30

# Shield system
SHIELD_POSITIONS = {
    'top': 470,
    'middle': 530,
    'bottom': 600
}

# ===== SCORING SYSTEM =====
POINTS_PER_SECOND = 1
POINTS_ENEMY_KILL = 10
POINTS_PERFECT_BLOCK = 50
POINTS_COMBO_MULTIPLIER = [1.0, 1.5, 2.0, 3.0, 5.0]

# Level progression
LEVEL_THRESHOLDS = {
    1: 0,
    2: 100,
    3: 200,
    4: 500,
    5: 1000
}

# ===== PHYSICS & MOVEMENT =====
PLAYER_MOVE_SPEED = 5
SLIDE_DURATION = 30  # frames
JUMP_BUFFER_TIME = 0.1  # seconds
COYOTE_TIME = 0.1  # seconds
DASH_COOLDOWN = 3.0  # seconds
DASH_DISTANCE = 150

# ===== ENEMY SETTINGS =====
NINJA_SPEED = 8
WIZARD_SPEED = 15
CROCODILE_SPEED = 6

ENEMY_SPAWN_RATES = {
    'wizard': 0.02,
    'ninja': 0.005,
    'crocodile': 0.01,
    'danger_tree': 0.03
}

# ===== AUDIO SETTINGS =====
AUDIO_FREQUENCY = 44100
AUDIO_CHANNELS = 2
AUDIO_BUFFER_SIZE = 512

DEFAULT_VOLUMES = {
    'master': 0.8,
    'music': 0.7,
    'sfx': 0.9,
    'ambient': 0.6,
    'ui': 0.5
}

# ===== VISUAL EFFECTS =====
PARTICLE_MAX_COUNT = 1000
SCREEN_SHAKE_INTENSITY = 1.0
FLASH_DURATION = 0.2  # seconds

# Parallax layers
PARALLAX_SPEEDS = [0.2, 0.4, 0.6, 0.8, 1.0, 1.3]

# ===== INPUT SETTINGS =====
DEFAULT_KEYBINDS = {
    'move_forward': pygame.K_SPACE,
    'jump': pygame.K_j,
    'slide': pygame.K_d,
    'shield_toggle': pygame.K_s,
    'attack': pygame.K_a,
    'shield_up': pygame.K_UP,
    'shield_down': pygame.K_DOWN,
    'pause': pygame.K_ESCAPE,
    'debug': pygame.K_F3,
    'console': pygame.K_BACKQUOTE
}

# ===== FILE PATHS =====
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
AUDIO_DIR = BASE_DIR / "audio"
IMAGES_DIR = BASE_DIR / "pictures"
SAVES_DIR = BASE_DIR / "saves"
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
for directory in [SAVES_DIR, DATA_DIR]:
    directory.mkdir(exist_ok=True)

# ===== COLOR PALETTE =====
COLORS = {
    # UI Colors
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'gray': (128, 128, 128),
    'dark_gray': (64, 64, 64),
    'light_gray': (192, 192, 192),
    
    # Theme Colors (Forest)
    'forest_green': (34, 139, 34),
    'dark_green': (0, 100, 0),
    'leaf_green': (124, 252, 0),
    'bark_brown': (139, 69, 19),
    'earth_brown': (160, 82, 45),
    
    # Status Colors
    'health_red': (220, 20, 60),
    'shield_blue': (70, 130, 180),
    'mana_purple': (148, 0, 211),
    'xp_gold': (255, 215, 0),
    
    # Feedback Colors
    'damage_red': (255, 0, 0),
    'heal_green': (0, 255, 0),
    'warning_orange': (255, 165, 0),
    'critical_yellow': (255, 255, 0),
    
    # Transparency
    'transparent': (0, 0, 0, 0),
    'semi_transparent': (0, 0, 0, 128)
}

# ===== UI SETTINGS =====
UI_ANIMATION_SPEED = 0.2
BUTTON_HOVER_SCALE = 1.05
BUTTON_CLICK_SCALE = 0.95
TOOLTIP_DELAY = 0.5

FONT_SIZES = {
    'tiny': 12,
    'small': 16,
    'normal': 20,
    'large': 28,
    'huge': 36,
    'title': 48
}

# ===== ACCESSIBILITY =====
COLORBLIND_MODES = ['none', 'protanopia', 'deuteranopia', 'tritanopia', 'achromatopsia']
UI_SCALE_OPTIONS = [100, 125, 150, 200]
REDUCED_MOTION_DEFAULT = False

# ===== PERFORMANCE =====
MAX_PARTICLES = 1000
MAX_ENTITIES = 100
CULLING_MARGIN = 200  # pixels outside screen to start culling

QUALITY_PRESETS = {
    'low': {
        'particles': 250,
        'effects': False,
        'shadows': False,
        'post_processing': False,
        'target_fps': 30
    },
    'medium': {
        'particles': 500,
        'effects': True,
        'shadows': True,
        'post_processing': False,
        'target_fps': 60
    },
    'high': {
        'particles': 750,
        'effects': True,
        'shadows': True,
        'post_processing': True,
        'target_fps': 60
    },
    'ultra': {
        'particles': 1000,
        'effects': True,
        'shadows': True,
        'post_processing': True,
        'target_fps': 60
    }
}

# ===== DEBUG SETTINGS =====
DEBUG_MODE = False
SHOW_HITBOXES = False
SHOW_FPS = False
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# ===== ACHIEVEMENT DEFINITIONS =====
ACHIEVEMENTS = {
    'first_steps': {
        'name': 'First Steps',
        'description': 'Survive for 30 seconds',
        'requirement': {'type': 'survival_time', 'value': 30},
        'tier': 'bronze',
        'xp_reward': 100
    },
    'survivor': {
        'name': 'Survivor',
        'description': 'Survive for 2 minutes',
        'requirement': {'type': 'survival_time', 'value': 120},
        'tier': 'silver',
        'xp_reward': 250
    },
    'unstoppable': {
        'name': 'Unstoppable',
        'description': 'Survive for 5 minutes',
        'requirement': {'type': 'survival_time', 'value': 300},
        'tier': 'gold',
        'xp_reward': 500
    },
    'legend': {
        'name': 'Legend',
        'description': 'Survive for 10 minutes',
        'requirement': {'type': 'survival_time', 'value': 600},
        'tier': 'platinum',
        'xp_reward': 1000
    }
}

# ===== SAVE FILE STRUCTURE =====
SAVE_VERSION = "1.0.0"
DEFAULT_SAVE_DATA = {
    "version": SAVE_VERSION,
    "player": {
        "name": "Player",
        "level": 1,
        "xp": 0,
        "total_xp": 0,
        "skill_points": 0,
        "skills_unlocked": [],
        "equipped_skin": "default",
        "equipped_weapon": "classic_sword",
        "equipped_shield": "wooden",
        "equipped_trail": "none",
        "title": "Warrior"
    },
    "statistics": {
        "total_playtime": 0,
        "runs_completed": 0,
        "best_score": 0,
        "longest_survival": 0,
        "total_enemies_defeated": 0,
        "total_damage_dealt": 0,
        "total_damage_taken": 0,
        "perfect_blocks": 0,
        "highest_combo": 0,
        "total_distance": 0,
        "deaths": 0,
        "deaths_by_enemy": {
            "ninja": 0,
            "wizard": 0,
            "crocodile": 0,
            "tree": 0
        }
    },
    "achievements": {
        "unlocked": [],
        "progress": {}
    },
    "unlocks": {
        "skins": ["default"],
        "weapons": ["classic_sword"],
        "shields": ["wooden"],
        "trails": ["none"],
        "music": ["theme"]
    },
    "settings": {
        "audio": DEFAULT_VOLUMES,
        "video": {
            "resolution": DEFAULT_RESOLUTION,
            "fullscreen": False,
            "vsync": VSYNC_DEFAULT,
            "quality_preset": "medium"
        },
        "gameplay": {
            "difficulty": "normal",
            "show_tutorial": True,
            "auto_pause": True,
            "damage_numbers": True,
            "screen_shake_intensity": 100
        },
        "controls": {
            "keyboard": DEFAULT_KEYBINDS.copy(),
            "controller_enabled": False
        },
        "accessibility": {
            "colorblind_mode": "none",
            "high_contrast": False,
            "ui_scale": 100,
            "reduced_motion": False
        }
    }
}