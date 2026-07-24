import pytest
from typing import Tuple, Literal

# Define type aliases for clarity
ExitCode = int
TestResult = Literal["PASS", "FAIL", "SKIP"]


def evaluate_test_run(exit_code: ExitCode) -> TestResult:
    """
    Evaluates the test run exit code according to bisect semantics.

    Args:
        exit_code: The non-zero return code from pytest execution.

    Returns:
        A string representing "PASS", "FAIL", or "SKIP".
    """
    if exit_code == 0:
        # All tests passed successfully
        return "PASS"
    elif exit_code == 1:
        # Tests failed (the primary failure state)
        return "FAIL"
    else:
        # Codes 2, 3, 4, 5 (Interruption, Internal Error, Collection/Usage Errors, No tests).
        # These indicate the system is broken or untestable at this point in history.
        # This maps directly to 'git bisect skip'.
        return "SKIP"


class TestHarness:
    """
    Mock class representing the system that interfaces with Git and pytest.
    In a real scenario, this would use subprocess/os execution logic.
    We simulate the output for testing purposes.
    """

    @staticmethod
    def run_pytest(mock_exit_code: int) -> ExitCode:
        """
        Simulates running pytest on a given commit and returning the exit code.
        In a real implementation, this would execute subprocess calls.
        """
        # SECURITY NOTE: We mock the execution result to avoid forbidden operations.
        return mock_exit_code


    @staticmethod
    def process_commit_test_run(mock_exit_code: int) -> Tuple[TestResult, bool]:
        """
        The core function that implements the bounty fix.
        It evaluates the exit code and determines if a definitive PASS/FAIL state was reached.

        Returns: (TestResult, IsTestableForBisection)
        """
        result = evaluate_test_run(mock_exit_code)

        # Determine if we can continue bisecting based on the result
        if result == "PASS" or result == "FAIL":
            is_testable = True
        elif result == "SKIP":
            is_testable = False
        else:
            # Should not happen given our controlled return type, but handles unforeseen states.
            raise ValueError(f"Unknown test state encountered for code {mock_exit_code}")

        return (result, is_testable)

