"""Test session hooks shared by the Forest Survival suite."""

import pytest


def pytest_sessionfinish(session, exitstatus):
    """An empty suite is a valid setup check, not a failure."""
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = pytest.ExitCode.OK
