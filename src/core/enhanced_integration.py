"""
Forest Survival - Enhanced Integration Manager
Complete system integration and coordination for all game systems.
"""

import time
import threading
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

import config


class SystemPriority(Enum):
    """System update priority levels."""
    CRITICAL = 0    # Core gameplay systems
    HIGH = 1        # Important systems
    NORMAL = 2      # Standard systems
    LOW = 3         # Non-essential systems
    BACKGROUND = 4  # Background processes


class SystemState(Enum):
    """System state enumeration."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"


@dataclass
class SystemInfo:
    """Information about a registered system."""
    name: str
    system_object: Any
    priority: SystemPriority
    state: SystemState
    
    # Lifecycle methods
    init_method: Optional[str] = "initialize"
    update_method: Optional[str] = "update"
    cleanup_method: Optional[str] = "cleanup"
    
    # Performance tracking
    update_time: float = 0.0
    average_update_time: float = 0.0
    update_count: int = 0
    
    # Dependencies
    dependencies: List[str] = None
    dependents: List[str] = None
    
    # Error handling
    error_count: int = 0
    last_error: Optional[str] = None
    error_threshold: int = 5
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.dependents is None:
            self.dependents = []


class EventSystem:
    """Global event system for inter-system communication."""
    
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self.event_queue: List[Dict[str, Any]] = []
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        
        # Performance tracking
        self.events_processed = 0
        self.processing_time = 0.0
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        if callback not in self.listeners[event_type]:
            self.listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type."""
        if event_type in self.listeners and callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)
    
    def emit(self, event_type: str, data: Dict[str, Any] = None, immediate: bool = False):
        """Emit an event."""
        event = {
            'type': event_type,
            'data': data or {},
            'timestamp': time.time(),
            'immediate': immediate
        }
        
        if immediate:
            self._process_event(event)
        else:
            self.event_queue.append(event)
    
    def _process_event(self, event: Dict[str, Any]):
        """Process a single event."""
        event_type = event['type']
        
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Event callback error for {event_type}: {e}")
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        self.events_processed += 1
    
    def process_events(self) -> int:
        """Process all queued events."""
        start_time = time.time()
        processed_count = 0
        
        while self.event_queue:
            event = self.event_queue.pop(0)
            self._process_event(event)
            processed_count += 1
        
        self.processing_time += time.time() - start_time
        return processed_count
    
    def get_event_info(self) -> Dict[str, Any]:
        """Get event system information."""
        return {
            'listeners': {event_type: len(callbacks) for event_type, callbacks in self.listeners.items()},
            'queued_events': len(self.event_queue),
            'events_processed': self.events_processed,
            'processing_time': self.processing_time,
            'average_processing_time': self.processing_time / max(1, self.events_processed)
        }


