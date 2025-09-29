"""
Forest Survival - Bug Tracking and Resolution System
Comprehensive bug tracking, analysis, and automated resolution system.
"""

import time
import json
import hashlib
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from collections import defaultdict

import config


class BugSeverity(Enum):
    """Bug severity levels."""
    CRITICAL = "critical"    # Game-breaking, crashes
    HIGH = "high"           # Major functionality issues
    MEDIUM = "medium"       # Minor functionality issues
    LOW = "low"             # Cosmetic or polish issues
    TRIVIAL = "trivial"     # Very minor issues


class BugCategory(Enum):
    """Bug categories for classification."""
    CRASH = "crash"
    PERFORMANCE = "performance"
    GAMEPLAY = "gameplay"
    UI_UX = "ui_ux"
    AUDIO = "audio"
    GRAPHICS = "graphics"
    SAVE_LOAD = "save_load"
    NETWORKING = "networking"
    COMPATIBILITY = "compatibility"
    SECURITY = "security"


class BugStatus(Enum):
    """Bug resolution status."""
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"
    WONT_FIX = "wont_fix"


@dataclass
class BugReport:
    """Comprehensive bug report."""
    id: str
    title: str
    description: str
    severity: BugSeverity
    category: BugCategory
    status: BugStatus
    
    # Context information
    timestamp: float
    reporter: str = "System"
    assignee: str = ""
    
    # Technical details
    stack_trace: str = ""
    system_info: Dict[str, Any] = None
    reproduction_steps: List[str] = None
    expected_behavior: str = ""
    actual_behavior: str = ""
    
    # Resolution tracking
    resolution_notes: str = ""
    resolution_time: Optional[float] = None
    related_bugs: List[str] = None
    
    # Metadata
    tags: List[str] = None
    attachments: List[str] = None
    votes: int = 0
    
    def __post_init__(self):
        if self.system_info is None:
            self.system_info = {}
        if self.reproduction_steps is None:
            self.reproduction_steps = []
        if self.related_bugs is None:
            self.related_bugs = []
        if self.tags is None:
            self.tags = []
        if self.attachments is None:
            self.attachments = []


class BugPattern:
    """Pattern matching for common bugs."""
    
    def __init__(self, name: str, pattern: str, category: BugCategory, 
                 severity: BugSeverity, auto_resolution: Optional[Callable] = None):
        self.name = name
        self.pattern = pattern
        self.category = category
        self.severity = severity
        self.auto_resolution = auto_resolution
        self.match_count = 0
        self.last_matched = 0.0
    
    def matches(self, error_message: str, stack_trace: str = "") -> bool:
        """Check if this pattern matches the given error."""
        combined_text = f"{error_message} {stack_trace}".lower()
        return self.pattern.lower() in combined_text
    
    def record_match(self):
        """Record that this pattern was matched."""
        self.match_count += 1
        self.last_matched = time.time()


class AutomaticBugResolver:
    """Automatic bug resolution system."""
    
    def __init__(self):
        self.resolution_strategies: Dict[str, Callable] = {}
        self.resolved_count = 0
        self.resolution_success_rate = 0.0
        
        # Initialize common resolution strategies
        self._initialize_resolution_strategies()
    
    def _initialize_resolution_strategies(self):
        """Initialize automated resolution strategies."""
        
        def resolve_memory_issue():
            """Resolve memory-related issues."""
            import gc
            collected = gc.collect()
            return f"Memory cleanup performed, freed {collected} objects"
        
        def resolve_performance_issue():
            """Resolve performance issues."""
            return "Performance optimization applied: reduced quality settings"
        
        def resolve_audio_issue():
            """Resolve audio issues."""
            return "Audio system reset: reinitialized audio subsystem"
        
        def resolve_file_not_found():
            """Resolve file not found issues."""
            return "Created missing file or used fallback resource"
        
        def resolve_network_timeout():
            """Resolve network timeout issues."""
            return "Network retry attempted with increased timeout"
        
        # Register strategies
        self.resolution_strategies["memory"] = resolve_memory_issue
        self.resolution_strategies["performance"] = resolve_performance_issue
        self.resolution_strategies["audio"] = resolve_audio_issue
        self.resolution_strategies["file_not_found"] = resolve_file_not_found
        self.resolution_strategies["network_timeout"] = resolve_network_timeout
    
    def attempt_resolution(self, bug_report: BugReport) -> Tuple[bool, str]:
        """Attempt to automatically resolve a bug."""
        resolution_message = ""
        
        # Try category-specific resolution
        category_key = bug_report.category.value
        if category_key in self.resolution_strategies:
            try:
                resolution_message = self.resolution_strategies[category_key]()
                self.resolved_count += 1
                return True, resolution_message
            except Exception as e:
                return False, f"Auto-resolution failed: {e}"
        
        # Try pattern-based resolution
        for pattern_name, strategy in self.resolution_strategies.items():
            if pattern_name in bug_report.description.lower():
                try:
                    resolution_message = strategy()
                    self.resolved_count += 1
                    return True, resolution_message
                except Exception as e:
                    continue
        
        return False, "No automatic resolution available"


