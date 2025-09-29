"""
Forest Survival - Final Integration Coordinator
Coordinates final system integration, testing, and validation.
"""

import time
import threading
import json
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

import config
from src.core.enhanced_integration import EnhancedIntegrationManager
from src.testing.comprehensive_test_suite import ComprehensiveTestSuite, create_comprehensive_test_suite
from src.testing.bug_tracking import BugTrackingSystem, BugSeverity, BugCategory
from src.effects.performance_optimization import PerformanceOptimizationSystem


class IntegrationPhase(Enum):
    """Integration phases."""
    INITIALIZATION = "initialization"
    SYSTEM_VALIDATION = "system_validation"
    INTEGRATION_TESTING = "integration_testing"
    PERFORMANCE_TESTING = "performance_testing"
    STRESS_TESTING = "stress_testing"
    BUG_FIXING = "bug_fixing"
    FINAL_VALIDATION = "final_validation"
    COMPLETE = "complete"


class ValidationResult(Enum):
    """Validation result status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class IntegrationReport:
    """Comprehensive integration report."""
    phase: IntegrationPhase
    status: ValidationResult
    timestamp: float
    duration: float
    
    # Results
    message: str
    details: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]
    
    # Metrics
    systems_tested: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    bugs_found: int = 0
    performance_score: float = 0.0


class FinalIntegrationCoordinator:
    """
    Coordinates the final integration process for the Forest Survival game.
    """
    
    def __init__(self):
        # Core components
        self.integration_manager = EnhancedIntegrationManager()
        self.test_suite = create_comprehensive_test_suite()
        self.bug_tracker = BugTrackingSystem()
        self.performance_system = PerformanceOptimizationSystem()
        
        # Integration state
        self.current_phase = IntegrationPhase.INITIALIZATION
        self.integration_running = False
        self.integration_thread = None
        
        # Results tracking
        self.phase_reports: List[IntegrationReport] = []
        self.overall_status = ValidationResult.FAILED
        self.start_time = 0.0
        self.end_time = 0.0
        
        # Configuration
        self.auto_fix_enabled = True
        self.performance_target_fps = 60
        self.max_acceptable_bugs = 5
        self.stress_test_duration = 300  # 5 minutes
        
        # System requirements
        self.required_systems = [
            "game_state_manager",
            "player_controller",
            "world_manager",
            "visual_effects",
            "audio_manager",
            "performance_system"
        ]
        
        # Integration callbacks
        self.phase_callbacks: Dict[IntegrationPhase, List[Callable]] = {}
        
        print("Final integration coordinator initialized")
    
    def add_phase_callback(self, phase: IntegrationPhase, callback: Callable):
        """Add a callback for a specific integration phase."""
        if phase not in self.phase_callbacks:
            self.phase_callbacks[phase] = []
        self.phase_callbacks[phase].append(callback)
    
    def _trigger_phase_callbacks(self, phase: IntegrationPhase, report: IntegrationReport):
        """Trigger callbacks for a specific phase."""
        if phase in self.phase_callbacks:
            for callback in self.phase_callbacks[phase]:
                try:
                    callback(report)
                except Exception as e:
                    print(f"Phase callback error: {e}")
    
    def start_integration(self) -> bool:
        """Start the complete integration process."""
        if self.integration_running:
            print("Integration already in progress")
            return False
        
        print("=== Starting Final Integration Process ===")
        
        self.integration_running = True
        self.start_time = time.time()
        self.phase_reports.clear()
        self.overall_status = ValidationResult.FAILED
        
        # Run integration in separate thread for non-blocking operation
        self.integration_thread = threading.Thread(target=self._run_integration, daemon=True)
        self.integration_thread.start()
        
        return True
    
    def _run_integration(self):
        """Run the complete integration process."""
        try:
            # Phase 1: Initialization
            if not self._run_initialization_phase():
                return
            
            # Phase 2: System Validation
            if not self._run_system_validation_phase():
                return
            
            # Phase 3: Integration Testing
            if not self._run_integration_testing_phase():
                return
            
            # Phase 4: Performance Testing
            if not self._run_performance_testing_phase():
                return
            
            # Phase 5: Stress Testing
            if not self._run_stress_testing_phase():
                return
            
            # Phase 6: Bug Fixing
            if not self._run_bug_fixing_phase():
                return
            
            # Phase 7: Final Validation
            if not self._run_final_validation_phase():
                return
            
            # Mark as complete
            self.current_phase = IntegrationPhase.COMPLETE
            self.overall_status = ValidationResult.PASSED
            
            print("=== Integration Process Complete ===")
            
        except Exception as e:
            print(f"Integration process failed: {e}")
            self.bug_tracker.report_bug(
                "Integration Process Failure",
                f"The integration process failed with error: {str(e)}",
                BugSeverity.CRITICAL,
                BugCategory.CRASH,
                stack_trace=str(e)
            )
        
        finally:
            self.integration_running = False
            self.end_time = time.time()
    
    def _run_initialization_phase(self) -> bool:
        """Run initialization phase."""
        print("\n--- Phase 1: Initialization ---")
        self.current_phase = IntegrationPhase.INITIALIZATION
        phase_start = time.time()
        
        issues = []
        recommendations = []
        
        try:
            # Initialize core systems
            if not self.integration_manager.initialize_systems():
                issues.append("Failed to initialize core systems")
                
            # Initialize performance monitoring
            self.performance_system.optimize_for_target(self.performance_target_fps)
            
            # Validate required systems
            missing_systems = []
            for required_system in self.required_systems:
                if required_system not in self.integration_manager.systems:
                    missing_systems.append(required_system)
            
            if missing_systems:
                issues.append(f"Missing required systems: {', '.join(missing_systems)}")
            
            # Determine phase result
            status = ValidationResult.PASSED if not issues else ValidationResult.FAILED
            
            # Create report
            report = IntegrationReport(
                phase=IntegrationPhase.INITIALIZATION,
                status=status,
                timestamp=time.time(),
                duration=time.time() - phase_start,
                message="System initialization completed" if status == ValidationResult.PASSED else "Initialization failed",
                details={
                    'initialized_systems': len(self.integration_manager.systems),
                    'required_systems': len(self.required_systems),
                    'missing_systems': missing_systems
                },
                issues=issues,
                recommendations=recommendations,
                systems_tested=len(self.integration_manager.systems)
            )
            
            self.phase_reports.append(report)
            self._trigger_phase_callbacks(IntegrationPhase.INITIALIZATION, report)
            
            print(f"Initialization: {status.value} ({report.duration:.2f}s)")
            return status == ValidationResult.PASSED
            
        except Exception as e:
            self.bug_tracker.report_bug(
                "Initialization Phase Error",
                f"Error during initialization: {str(e)}",
                BugSeverity.CRITICAL,
                BugCategory.CRASH
            )
            return False
    
    def _run_system_validation_phase(self) -> bool:
        """Run system validation phase."""
        print("\n--- Phase 2: System Validation ---")
        self.current_phase = IntegrationPhase.SYSTEM_VALIDATION
        phase_start = time.time()
        
        issues = []
        recommendations = []
        systems_tested = 0
        
        try:
            # Validate each system
            for system_name, system_info in self.integration_manager.systems.items():
                systems_tested += 1
                
                # Check system state
                if system_info.state != system_info.state.RUNNING:
                    issues.append(f"System '{system_name}' not in running state: {system_info.state.value}")
                
                # Check for errors
                if system_info.error_count > 0:
                    issues.append(f"System '{system_name}' has {system_info.error_count} errors")
                
                # Check update performance
                if system_info.average_update_time > 5.0:  # 5ms threshold
                    recommendations.append(f"System '{system_name}' update time high: {system_info.average_update_time:.2f}ms")
            
            # Check system dependencies
            for system_name, system_info in self.integration_manager.systems.items():
                for dependency in system_info.dependencies:
                    if dependency not in self.integration_manager.systems:
                        issues.append(f"System '{system_name}' missing dependency: {dependency}")
            
            status = ValidationResult.PASSED if not issues else ValidationResult.WARNING
            
            report = IntegrationReport(
                phase=IntegrationPhase.SYSTEM_VALIDATION,
                status=status,
                timestamp=time.time(),
                duration=time.time() - phase_start,
                message=f"Validated {systems_tested} systems",
                details={
                    'systems_validated': systems_tested,
                    'systems_with_errors': len([s for s in self.integration_manager.systems.values() if s.error_count > 0]),
                    'dependency_issues': len([i for i in issues if 'dependency' in i])
                },
                issues=issues,
                recommendations=recommendations,
                systems_tested=systems_tested
            )
            
            self.phase_reports.append(report)
            self._trigger_phase_callbacks(IntegrationPhase.SYSTEM_VALIDATION, report)
            
            print(f"System Validation: {status.value} ({report.duration:.2f}s)")
            return True  # Continue even with warnings
            
        except Exception as e:
            self.bug_tracker.report_bug(
                "System Validation Error",
                f"Error during system validation: {str(e)}",
                BugSeverity.HIGH,
                BugCategory.CRASH
            )
            return False
    
    def _run_integration_testing_phase(self) -> bool:
        """Run integration testing phase."""
        print("\n--- Phase 3: Integration Testing ---")
        self.current_phase = IntegrationPhase.INTEGRATION_TESTING
        phase_start = time.time()
        
        try:
            # Run integration tests
            from src.testing.comprehensive_test_suite import TestType
            test_results = self.test_suite.run_tests_by_type(TestType.INTEGRATION)
            
            # Analyze results
            total_tests = test_results.get('total_tests', 0)
            passed_tests = test_results.get('passed', 0)
            failed_tests = test_results.get('failed', 0)
            
            issues = []
            if failed_tests > 0:
                issues.append(f"{failed_tests} integration tests failed")
            
            # Report any test failures as bugs
            for result in test_results.get('results', []):
                if result.status.value in ['failed', 'error']:
                    self.bug_tracker.report_bug(
                        f"Test Failure: {result.test_name}",
                        result.message,
                        BugSeverity.MEDIUM,
                        BugCategory.CRASH
                    )
            
            status = ValidationResult.PASSED if failed_tests == 0 else ValidationResult.WARNING
            
            report = IntegrationReport(
                phase=IntegrationPhase.INTEGRATION_TESTING,
                status=status,
                timestamp=time.time(),
                duration=time.time() - phase_start,
                message=f"Integration testing completed: {passed_tests}/{total_tests} passed",
                details=test_results,
                issues=issues,
                recommendations=[],
                systems_tested=total_tests,
                tests_passed=passed_tests,
                tests_failed=failed_tests
            )
            
            self.phase_reports.append(report)
            self._trigger_phase_callbacks(IntegrationPhase.INTEGRATION_TESTING, report)
            
            print(f"Integration Testing: {status.value} ({report.duration:.2f}s)")
            return True
            
        except Exception as e:
            self.bug_tracker.report_bug(
                "Integration Testing Error",
                f"Error during integration testing: {str(e)}",
                BugSeverity.HIGH,
                BugCategory.CRASH
            )
            return False
    
    def _run_performance_testing_phase(self) -> bool:
        """Run performance testing phase."""
        print("\n--- Phase 4: Performance Testing ---")
        self.current_phase = IntegrationPhase.PERFORMANCE_TESTING
        phase_start = time.time()
        
        try:
            # Run performance tests
            from src.testing.comprehensive_test_suite import TestType
            test_results = self.test_suite.run_tests_by_type(TestType.PERFORMANCE)
            
            # Get current performance metrics
            perf_info = self.performance_system.get_optimization_info()
            fps_info = perf_info['fps_info']
            
            issues = []
            recommendations = []
            
            # Check FPS performance
            current_fps = fps_info.get('current_fps', 0)
            if current_fps < self.performance_target_fps * 0.8:
                issues.append(f"FPS below target: {current_fps:.1f} < {self.performance_target_fps * 0.8:.1f}")
                recommendations.append("Consider enabling aggressive optimization")
            
            # Check memory usage
            memory_info = perf_info['memory_info']
            if memory_info.get('is_warning', False):
                recommendations.append("Memory usage is high, consider cleanup")
            
            # Calculate performance score
            fps_score = min(1.0, current_fps / self.performance_target_fps)
            memory_score = 1.0 - min(1.0, memory_info.get('current_mb', 0) / 1024)  # 1GB baseline
            performance_score = (fps_score + memory_score) / 2.0
            
            status = ValidationResult.PASSED if performance_score >= 0.7 else ValidationResult.WARNING
            
            report = IntegrationReport(
                phase=IntegrationPhase.PERFORMANCE_TESTING,
                status=status,
                timestamp=time.time(),
                duration=time.time() - phase_start,
                message=f"Performance testing completed (score: {performance_score:.2f})",
                details={
                    'fps_info': fps_info,
                    'memory_info': memory_info,
                    'performance_score': performance_score,
                    'test_results': test_results
                },
                issues=issues,
                recommendations=recommendations,
                performance_score=performance_score
            )
            
            self.phase_reports.append(report)
            self._trigger_phase_callbacks(IntegrationPhase.PERFORMANCE_TESTING, report)
            
            print(f"Performance Testing: {status.value} (score: {performance_score:.2f})")
            return True
            
        except Exception as e:
            self.bug_tracker.report_bug(
                "Performance Testing Error",
                f"Error during performance testing: {str(e)}",
                BugSeverity.MEDIUM,
                BugCategory.PERFORMANCE
            )
            return False
    
    def _run_stress_testing_phase(self) -> bool:
        """Run stress testing phase."""
        print("\n--- Phase 5: Stress Testing ---")
        self.current_phase = IntegrationPhase.STRESS_TESTING
        phase_start = time.time()
        
        try:
            # Run stress tests
            from src.testing.comprehensive_test_suite import TestType
            test_results = self.test_suite.run_tests_by_type(TestType.STRESS)
            
            # Monitor system during stress test
            issues = []
            recommendations = []
            
            # Check for system instability
            error_systems = [
                name for name, info in self.integration_manager.systems.items()
                if info.error_count > 5
            ]
            
            if error_systems:
                issues.append(f"Systems with high error counts: {', '.join(error_systems)}")
            
            # Check for memory leaks
            memory_info = self.performance_system.memory_manager.get_memory_info()
            if memory_info.get('is_critical', False):
                issues.append("Critical memory usage detected during stress test")
            
            status = ValidationResult.PASSED if not issues else ValidationResult.WARNING
            
            report = IntegrationReport(
                phase=IntegrationPhase.STRESS_TESTING,
                status=status,
                timestamp=time.time(),
                duration=time.time() - phase_start,
                message=f"Stress testing completed",
                details={
                    'test_results': test_results,
                    'error_systems': error_systems,
                    'memory_info': memory_info
                },
                issues=issues,
                recommendations=recommendations
            )
            
            self.phase_reports.append(report)
            self._trigger_phase_callbacks(IntegrationPhase.STRESS_TESTING, report)
            
            print(f"Stress Testing: {status.value} ({report.duration:.2f}s)")
            return True
            
        except Exception as e:
            self.bug_tracker.report_bug(
                "Stress Testing Error",
                f"Error during stress testing: {str(e)}",
                BugSeverity.MEDIUM,
                BugCategory.PERFORMANCE
            )
            return False
    
    def _run_bug_fixing_phase(self) -> bool:
        """Run bug fixing phase."""
        print("\n--- Phase 6: Bug Fixing ---")
        self.current_phase = IntegrationPhase.BUG_FIXING
        phase_start = time.time()
        
        try:
            # Get current bug statistics
            bug_stats = self.bug_tracker.get_bug_statistics()
            critical_bugs = self.bug_tracker.get_critical_bugs()
            open_bugs = self.bug_tracker.get_open_bugs()
            
            issues = []
            recommendations = []
            
            # Attempt automatic bug resolution
            auto_fixed = 0
            if self.auto_fix_enabled:
                for bug in open_bugs[:10]:  # Limit to first 10 bugs
                    success, resolution = self.bug_tracker.auto_resolver.attempt_resolution(bug)
                    if success:
                        self.bug_tracker.resolve_bug(bug.id, resolution, "AutoFixer")
                        auto_fixed += 1
            
            # Check remaining critical bugs
            remaining_critical = len([b for b in open_bugs if b.severity == BugSeverity.CRITICAL])
            if remaining_critical > 0:
                issues.append(f"{remaining_critical} critical bugs remain unresolved")
            
            # Check total open bugs
            remaining_open = len(open_bugs) - auto_fixed
            if remaining_open > self.max_acceptable_bugs:
                recommendations.append(f"Consider manual review of {remaining_open} open bugs")
            
            status = ValidationResult.PASSED if remaining_critical == 0 else ValidationResult.WARNING
            
            report = IntegrationReport(
                phase=IntegrationPhase.BUG_FIXING,
                status=status,
                timestamp=time.time(),
                duration=time.time() - phase_start,
                message=f"Bug fixing completed: {auto_fixed} bugs auto-fixed",
                details={
                    'bug_stats': bug_stats,
                    'auto_fixed': auto_fixed,
                    'remaining_critical': remaining_critical,
                    'remaining_open': remaining_open
                },
                issues=issues,
                recommendations=recommendations,
                bugs_found=len(open_bugs)
            )
            
            self.phase_reports.append(report)
            self._trigger_phase_callbacks(IntegrationPhase.BUG_FIXING, report)
            
            print(f"Bug Fixing: {status.value} (auto-fixed: {auto_fixed})")
            return True
            
        except Exception as e:
            self.bug_tracker.report_bug(
                "Bug Fixing Phase Error",
                f"Error during bug fixing: {str(e)}",
                BugSeverity.HIGH,
                BugCategory.CRASH
            )
            return False
    
    def _run_final_validation_phase(self) -> bool:
        """Run final validation phase."""
        print("\n--- Phase 7: Final Validation ---")
        self.current_phase = IntegrationPhase.FINAL_VALIDATION
        phase_start = time.time()
        
        try:
            # Final system check
            all_systems_running = all(
                info.state.value == 'running' 
                for info in self.integration_manager.systems.values()
            )
            
            # Final performance check
            perf_info = self.performance_system.get_optimization_info()
            fps_acceptable = perf_info['fps_info'].get('current_fps', 0) >= self.performance_target_fps * 0.8
            
            # Final bug check
            critical_bugs = len(self.bug_tracker.get_critical_bugs())
            
            issues = []
            if not all_systems_running:
                issues.append("Not all systems are running")
            if not fps_acceptable:
                issues.append("Performance below acceptable threshold")
            if critical_bugs > 0:
                issues.append(f"{critical_bugs} critical bugs remain")
            
            status = ValidationResult.PASSED if not issues else ValidationResult.FAILED
            
            report = IntegrationReport(
                phase=IntegrationPhase.FINAL_VALIDATION,
                status=status,
                timestamp=time.time(),
                duration=time.time() - phase_start,
                message="Final validation completed" if status == ValidationResult.PASSED else "Final validation failed",
                details={
                    'all_systems_running': all_systems_running,
                    'fps_acceptable': fps_acceptable,
                    'critical_bugs': critical_bugs,
                    'final_performance': perf_info
                },
                issues=issues,
                recommendations=[]
            )
            
            self.phase_reports.append(report)
            self._trigger_phase_callbacks(IntegrationPhase.FINAL_VALIDATION, report)
            
            print(f"Final Validation: {status.value}")
            return status == ValidationResult.PASSED
            
        except Exception as e:
            self.bug_tracker.report_bug(
                "Final Validation Error",
                f"Error during final validation: {str(e)}",
                BugSeverity.CRITICAL,
                BugCategory.CRASH
            )
            return False
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status."""
        return {
            'current_phase': self.current_phase.value,
            'running': self.integration_running,
            'overall_status': self.overall_status.value,
            'progress': len(self.phase_reports) / 7,  # 7 total phases
            'phase_count': len(self.phase_reports),
            'total_duration': (self.end_time or time.time()) - self.start_time if self.start_time > 0 else 0,
            'bug_stats': self.bug_tracker.get_bug_statistics(),
            'performance_info': self.performance_system.get_optimization_info() if hasattr(self, 'performance_system') else {}
        }
    
    def generate_integration_report(self) -> str:
        """Generate comprehensive integration report."""
        status = self.get_integration_status()
        
        report = f"""
=== Forest Survival - Final Integration Report ===

Overall Status: {status['overall_status']}
Total Duration: {status['total_duration']:.2f} seconds
Progress: {status['progress'] * 100:.1f}%

Phase Results:
"""
        
        for phase_report in self.phase_reports:
            report += f"\n{phase_report.phase.value.title()}:\n"
            report += f"  Status: {phase_report.status.value}\n"
            report += f"  Duration: {phase_report.duration:.2f}s\n"
            report += f"  Message: {phase_report.message}\n"
            
            if phase_report.issues:
                report += "  Issues:\n"
                for issue in phase_report.issues:
                    report += f"    - {issue}\n"
            
            if phase_report.recommendations:
                report += "  Recommendations:\n"
                for rec in phase_report.recommendations:
                    report += f"    - {rec}\n"
        
        # Add bug summary
        bug_stats = status['bug_stats']
        report += f"""

Bug Summary:
  Total Bugs: {bug_stats['total_bugs']}
  Open Bugs: {bug_stats['open_bugs']}
  Critical Bugs: {bug_stats['critical_bugs']}
  Resolution Rate: {bug_stats['resolution_rate']:.1f}%
"""
        
        # Add performance summary
        if 'fps_info' in status['performance_info']:
            fps_info = status['performance_info']['fps_info']
            report += f"""
Performance Summary:
  Current FPS: {fps_info.get('current_fps', 0):.1f}
  Target FPS: {self.performance_target_fps}
  Frame Time: {fps_info.get('frame_time_ms', 0):.1f}ms
"""
        
        return report
    
    def stop_integration(self):
        """Stop the integration process."""
        self.integration_running = False
        print("Integration process stopped")


def main():
    """Test the integration coordinator."""
    print("=== Final Integration Coordinator Test ===")
    
    coordinator = FinalIntegrationCoordinator()
    
    # Add some test callbacks
    def phase_callback(report):
        print(f"Phase callback: {report.phase.value} - {report.status.value}")
    
    for phase in IntegrationPhase:
        coordinator.add_phase_callback(phase, phase_callback)
    
    # Start integration
    coordinator.start_integration()
    
    # Wait for completion (in real usage, this would be handled differently)
    while coordinator.integration_running:
        time.sleep(1)
        status = coordinator.get_integration_status()
        print(f"Progress: {status['progress'] * 100:.1f}% - {status['current_phase']}")
    
    # Print final report
    print(coordinator.generate_integration_report())


if __name__ == "__main__":
    main()