class EnhancedIntegrationManager:
    """
    Enhanced system integration manager with advanced coordination and monitoring.
    """
    
    def __init__(self):
        # System registry
        self.systems: Dict[str, SystemInfo] = {}
        self.update_order: List[str] = []
        
        # Event system
        self.event_system = EventSystem()
        
        # State management
        self.manager_state = SystemState.UNINITIALIZED
        self.initialization_progress = 0.0
        
        # Performance monitoring
        self.total_update_time = 0.0
        self.frame_count = 0
        self.performance_history = []
        self.max_history = 100
        
        # Threading
        self.background_thread = None
        self.background_running = False
        self.thread_lock = threading.Lock()
        
        # Error handling
        self.error_recovery_enabled = True
        self.global_error_count = 0
        
        # Configuration
        self.max_update_time = 16.67  # Target 60 FPS (ms)
        self.time_budget_per_priority = {
            SystemPriority.CRITICAL: 8.0,   # 50% of frame time
            SystemPriority.HIGH: 4.0,       # 25% of frame time
            SystemPriority.NORMAL: 2.0,     # 12.5% of frame time
            SystemPriority.LOW: 1.0,        # 6.25% of frame time
            SystemPriority.BACKGROUND: 0.5  # 3.125% of frame time
        }
        
        print("Enhanced integration manager initialized")
    
    def register_system(self, name: str, system_obj: Any, priority: SystemPriority = SystemPriority.NORMAL,
                       dependencies: List[str] = None, init_method: str = "initialize",
                       update_method: str = "update", cleanup_method: str = "cleanup") -> bool:
        """Register a system with the manager."""
        try:
            # Check for duplicate registration
            if name in self.systems:
                print(f"Warning: System '{name}' already registered")
                return False
            
            # Validate system object has required methods
            if not hasattr(system_obj, update_method):
                print(f"Error: System '{name}' missing update method '{update_method}'")
                return False
            
            # Create system info
            system_info = SystemInfo(
                name=name,
                system_object=system_obj,
                priority=priority,
                state=SystemState.UNINITIALIZED,
                dependencies=dependencies or [],
                init_method=init_method,
                update_method=update_method,
                cleanup_method=cleanup_method
            )
            
            self.systems[name] = system_info
            self._rebuild_update_order()
            
            print(f"Registered system: {name} (priority: {priority.value})")
            
            # Emit registration event
            self.event_system.emit('system_registered', {
                'system_name': name,
                'priority': priority.value
            })
            
            return True
            
        except Exception as e:
            print(f"Failed to register system '{name}': {e}")
            return False
    
    def unregister_system(self, name: str) -> bool:
        """Unregister a system."""
        if name not in self.systems:
            return False
        
        system_info = self.systems[name]
        
        # Cleanup system if it has a cleanup method
        self._cleanup_system(system_info)
        
        # Remove from registry
        del self.systems[name]
        self._rebuild_update_order()
        
        # Emit unregistration event
        self.event_system.emit('system_unregistered', {'system_name': name})
        
        print(f"Unregistered system: {name}")
        return True
    
    def _rebuild_update_order(self):
        """Rebuild system update order based on dependencies and priorities."""
        # Sort systems by priority and handle dependencies
        sorted_systems = sorted(
            self.systems.items(),
            key=lambda x: (x[1].priority.value, x[0])
        )
        
        self.update_order = []
        resolved = set()
        
        def resolve_dependencies(system_name: str):
            if system_name in resolved:
                return
            
            system_info = self.systems[system_name]
            
            # Resolve dependencies first
            for dep in system_info.dependencies:
                if dep in self.systems and dep not in resolved:
                    resolve_dependencies(dep)
            
            self.update_order.append(system_name)
            resolved.add(system_name)
        
        # Resolve all systems
        for system_name, system_info in sorted_systems:
            resolve_dependencies(system_name)
    
    def initialize_systems(self) -> bool:
        """Initialize all registered systems."""
        self.manager_state = SystemState.INITIALIZING
        self.initialization_progress = 0.0
        
        total_systems = len(self.systems)
        initialized_count = 0
        
        try:
            for system_name in self.update_order:
                system_info = self.systems[system_name]
                
                print(f"Initializing system: {system_name}")
                
                # Initialize system
                if self._initialize_system(system_info):
                    initialized_count += 1
                    self.initialization_progress = initialized_count / total_systems
                else:
                    print(f"Failed to initialize system: {system_name}")
                    if system_info.priority == SystemPriority.CRITICAL:
                        # Critical system failure
                        self.manager_state = SystemState.ERROR
                        return False
            
            self.manager_state = SystemState.RUNNING
            self.initialization_progress = 1.0
            
            # Start background thread for background systems
            self._start_background_thread()
            
            # Emit initialization complete event
            self.event_system.emit('systems_initialized', {
                'total_systems': total_systems,
                'successful_inits': initialized_count
            })
            
            print(f"System initialization complete: {initialized_count}/{total_systems} systems")
            return True
            
        except Exception as e:
            print(f"System initialization failed: {e}")
            self.manager_state = SystemState.ERROR
            return False
    
    def _initialize_system(self, system_info: SystemInfo) -> bool:
        """Initialize a single system."""
        try:
            system_info.state = SystemState.INITIALIZING
            
            # Call initialization method if it exists
            if hasattr(system_info.system_object, system_info.init_method):
                init_func = getattr(system_info.system_object, system_info.init_method)
                init_func()
            
            system_info.state = SystemState.RUNNING
            return True
            
        except Exception as e:
            print(f"System initialization error for '{system_info.name}': {e}")
            system_info.state = SystemState.ERROR
            system_info.error_count += 1
            system_info.last_error = str(e)
            return False
    
    def update_systems(self, dt: float):
        """Update all running systems with time budgeting."""
        if self.manager_state != SystemState.RUNNING:
            return
        
        start_time = time.time()
        priority_timers = {priority: 0.0 for priority in SystemPriority}
        
        # Process events first
        self.event_system.process_events()
        
        # Update systems by priority with time budgeting
        for system_name in self.update_order:
            system_info = self.systems[system_name]
            
            if system_info.state != SystemState.RUNNING:
                continue
            
            # Skip background systems (handled by background thread)
            if system_info.priority == SystemPriority.BACKGROUND:
                continue
            
            # Check time budget for this priority level
            priority_time_used = priority_timers[system_info.priority]
            priority_budget = self.time_budget_per_priority[system_info.priority]
            
            if priority_time_used >= priority_budget:
                # Skip this system this frame to maintain frame rate
                continue
            
            # Update system
            system_start_time = time.time()
            
            if self._update_system(system_info, dt):
                update_time = (time.time() - system_start_time) * 1000.0  # Convert to ms
                
                # Update timing statistics
                system_info.update_time = update_time
                system_info.update_count += 1
                
                # Calculate running average
                alpha = 0.1  # Smoothing factor
                system_info.average_update_time = (
                    alpha * update_time + (1.0 - alpha) * system_info.average_update_time
                )
                
                # Track priority time usage
                priority_timers[system_info.priority] += update_time
            
            # Check if we're exceeding frame time budget
            total_time = (time.time() - start_time) * 1000.0
            if total_time >= self.max_update_time:
                break
        
        # Update performance tracking
        total_frame_time = (time.time() - start_time) * 1000.0
        self.total_update_time += total_frame_time
        self.frame_count += 1
        
        # Store performance history
        self.performance_history.append({
            'frame_time': total_frame_time,
            'priority_times': priority_timers.copy(),
            'timestamp': time.time()
        })
        
        if len(self.performance_history) > self.max_history:
            self.performance_history.pop(0)
    
    def _update_system(self, system_info: SystemInfo, dt: float) -> bool:
        """Update a single system."""
        try:
            # Call update method
            update_func = getattr(system_info.system_object, system_info.update_method)
            update_func(dt)
            
            # Reset error count on successful update
            if system_info.error_count > 0:
                system_info.error_count = max(0, system_info.error_count - 1)
            
            return True
            
        except Exception as e:
            print(f"System update error for '{system_info.name}': {e}")
            system_info.error_count += 1
            system_info.last_error = str(e)
            
            # Handle error recovery
            if self.error_recovery_enabled and system_info.error_count >= system_info.error_threshold:
                print(f"System '{system_info.name}' exceeded error threshold, pausing")
                system_info.state = SystemState.ERROR
                
                # Emit error event
                self.event_system.emit('system_error', {
                    'system_name': system_info.name,
                    'error_count': system_info.error_count,
                    'error_message': str(e)
                })
            
            return False
    
    def _cleanup_system(self, system_info: SystemInfo):
        """Cleanup a single system."""
        try:
            system_info.state = SystemState.SHUTTING_DOWN
            
            # Call cleanup method if it exists
            if hasattr(system_info.system_object, system_info.cleanup_method):
                cleanup_func = getattr(system_info.system_object, system_info.cleanup_method)
                cleanup_func()
            
            system_info.state = SystemState.SHUTDOWN
            print(f"System cleaned up: {system_info.name}")
            
        except Exception as e:
            print(f"System cleanup error for '{system_info.name}': {e}")
            system_info.state = SystemState.ERROR
    
    def _start_background_thread(self):
        """Start background thread for background priority systems."""
        if self.background_thread and self.background_running:
            return
        
        self.background_running = True
        self.background_thread = threading.Thread(target=self._background_update_loop, daemon=True)
        self.background_thread.start()
    
    def _background_update_loop(self):
        """Background thread update loop."""
        last_time = time.time()
        
        while self.background_running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Update background systems
            with self.thread_lock:
                background_systems = [
                    info for info in self.systems.values()
                    if info.priority == SystemPriority.BACKGROUND and info.state == SystemState.RUNNING
                ]
            
            for system_info in background_systems:
                self._update_system(system_info, dt)
            
            # Sleep to limit background update rate
            time.sleep(0.1)  # 10 FPS for background systems
    
    def pause_system(self, name: str) -> bool:
        """Pause a specific system."""
        if name not in self.systems:
            return False
        
        system_info = self.systems[name]
        if system_info.state == SystemState.RUNNING:
            system_info.state = SystemState.PAUSED
            
            # Emit pause event
            self.event_system.emit('system_paused', {'system_name': name})
            return True
        
        return False
    
    def resume_system(self, name: str) -> bool:
        """Resume a paused system."""
        if name not in self.systems:
            return False
        
        system_info = self.systems[name]
        if system_info.state == SystemState.PAUSED:
            system_info.state = SystemState.RUNNING
            
            # Emit resume event
            self.event_system.emit('system_resumed', {'system_name': name})
            return True
        
        return False
    
    def get_system_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific system."""
        if name not in self.systems:
            return None
        
        system_info = self.systems[name]
        return {
            'name': system_info.name,
            'priority': system_info.priority.value,
            'state': system_info.state.value,
            'update_time': system_info.update_time,
            'average_update_time': system_info.average_update_time,
            'update_count': system_info.update_count,
            'error_count': system_info.error_count,
            'last_error': system_info.last_error,
            'dependencies': system_info.dependencies,
            'dependents': system_info.dependents
        }
    
    def get_manager_info(self) -> Dict[str, Any]:
        """Get comprehensive manager information."""
        avg_frame_time = self.total_update_time / max(1, self.frame_count)
        
        return {
            'manager_state': self.manager_state.value,
            'initialization_progress': self.initialization_progress,
            'total_systems': len(self.systems),
            'running_systems': len([s for s in self.systems.values() if s.state == SystemState.RUNNING]),
            'paused_systems': len([s for s in self.systems.values() if s.state == SystemState.PAUSED]),
            'error_systems': len([s for s in self.systems.values() if s.state == SystemState.ERROR]),
            'average_frame_time': avg_frame_time,
            'frame_count': self.frame_count,
            'global_error_count': self.global_error_count,
            'update_order': self.update_order.copy(),
            'event_info': self.event_system.get_event_info()
        }
    
    def shutdown(self):
        """Shutdown all systems and the manager."""
        print("Shutting down integration manager...")
        
        self.manager_state = SystemState.SHUTTING_DOWN
        
        # Stop background thread
        self.background_running = False
        if self.background_thread:
            self.background_thread.join(timeout=5.0)
        
        # Cleanup all systems in reverse order
        for system_name in reversed(self.update_order):
            if system_name in self.systems:
                system_info = self.systems[system_name]
                self._cleanup_system(system_info)
        
        # Clear registry
        self.systems.clear()
        self.update_order.clear()
        
        self.manager_state = SystemState.SHUTDOWN
        print("Integration manager shutdown complete")
    
    # Event system wrapper methods
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event."""
        self.event_system.subscribe(event_type, callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event."""
        self.event_system.unsubscribe(event_type, callback)
    
    def emit_event(self, event_type: str, data: Dict[str, Any] = None, immediate: bool = False):
        """Emit an event."""
        self.event_system.emit(event_type, data, immediate)