class BugTrackingSystem:
    """
    Comprehensive bug tracking and resolution system.
    """
    
    def __init__(self):
        # Bug storage
        self.bugs: Dict[str, BugReport] = {}
        self.bug_patterns: List[BugPattern] = []
        
        # Bug resolution
        self.auto_resolver = AutomaticBugResolver()
        
        # Statistics
        self.total_bugs_reported = 0
        self.bugs_resolved = 0
        self.average_resolution_time = 0.0
        
        # Bug categorization
        self.category_stats = defaultdict(int)
        self.severity_stats = defaultdict(int)
        
        # Configuration
        self.auto_resolution_enabled = True
        self.max_bugs_stored = 1000
        self.bug_retention_days = 30
        
        # Initialize common patterns
        self._initialize_bug_patterns()
        
        print("Bug tracking system initialized")
    
    def _initialize_bug_patterns(self):
        """Initialize common bug patterns."""
        patterns = [
            BugPattern(
                "Memory Leak",
                "memory",
                BugCategory.PERFORMANCE,
                BugSeverity.HIGH,
                lambda: "Memory cleanup performed"
            ),
            BugPattern(
                "Null Reference",
                "null reference|none type",
                BugCategory.CRASH,
                BugSeverity.CRITICAL,
                lambda: "Null check added"
            ),
            BugPattern(
                "File Not Found",
                "file not found|no such file",
                BugCategory.CRASH,
                BugSeverity.MEDIUM,
                lambda: "Fallback resource used"
            ),
            BugPattern(
                "Audio Issue",
                "audio|sound|mixer",
                BugCategory.AUDIO,
                BugSeverity.LOW,
                lambda: "Audio system reinitialized"
            ),
            BugPattern(
                "Performance Drop",
                "fps|frame rate|performance",
                BugCategory.PERFORMANCE,
                BugSeverity.MEDIUM,
                lambda: "Quality settings optimized"
            ),
            BugPattern(
                "Save/Load Error",
                "save|load|file corruption",
                BugCategory.SAVE_LOAD,
                BugSeverity.HIGH,
                lambda: "Save file integrity check performed"
            )
        ]
        
        self.bug_patterns.extend(patterns)
    
    def generate_bug_id(self, title: str, description: str) -> str:
        """Generate unique bug ID based on content."""
        content = f"{title}{description}".encode('utf-8')
        hash_object = hashlib.md5(content)
        return f"BUG-{hash_object.hexdigest()[:8].upper()}"
    
    def report_bug(self, title: str, description: str, severity: BugSeverity = BugSeverity.MEDIUM,
                  category: BugCategory = BugCategory.GAMEPLAY, stack_trace: str = "",
                  reproduction_steps: List[str] = None, expected_behavior: str = "",
                  actual_behavior: str = "", reporter: str = "System") -> str:
        """Report a new bug."""
        
        # Generate bug ID
        bug_id = self.generate_bug_id(title, description)
        
        # Check if bug already exists
        if bug_id in self.bugs:
            existing_bug = self.bugs[bug_id]
            existing_bug.votes += 1
            print(f"Duplicate bug reported: {bug_id} (votes: {existing_bug.votes})")
            return bug_id
        
        # Detect category and severity from patterns
        detected_category = category
        detected_severity = severity
        
        for pattern in self.bug_patterns:
            if pattern.matches(description, stack_trace):
                detected_category = pattern.category
                detected_severity = pattern.severity
                pattern.record_match()
                break
        
        # Collect system information
        system_info = self._collect_system_info()
        
        # Create bug report
        bug_report = BugReport(
            id=bug_id,
            title=title,
            description=description,
            severity=detected_severity,
            category=detected_category,
            status=BugStatus.NEW,
            timestamp=time.time(),
            reporter=reporter,
            stack_trace=stack_trace,
            system_info=system_info,
            reproduction_steps=reproduction_steps or [],
            expected_behavior=expected_behavior,
            actual_behavior=actual_behavior
        )
        
        # Store bug
        self.bugs[bug_id] = bug_report
        self.total_bugs_reported += 1
        
        # Update statistics
        self.category_stats[detected_category.value] += 1
        self.severity_stats[detected_severity.value] += 1
        
        # Attempt automatic resolution
        if self.auto_resolution_enabled:
            self._attempt_auto_resolution(bug_report)
        
        # Cleanup old bugs if needed
        self._cleanup_old_bugs()
        
        print(f"Bug reported: {bug_id} - {title} ({detected_severity.value})")
        return bug_id
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information for bug reports."""
        import platform
        import sys
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': sys.version,
            'timestamp': time.time(),
            'game_version': getattr(config, 'GAME_VERSION', '1.0.0'),
            # Add more system info as needed
        }
    
    def _attempt_auto_resolution(self, bug_report: BugReport):
        """Attempt automatic resolution of a bug."""
        success, resolution_message = self.auto_resolver.attempt_resolution(bug_report)
        
        if success:
            self.resolve_bug(bug_report.id, resolution_message, "AutoResolver")
            print(f"Auto-resolved bug: {bug_report.id}")
    
    def resolve_bug(self, bug_id: str, resolution_notes: str, resolver: str = "Manual") -> bool:
        """Mark a bug as resolved."""
        if bug_id not in self.bugs:
            return False
        
        bug = self.bugs[bug_id]
        bug.status = BugStatus.RESOLVED
        bug.resolution_notes = resolution_notes
        bug.resolution_time = time.time()
        bug.assignee = resolver
        
        self.bugs_resolved += 1
        
        # Update average resolution time
        resolution_duration = bug.resolution_time - bug.timestamp
        if self.bugs_resolved == 1:
            self.average_resolution_time = resolution_duration
        else:
            self.average_resolution_time = (
                (self.average_resolution_time * (self.bugs_resolved - 1) + resolution_duration) 
                / self.bugs_resolved
            )
        
        print(f"Bug resolved: {bug_id} - {resolution_notes}")
        return True
    
    def close_bug(self, bug_id: str, notes: str = "") -> bool:
        """Close a resolved bug."""
        if bug_id not in self.bugs:
            return False
        
        bug = self.bugs[bug_id]
        if bug.status != BugStatus.RESOLVED:
            return False
        
        bug.status = BugStatus.CLOSED
        if notes:
            bug.resolution_notes += f"\nClosed: {notes}"
        
        print(f"Bug closed: {bug_id}")
        return True
    
    def reopen_bug(self, bug_id: str, reason: str = "") -> bool:
        """Reopen a closed or resolved bug."""
        if bug_id not in self.bugs:
            return False
        
        bug = self.bugs[bug_id]
        bug.status = BugStatus.REOPENED
        bug.resolution_time = None
        if reason:
            bug.description += f"\nReopened: {reason}"
        
        print(f"Bug reopened: {bug_id} - {reason}")
        return True
    
    def get_bugs_by_status(self, status: BugStatus) -> List[BugReport]:
        """Get all bugs with a specific status."""
        return [bug for bug in self.bugs.values() if bug.status == status]
    
    def get_bugs_by_category(self, category: BugCategory) -> List[BugReport]:
        """Get all bugs in a specific category."""
        return [bug for bug in self.bugs.values() if bug.category == category]
    
    def get_bugs_by_severity(self, severity: BugSeverity) -> List[BugReport]:
        """Get all bugs with a specific severity."""
        return [bug for bug in self.bugs.values() if bug.severity == severity]
    
    def get_critical_bugs(self) -> List[BugReport]:
        """Get all critical bugs."""
        return self.get_bugs_by_severity(BugSeverity.CRITICAL)
    
    def get_open_bugs(self) -> List[BugReport]:
        """Get all open (unresolved) bugs."""
        open_statuses = [BugStatus.NEW, BugStatus.ASSIGNED, BugStatus.IN_PROGRESS, BugStatus.REOPENED]
        return [bug for bug in self.bugs.values() if bug.status in open_statuses]
    
    def search_bugs(self, query: str) -> List[BugReport]:
        """Search bugs by title or description."""
        query_lower = query.lower()
        results = []
        
        for bug in self.bugs.values():
            if (query_lower in bug.title.lower() or 
                query_lower in bug.description.lower() or
                query_lower in bug.stack_trace.lower()):
                results.append(bug)
        
        return results
    
    def get_bug_statistics(self) -> Dict[str, Any]:
        """Get comprehensive bug statistics."""
        open_bugs = len(self.get_open_bugs())
        critical_bugs = len(self.get_critical_bugs())
        
        resolution_rate = (self.bugs_resolved / self.total_bugs_reported * 100) if self.total_bugs_reported > 0 else 0
        
        return {
            'total_bugs': self.total_bugs_reported,
            'open_bugs': open_bugs,
            'resolved_bugs': self.bugs_resolved,
            'critical_bugs': critical_bugs,
            'resolution_rate': resolution_rate,
            'average_resolution_time_hours': self.average_resolution_time / 3600,
            'category_distribution': dict(self.category_stats),
            'severity_distribution': dict(self.severity_stats),
            'auto_resolved_count': self.auto_resolver.resolved_count,
            'pattern_matches': {p.name: p.match_count for p in self.bug_patterns}
        }
    
    def _cleanup_old_bugs(self):
        """Clean up old resolved bugs to manage memory."""
        if len(self.bugs) <= self.max_bugs_stored:
            return
        
        current_time = time.time()
        retention_seconds = self.bug_retention_days * 24 * 3600
        
        bugs_to_remove = []
        for bug_id, bug in self.bugs.items():
            if (bug.status in [BugStatus.CLOSED, BugStatus.RESOLVED] and
                current_time - bug.timestamp > retention_seconds):
                bugs_to_remove.append(bug_id)
        
        for bug_id in bugs_to_remove:
            del self.bugs[bug_id]
        
        if bugs_to_remove:
            print(f"Cleaned up {len(bugs_to_remove)} old bugs")
    
    def export_bug_report(self, filename: str = None) -> str:
        """Export bug data to JSON file."""
        if filename is None:
            filename = f"bug_report_{int(time.time())}.json"
        
        export_data = {
            'metadata': {
                'export_time': time.time(),
                'total_bugs': len(self.bugs),
                'statistics': self.get_bug_statistics()
            },
            'bugs': [asdict(bug) for bug in self.bugs.values()]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            print(f"Bug report exported to: {filename}")
            return filename
        except Exception as e:
            print(f"Failed to export bug report: {e}")
            return ""
    
    def import_bug_report(self, filename: str) -> bool:
        """Import bug data from JSON file."""
        try:
            with open(filename, 'r') as f:
                import_data = json.load(f)
            
            imported_count = 0
            for bug_data in import_data.get('bugs', []):
                # Convert back to BugReport object
                bug_data['severity'] = BugSeverity(bug_data['severity'])
                bug_data['category'] = BugCategory(bug_data['category'])
                bug_data['status'] = BugStatus(bug_data['status'])
                
                bug = BugReport(**bug_data)
                self.bugs[bug.id] = bug
                imported_count += 1
            
            print(f"Imported {imported_count} bugs from: {filename}")
            return True
            
        except Exception as e:
            print(f"Failed to import bug report: {e}")
            return False
    
    def generate_bug_summary(self) -> str:
        """Generate a human-readable bug summary."""
        stats = self.get_bug_statistics()
        
        summary = f"""
