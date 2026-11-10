"""Placeholder results used to live here. The real suite is pytest in tests/."""

from enum import Enum


class TestType(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    STRESS = "stress"
    REGRESSION = "regression"
    USER_ACCEPTANCE = "user_acceptance"


class ComprehensiveTestSuite:
    """Kept so old imports load. It does not invent passing tests."""

    def run_all_tests(self):
        raise RuntimeError("Run pytest. This module no longer reports fabricated results.")


def create_comprehensive_test_suite() -> ComprehensiveTestSuite:
    return ComprehensiveTestSuite()
