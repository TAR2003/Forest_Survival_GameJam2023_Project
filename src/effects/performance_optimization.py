"""
Forest Survival - Performance Optimization System
Advanced performance monitoring, optimization, and scaling systems.
"""

import time
import gc
import sys
import threading
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass
from collections import deque

import config


class OptimizationLevel(Enum):
    """Performance optimization levels."""
    ULTRA = "ultra"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    POTATO = "potato"


class PerformanceCategory(Enum):
    """Performance monitoring categories."""
    RENDERING = "rendering"
    PHYSICS = "physics"
    AI = "ai"
    AUDIO = "audio"
    NETWORKING = "networking"
    MEMORY = "memory"
    DISK_IO = "disk_io"


@dataclass
class PerformanceMetric:
    """Performance metric data."""
    name: str
    category: PerformanceCategory
    current_value: float
    average_value: float
    peak_value: float
    min_value: float
    
    # Thresholds
    warning_threshold: float
    critical_threshold: float
    
    # History
    history: deque = None
    max_history: int = 100
    
    def __post_init__(self):
        if self.history is None:
            self.history = deque(maxlen=self.max_history)
    
    def update(self, value: float):
        """Update metric with new value."""
        self.current_value = value
        self.history.append(value)
        
        # Update statistics
        if len(self.history) > 0:
            self.average_value = sum(self.history) / len(self.history)
            self.peak_value = max(self.history)
            self.min_value = min(self.history)
    
    def is_warning(self) -> bool:
        """Check if metric is in warning range."""
        return self.current_value >= self.warning_threshold
    
    def is_critical(self) -> bool:
        """Check if metric is in critical range."""
        return self.current_value >= self.critical_threshold


class FrameRateManager:
    """Manages frame rate and timing."""
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        
        # Timing
        self.last_frame_time = time.time()
        self.frame_times = deque(maxlen=100)
        self.delta_times = deque(maxlen=100)
        
        # Statistics
        self.current_fps = 0.0
        self.average_fps = 0.0
        self.frame_time_ms = 0.0
        
        # Adaptive settings
        self.adaptive_quality = True
        self.quality_adjustment_cooldown = 5.0  # seconds
        self.last_quality_adjustment = 0.0
        
        # Frame limiting
        self.vsync_enabled = True
        self.frame_limit_enabled = True
    
    def update(self) -> float:
        """Update timing and return delta time."""
        current_time = time.time()
        delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Store timing data
        self.frame_times.append(current_time)
        self.delta_times.append(delta_time)
        
        # Calculate statistics
        self.frame_time_ms = delta_time * 1000.0
        
        if len(self.frame_times) >= 2:
            total_time = self.frame_times[-1] - self.frame_times[0]
            frame_count = len(self.frame_times) - 1
            if total_time > 0:
                self.current_fps = 1.0 / delta_time
                self.average_fps = frame_count / total_time
        
        return delta_time
    
    def set_target_fps(self, fps: int):
        """Set target frame rate."""
        self.target_fps = fps
        self.target_frame_time = 1.0 / fps
    
    def get_fps_info(self) -> Dict[str, float]:
        """Get frame rate information."""
        return {
            'current_fps': self.current_fps,
            'average_fps': self.average_fps,
            'target_fps': self.target_fps,
            'frame_time_ms': self.frame_time_ms,
            'target_frame_time_ms': self.target_frame_time * 1000.0
        }


