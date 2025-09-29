"""
Forest Survival - Performance Monitor
Tracks and displays performance metrics with debug overlays.
"""

import pygame
import time
import psutil
from typing import Dict, List, Optional
from collections import deque
from dataclasses import dataclass

import config


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    fps: float = 0.0
    frame_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    entity_count: int = 0
    particle_count: int = 0
    draw_calls: int = 0


class PerformanceMonitor:
    """
    Monitors game performance and provides debugging tools.
    """
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.debug_enabled = config.DEBUG_MODE
        self.show_fps = config.SHOW_FPS
        
        # Performance tracking
        self.frame_times = deque(maxlen=60)  # Store last 60 frame times
        self.fps_history = deque(maxlen=120)  # Store 2 seconds of FPS data
        
        # Current metrics
        self.metrics = PerformanceMetrics()
        
        # Quality settings
        self.quality_preset = 'medium'
        self.quality_settings = config.QUALITY_PRESETS[self.quality_preset].copy()
        
        # Debug font
        try:
            self.debug_font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
        except pygame.error:
            self.debug_font = None
            self.small_font = None
        
        # Performance counters
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.accumulated_frame_time = 0.0
        
        # System monitoring
        self.process = psutil.Process()
        self.last_cpu_update = time.time()
        
        print("Performance Monitor initialized")
    
    def update(self, delta_time: float):
        """
        Update performance monitoring.
        
        Args:
            delta_time: Time since last frame in seconds
        """
        current_time = time.time()
        
        # Track frame time
        frame_time_ms = delta_time * 1000
        self.frame_times.append(frame_time_ms)
        self.accumulated_frame_time += delta_time
        self.frame_count += 1
        
        # Update FPS every second
        if current_time - self.last_fps_update >= 1.0:
            if self.accumulated_frame_time > 0:
                self.metrics.fps = self.frame_count / self.accumulated_frame_time
                self.fps_history.append(self.metrics.fps)
            
            self.frame_count = 0
            self.accumulated_frame_time = 0.0
            self.last_fps_update = current_time
        
        # Update frame time metric
        if self.frame_times:
            self.metrics.frame_time = sum(self.frame_times) / len(self.frame_times)
        
        # Update system metrics every 2 seconds
        if current_time - self.last_cpu_update >= 2.0:
            self._update_system_metrics()
            self.last_cpu_update = current_time
        
        # Auto-adjust quality if needed
        self._auto_adjust_quality()
    
    def _update_system_metrics(self):
        """Update CPU and memory usage."""
        try:
            self.metrics.cpu_usage = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            self.metrics.memory_usage = memory_info.rss / (1024 * 1024)  # MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    def _auto_adjust_quality(self):
        """Automatically adjust quality settings based on performance."""
        if not self.fps_history or len(self.fps_history) < 10:
            return
        
        avg_fps = sum(list(self.fps_history)[-10:]) / 10
        target_fps = self.quality_settings['target_fps']
        
        # If FPS is consistently low, reduce quality
        if avg_fps < target_fps * 0.9:  # 10% below target
            self._reduce_quality()
        
        # If FPS is consistently high, can increase quality
        elif avg_fps > target_fps * 1.1 and self.quality_preset != 'ultra':
            # Only increase if stable for longer period
            if len(self.fps_history) >= 30:
                recent_avg = sum(list(self.fps_history)[-30:]) / 30
                if recent_avg > target_fps * 1.1:
                    self._increase_quality()
    
    def _reduce_quality(self):
        """Reduce quality settings to improve performance."""
        presets = ['ultra', 'high', 'medium', 'low']
        current_index = presets.index(self.quality_preset)
        
        if current_index < len(presets) - 1:
            new_preset = presets[current_index + 1]
            self.set_quality_preset(new_preset)
            print(f"Auto-reduced quality to {new_preset}")
    
    def _increase_quality(self):
        """Increase quality settings if performance allows."""
        presets = ['low', 'medium', 'high', 'ultra']
        current_index = presets.index(self.quality_preset)
        
        if current_index < len(presets) - 1:
            new_preset = presets[current_index + 1]
            self.set_quality_preset(new_preset)
            print(f"Auto-increased quality to {new_preset}")
    
    def set_quality_preset(self, preset: str):
        """
        Set quality preset.
        
        Args:
            preset: Quality preset name ('low', 'medium', 'high', 'ultra')
        """
        if preset in config.QUALITY_PRESETS:
            self.quality_preset = preset
            self.quality_settings = config.QUALITY_PRESETS[preset].copy()
            print(f"Quality preset set to {preset}")
        else:
            print(f"Unknown quality preset: {preset}")
    
    def get_quality_setting(self, setting: str):
        """Get a quality setting value."""
        return self.quality_settings.get(setting)
    
    def update_entity_count(self, count: int):
        """Update entity count for monitoring."""
        self.metrics.entity_count = count
    
    def update_particle_count(self, count: int):
        """Update particle count for monitoring."""
        self.metrics.particle_count = count
    
    def increment_draw_calls(self):
        """Increment draw call counter."""
        self.metrics.draw_calls += 1
    
    def reset_draw_calls(self):
        """Reset draw call counter for new frame."""
        self.metrics.draw_calls = 0
    
    def toggle_debug_overlay(self):
        """Toggle debug overlay visibility."""
        self.debug_enabled = not self.debug_enabled
        print(f"Debug overlay: {'enabled' if self.debug_enabled else 'disabled'}")
    
    def toggle_fps_display(self):
        """Toggle FPS display."""
        self.show_fps = not self.show_fps
    
    def render_debug_overlay(self, screen: pygame.Surface):
        """
        Render debug performance overlay.
        
        Args:
            screen: Screen surface to render on
        """
        if not self.debug_enabled or not self.debug_font:
            return
        
        # Background panel
        overlay_width = 300
        overlay_height = 200
        overlay_rect = pygame.Rect(10, 10, overlay_width, overlay_height)
        
        # Semi-transparent background
        overlay_surface = pygame.Surface((overlay_width, overlay_height))
        overlay_surface.set_alpha(200)
        overlay_surface.fill((0, 0, 0))
        screen.blit(overlay_surface, overlay_rect)
        
        # Performance metrics text
        y_offset = 20
        line_height = 20
        
        metrics_text = [
            f"FPS: {self.metrics.fps:.1f}",
            f"Frame Time: {self.metrics.frame_time:.2f}ms",
            f"CPU: {self.metrics.cpu_usage:.1f}%",
            f"Memory: {self.metrics.memory_usage:.1f}MB",
            f"Entities: {self.metrics.entity_count}",
            f"Particles: {self.metrics.particle_count}",
            f"Draw Calls: {self.metrics.draw_calls}",
            f"Quality: {self.quality_preset.title()}",
        ]
        
        for i, text in enumerate(metrics_text):
            color = (255, 255, 255)
            
            # Color code based on values
            if "FPS:" in text and self.metrics.fps < 45:
                color = (255, 0, 0)  # Red for low FPS
            elif "Frame Time:" in text and self.metrics.frame_time > 20:
                color = (255, 165, 0)  # Orange for high frame time
            elif "CPU:" in text and self.metrics.cpu_usage > 80:
                color = (255, 0, 0)  # Red for high CPU
            elif "Memory:" in text and self.metrics.memory_usage > 500:
                color = (255, 165, 0)  # Orange for high memory
            
            text_surface = self.debug_font.render(text, True, color)
            screen.blit(text_surface, (20, y_offset + i * line_height))
        
        # FPS graph
        if len(self.fps_history) > 1:
            self._render_fps_graph(screen, overlay_rect)
    
    def _render_fps_graph(self, screen: pygame.Surface, overlay_rect: pygame.Rect):
        """Render FPS history graph."""
        graph_rect = pygame.Rect(
            overlay_rect.right - 150, 
            overlay_rect.top + 10, 
            140, 60
        )
        
        # Graph background
        pygame.draw.rect(screen, (40, 40, 40), graph_rect)
        pygame.draw.rect(screen, (255, 255, 255), graph_rect, 1)
        
        if len(self.fps_history) < 2:
            return
        
        # Draw FPS line
        fps_values = list(self.fps_history)
        max_fps = max(fps_values) if fps_values else 60
        min_fps = min(fps_values) if fps_values else 0
        
        if max_fps > min_fps:
            points = []
            for i, fps in enumerate(fps_values):
                x = graph_rect.left + (i / len(fps_values)) * graph_rect.width
                normalized_fps = (fps - min_fps) / (max_fps - min_fps)
                y = graph_rect.bottom - normalized_fps * graph_rect.height
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(screen, (0, 255, 0), False, points, 2)
        
        # Draw target FPS line
        target_fps = self.quality_settings['target_fps']
        if min_fps < target_fps < max_fps:
            normalized_target = (target_fps - min_fps) / (max_fps - min_fps)
            target_y = graph_rect.bottom - normalized_target * graph_rect.height
            pygame.draw.line(screen, (255, 0, 0), 
                           (graph_rect.left, target_y), 
                           (graph_rect.right, target_y), 1)
    
    def render_fps_counter(self, screen: pygame.Surface):
        """
        Render simple FPS counter.
        
        Args:
            screen: Screen surface to render on
        """
        if not self.show_fps or not self.debug_font:
            return
        
        fps_text = f"FPS: {self.metrics.fps:.1f}"
        color = (255, 255, 255)
        
        if self.metrics.fps < 45:
            color = (255, 0, 0)  # Red
        elif self.metrics.fps < 55:
            color = (255, 165, 0)  # Orange
        
        text_surface = self.debug_font.render(fps_text, True, color)
        screen.blit(text_surface, (screen.get_width() - 100, 10))
    
    def get_performance_summary(self) -> Dict:
        """Get current performance summary."""
        return {
            'fps': self.metrics.fps,
            'frame_time': self.metrics.frame_time,
            'cpu_usage': self.metrics.cpu_usage,
            'memory_usage': self.metrics.memory_usage,
            'entity_count': self.metrics.entity_count,
            'particle_count': self.metrics.particle_count,
            'quality_preset': self.quality_preset
        }
    
    def save_session_data(self):
        """Save performance data for this session."""
        if not self.fps_history:
            return
        
        session_data = {
            'avg_fps': sum(self.fps_history) / len(self.fps_history),
            'min_fps': min(self.fps_history),
            'max_fps': max(self.fps_history),
            'quality_preset': self.quality_preset,
            'session_time': time.time()
        }
        
        try:
            import json
            log_file = config.SAVES_DIR / "performance_log.json"
            
            # Load existing data
            existing_data = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    existing_data = json.load(f)
            
            # Add new session
            existing_data.append(session_data)
            
            # Keep only last 10 sessions
            existing_data = existing_data[-10:]
            
            # Save back to file
            with open(log_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving performance data: {e}")
    
    def should_skip_frame(self) -> bool:
        """Determine if frame should be skipped to maintain performance."""
        return (self.metrics.fps < 30 and 
                self.quality_preset == 'low' and 
                len(self.fps_history) > 5)
    
    def is_performance_critical(self) -> bool:
        """Check if performance is critically low."""
        return self.metrics.fps < 20 and len(self.fps_history) > 10