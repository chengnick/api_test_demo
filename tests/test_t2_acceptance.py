"""T2 acceptance: intentionally failing test.

Verifies the analyze CI job classifies failures end-to-end.
DELETE THIS FILE after T2 acceptance passes.
"""


def test_t2_intentional_failure():
    expected_status = 200
    actual_status = 500  # simulated: server returned unexpected error

    assert actual_status == expected_status, (
        f"getUserSummary returned {actual_status}, expected {expected_status} "
        "(intermittent server-side error, cause unclear)"
    )