class MemoryManager:
    """Manages memory usage and garbage collection."""
    
    def __init__(self):
        # Memory tracking
        self.memory_usage_history = deque(maxlen=100)
        self.gc_stats = {'collections': 0, 'freed_objects': 0}
        
        # Thresholds (in MB)
        self.warning_threshold = 512.0
        self.critical_threshold = 1024.0
        self.cleanup_threshold = 768.0
        
        # Auto cleanup
        self.auto_cleanup_enabled = True
        self.cleanup_interval = 30.0  # seconds
        self.last_cleanup = time.time()
        
        # Manual cleanup tracking
        self.manual_cleanups = 0
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            return memory_mb
        except ImportError:
            # Fallback to sys.getsizeof for approximate usage
            return sys.getsizeof(gc.get_objects()) / (1024 * 1024)
    
    def update(self):
        """Update memory management."""
        current_memory = self.get_memory_usage()
        self.memory_usage_history.append(current_memory)
        
        # Auto cleanup check
        if self.auto_cleanup_enabled:
            current_time = time.time()
            
            # Periodic cleanup
            if current_time - self.last_cleanup >= self.cleanup_interval:
                self.cleanup()
                self.last_cleanup = current_time
            
            # Emergency cleanup
            elif current_memory >= self.cleanup_threshold:
                self.cleanup()
                self.last_cleanup = current_time
    
    def cleanup(self):
        """Perform memory cleanup."""
        # Force garbage collection
        collected = gc.collect()
        
        self.gc_stats['collections'] += 1
        self.gc_stats['freed_objects'] += collected
        self.manual_cleanups += 1
        
        print(f"Memory cleanup: freed {collected} objects")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory management information."""
        current_memory = self.get_memory_usage()
        
        return {
            'current_mb': current_memory,
            'average_mb': sum(self.memory_usage_history) / len(self.memory_usage_history) if self.memory_usage_history else 0,
            'peak_mb': max(self.memory_usage_history) if self.memory_usage_history else 0,
            'warning_threshold': self.warning_threshold,
            'critical_threshold': self.critical_threshold,
            'is_warning': current_memory >= self.warning_threshold,
            'is_critical': current_memory >= self.critical_threshold,
            'gc_stats': self.gc_stats.copy(),
            'manual_cleanups': self.manual_cleanups
        }


class QualitySettingsManager:
    """Manages dynamic quality settings for performance optimization."""
    
    def __init__(self):
        self.current_level = OptimizationLevel.HIGH
        
        # Quality settings for different levels
        self.quality_presets = {
            OptimizationLevel.ULTRA: {
                'particle_count_multiplier': 2.0,
                'shadow_quality': 1.0,
                'texture_quality': 1.0,
                'effect_quality': 1.0,
                'draw_distance': 1.0,
                'anti_aliasing': True,
                'post_processing': True,
                'dynamic_lighting': True,
                'particle_physics': True
            },
            OptimizationLevel.HIGH: {
                'particle_count_multiplier': 1.0,
                'shadow_quality': 0.8,
                'texture_quality': 1.0,
                'effect_quality': 0.9,
                'draw_distance': 0.9,
                'anti_aliasing': True,
                'post_processing': True,
                'dynamic_lighting': True,
                'particle_physics': True
            },
            OptimizationLevel.MEDIUM: {
                'particle_count_multiplier': 0.7,
                'shadow_quality': 0.6,
                'texture_quality': 0.8,
                'effect_quality': 0.7,
                'draw_distance': 0.8,
                'anti_aliasing': True,
                'post_processing': False,
                'dynamic_lighting': True,
                'particle_physics': False
            },
            OptimizationLevel.LOW: {
                'particle_count_multiplier': 0.5,
                'shadow_quality': 0.4,
                'texture_quality': 0.6,
                'effect_quality': 0.5,
                'draw_distance': 0.6,
                'anti_aliasing': False,
                'post_processing': False,
                'dynamic_lighting': False,
                'particle_physics': False
            },
            OptimizationLevel.POTATO: {
                'particle_count_multiplier': 0.2,
                'shadow_quality': 0.0,
                'texture_quality': 0.4,
                'effect_quality': 0.2,
                'draw_distance': 0.4,
                'anti_aliasing': False,
                'post_processing': False,
                'dynamic_lighting': False,
                'particle_physics': False
            }
        }
        
        # Current settings
        self.current_settings = self.quality_presets[self.current_level].copy()
        
        # Auto adjustment
        self.auto_adjust = True
        self.adjustment_cooldown = 10.0  # seconds
        self.last_adjustment = 0.0
    
    def set_quality_level(self, level: OptimizationLevel):
        """Set quality level and update settings."""
        self.current_level = level
        self.current_settings = self.quality_presets[level].copy()
        print(f"Quality level set to: {level.value}")
    
    def get_setting(self, setting_name: str) -> Any:
        """Get current value for a quality setting."""
        return self.current_settings.get(setting_name, 1.0)
    
    def adjust_for_performance(self, fps: float, target_fps: float):
        """Automatically adjust quality based on performance."""
        if not self.auto_adjust:
            return
        
        current_time = time.time()
        if current_time - self.last_adjustment < self.adjustment_cooldown:
            return
        
        fps_ratio = fps / target_fps
        
        # Determine if adjustment is needed
        if fps_ratio < 0.8:  # Performance is poor
            # Lower quality
            current_index = list(OptimizationLevel).index(self.current_level)
            if current_index < len(OptimizationLevel) - 1:
                new_level = list(OptimizationLevel)[current_index + 1]
                self.set_quality_level(new_level)
                self.last_adjustment = current_time
        
        elif fps_ratio > 1.2:  # Performance is good
            # Raise quality
            current_index = list(OptimizationLevel).index(self.current_level)
            if current_index > 0:
                new_level = list(OptimizationLevel)[current_index - 1]
                self.set_quality_level(new_level)
                self.last_adjustment = current_time


class PerformanceProfiler:
    """Advanced performance profiling and monitoring."""
    
    def __init__(self):
        # Metrics
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.initialize_metrics()
        
        # Profiling data
        self.function_timings: Dict[str, List[float]] = {}
        self.active_timers: Dict[str, float] = {}
        
        # Monitoring
        self.monitoring_enabled = True
        self.detailed_profiling = False
        
        # Threading for background monitoring
        self.monitor_thread = None
        self.monitor_running = False
        
        # Callbacks for performance events
        self.warning_callbacks: List[Callable] = []
        self.critical_callbacks: List[Callable] = []
    
    def initialize_metrics(self):
        """Initialize performance metrics."""
        # Rendering metrics
        self.metrics['fps'] = PerformanceMetric(
            'FPS', PerformanceCategory.RENDERING, 0, 0, 0, float('inf'),
            warning_threshold=30, critical_threshold=15
        )
        
        self.metrics['frame_time'] = PerformanceMetric(
            'Frame Time (ms)', PerformanceCategory.RENDERING, 0, 0, 0, float('inf'),
            warning_threshold=33.33, critical_threshold=66.66
        )
        
        self.metrics['draw_calls'] = PerformanceMetric(
            'Draw Calls', PerformanceCategory.RENDERING, 0, 0, 0, float('inf'),
            warning_threshold=1000, critical_threshold=2000
        )
        
        # Memory metrics
        self.metrics['memory_usage'] = PerformanceMetric(
            'Memory Usage (MB)', PerformanceCategory.MEMORY, 0, 0, 0, float('inf'),
            warning_threshold=512, critical_threshold=1024
        )
        
        # Physics metrics
        self.metrics['physics_time'] = PerformanceMetric(
            'Physics Time (ms)', PerformanceCategory.PHYSICS, 0, 0, 0, float('inf'),
            warning_threshold=5, critical_threshold=10
        )
        
        # AI metrics
        self.metrics['ai_time'] = PerformanceMetric(
            'AI Time (ms)', PerformanceCategory.AI, 0, 0, 0, float('inf'),
            warning_threshold=3, critical_threshold=6
        )
    
    def start_timer(self, name: str):
        """Start timing a function or section."""
        if self.monitoring_enabled:
            self.active_timers[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """End timing and return elapsed time."""
        if not self.monitoring_enabled or name not in self.active_timers:
            return 0.0
        
        elapsed = time.time() - self.active_timers[name]
        del self.active_timers[name]
        
        # Store timing data
        if name not in self.function_timings:
            self.function_timings[name] = []
        
        self.function_timings[name].append(elapsed)
        
        # Limit history
        if len(self.function_timings[name]) > 100:
            self.function_timings[name].pop(0)
        
        return elapsed
    
    def update_metric(self, name: str, value: float):
        """Update a performance metric."""
        if name in self.metrics:
            metric = self.metrics[name]
            old_warning = metric.is_warning()
            old_critical = metric.is_critical()
            
            metric.update(value)
            
            # Check for state changes
            if not old_warning and metric.is_warning():
                self._trigger_warning_callbacks(name, metric)
            
            if not old_critical and metric.is_critical():
                self._trigger_critical_callbacks(name, metric)
    
    def _trigger_warning_callbacks(self, metric_name: str, metric: PerformanceMetric):
        """Trigger warning callbacks."""
        for callback in self.warning_callbacks:
            try:
                callback(metric_name, metric)
            except Exception as e:
                print(f"Warning callback error: {e}")
    
    def _trigger_critical_callbacks(self, metric_name: str, metric: PerformanceMetric):
        """Trigger critical callbacks."""
        for callback in self.critical_callbacks:
            try:
                callback(metric_name, metric)
            except Exception as e:
                print(f"Critical callback error: {e}")
    
    def add_warning_callback(self, callback: Callable):
        """Add callback for performance warnings."""
        self.warning_callbacks.append(callback)
    
    def add_critical_callback(self, callback: Callable):
        """Add callback for critical performance issues."""
        self.critical_callbacks.append(callback)
    
    def get_metric_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = {}
        
        for name, metric in self.metrics.items():
            summary[name] = {
                'current': metric.current_value,
                'average': metric.average_value,
                'peak': metric.peak_value,
                'min': metric.min_value,
                'is_warning': metric.is_warning(),
                'is_critical': metric.is_critical(),
                'category': metric.category.value
            }
        
        return summary
    
    def get_function_timings(self) -> Dict[str, Dict[str, float]]:
        """Get function timing statistics."""
        stats = {}
        
        for func_name, timings in self.function_timings.items():
            if timings:
                stats[func_name] = {
                    'average_ms': (sum(timings) / len(timings)) * 1000,
                    'total_ms': sum(timings) * 1000,
                    'calls': len(timings),
                    'max_ms': max(timings) * 1000,
                    'min_ms': min(timings) * 1000
                }
        
        return stats


class PerformanceOptimizationSystem:
    """
    Complete performance optimization system with monitoring, profiling, and dynamic adjustment.
    """
    
    def __init__(self):
        # Core components
        self.frame_rate_manager = FrameRateManager()
        self.memory_manager = MemoryManager()
        self.quality_manager = QualitySettingsManager()
        self.profiler = PerformanceProfiler()
        
        # System state
        self.optimization_enabled = True
        self.aggressive_optimization = False
        
        # Performance targets
        self.target_fps = 60
        self.target_frame_time = 16.67  # ms
        
        # Optimization strategies
        self.strategies_enabled = {
            'dynamic_quality': True,
            'memory_management': True,
            'frame_limiting': True,
            'background_optimization': True
        }
        
        # Statistics
        self.optimization_actions = 0
        self.quality_adjustments = 0
        self.memory_cleanups = 0
        
        print("Performance optimization system initialized")
    
    def update(self, dt: float):
        """Update performance optimization system."""
        if not self.optimization_enabled:
            return
        
        # Update core components
        self.frame_rate_manager.update()
        self.memory_manager.update()
        
        # Update profiler metrics
        fps_info = self.frame_rate_manager.get_fps_info()
        memory_info = self.memory_manager.get_memory_info()
        
        self.profiler.update_metric('fps', fps_info['current_fps'])
        self.profiler.update_metric('frame_time', fps_info['frame_time_ms'])
        self.profiler.update_metric('memory_usage', memory_info['current_mb'])
        
        # Dynamic quality adjustment
        if self.strategies_enabled['dynamic_quality']:
            self.quality_manager.adjust_for_performance(
                fps_info['current_fps'],
                self.target_fps
            )
    
    def start_profiling(self, name: str):
        """Start profiling a section."""
        self.profiler.start_timer(name)
    
    def end_profiling(self, name: str) -> float:
        """End profiling a section."""
        return self.profiler.end_timer(name)
    
    def optimize_for_target(self, target_fps: int):
        """Optimize system for a specific FPS target."""
        self.target_fps = target_fps
        self.target_frame_time = 1000.0 / target_fps
        
        self.frame_rate_manager.set_target_fps(target_fps)
        
        # Adjust quality preemptively based on target
        if target_fps >= 120:
            self.quality_manager.set_quality_level(OptimizationLevel.ULTRA)
        elif target_fps >= 60:
            self.quality_manager.set_quality_level(OptimizationLevel.HIGH)
        elif target_fps >= 30:
            self.quality_manager.set_quality_level(OptimizationLevel.MEDIUM)
        else:
            self.quality_manager.set_quality_level(OptimizationLevel.LOW)
    
    def force_memory_cleanup(self):
        """Force immediate memory cleanup."""
        self.memory_manager.cleanup()
        self.memory_cleanups += 1
    
    def enable_aggressive_optimization(self, enabled: bool = True):
        """Enable or disable aggressive optimization."""
        self.aggressive_optimization = enabled
        
        if enabled:
            # More aggressive settings
            self.quality_manager.adjustment_cooldown = 5.0
            self.memory_manager.cleanup_interval = 15.0
            self.memory_manager.cleanup_threshold = 512.0
        else:
            # Standard settings
            self.quality_manager.adjustment_cooldown = 10.0
            self.memory_manager.cleanup_interval = 30.0
            self.memory_manager.cleanup_threshold = 768.0
    
    def get_optimization_info(self) -> Dict[str, Any]:
        """Get comprehensive optimization system information."""
        return {
            'fps_info': self.frame_rate_manager.get_fps_info(),
            'memory_info': self.memory_manager.get_memory_info(),
            'quality_level': self.quality_manager.current_level.value,
            'quality_settings': self.quality_manager.current_settings.copy(),
            'metrics_summary': self.profiler.get_metric_summary(),
            'function_timings': self.profiler.get_function_timings(),
            'optimization_stats': {
                'optimization_actions': self.optimization_actions,
                'quality_adjustments': self.quality_adjustments,
                'memory_cleanups': self.memory_cleanups,
                'aggressive_mode': self.aggressive_optimization
            },
            'strategies_enabled': self.strategies_enabled.copy()
        }
    
    def get_performance_summary(self) -> str:
        """Get human-readable performance summary."""
        fps_info = self.frame_rate_manager.get_fps_info()
        memory_info = self.memory_manager.get_memory_info()
        
        summary = f"Performance Summary:\n"
        summary += f"FPS: {fps_info['current_fps']:.1f} (target: {self.target_fps})\n"
        summary += f"Frame Time: {fps_info['frame_time_ms']:.1f}ms\n"
        summary += f"Memory: {memory_info['current_mb']:.1f}MB\n"
        summary += f"Quality: {self.quality_manager.current_level.value}\n"
        
        # Performance status
        if fps_info['current_fps'] >= self.target_fps * 0.9:
            summary += "Status: Excellent"
        elif fps_info['current_fps'] >= self.target_fps * 0.7:
            summary += "Status: Good"
        elif fps_info['current_fps'] >= self.target_fps * 0.5:
            summary += "Status: Poor"
        else:
            summary += "Status: Critical"
        
        return summary