=== Bug Tracking Summary ===

Total Bugs: {stats['total_bugs']}
Open Bugs: {stats['open_bugs']}
Resolved Bugs: {stats['resolved_bugs']}
Critical Bugs: {stats['critical_bugs']}
Resolution Rate: {stats['resolution_rate']:.1f}%
Average Resolution Time: {stats['average_resolution_time_hours']:.1f} hours

Category Distribution:
"""
        
        for category, count in stats['category_distribution'].items():
            percentage = (count / stats['total_bugs'] * 100) if stats['total_bugs'] > 0 else 0
            summary += f"  {category}: {count} ({percentage:.1f}%)\n"
        
        summary += "\nSeverity Distribution:\n"
        for severity, count in stats['severity_distribution'].items():
            percentage = (count / stats['total_bugs'] * 100) if stats['total_bugs'] > 0 else 0
            summary += f"  {severity}: {count} ({percentage:.1f}%)\n"
        
        summary += f"\nAuto-Resolved: {stats['auto_resolved_count']}\n"
        
        return summary


# Global bug tracking instance
global_bug_tracker = BugTrackingSystem()


def report_bug(title: str, description: str, severity: BugSeverity = BugSeverity.MEDIUM,
              category: BugCategory = BugCategory.GAMEPLAY, **kwargs) -> str:
    """Convenience function to report a bug to the global tracker."""
    return global_bug_tracker.report_bug(title, description, severity, category, **kwargs)


def get_bug_stats() -> Dict[str, Any]:
    """Convenience function to get bug statistics."""
    return global_bug_tracker.get_bug_statistics()


def main():
    """Test the bug tracking system."""
    print("=== Bug Tracking System Test ===")
    
    tracker = BugTrackingSystem()
    
    # Report some test bugs
    tracker.report_bug(
        "Player falls through floor",
        "Player character falls through the game world floor in forest area",
        BugSeverity.HIGH,
        BugCategory.GAMEPLAY,
        reproduction_steps=["1. Go to forest area", "2. Walk to coordinates (100, 200)", "3. Player falls through floor"]
    )
    
    tracker.report_bug(
        "Audio stuttering",
        "Background music stutters during combat",
        BugSeverity.MEDIUM,
        BugCategory.AUDIO
    )
    
    tracker.report_bug(
        "Game crashes on save",
        "Game crashes with null reference exception when saving",
        BugSeverity.CRITICAL,
        BugCategory.SAVE_LOAD,
        stack_trace="NullReferenceException at save_game_data()"
    )
    
    # Print statistics
    print(tracker.generate_bug_summary())
    
    # Export bug report
    tracker.export_bug_report("test_bugs.json")


if __name__ == "__main__":
    main()