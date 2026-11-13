"""Harness regression: rehearsal progress must match the native mixed dataset."""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3]/"services/model-adaptation/scripts/run_fault_acceptance.py"
spec = importlib.util.spec_from_file_location("fault_acceptance", SCRIPT)
faults = importlib.util.module_from_spec(spec)
spec.loader.exec_module(faults)


def test_cancellation_observes_rehearsal_steps_without_counting_evaluation():
    counts = {"train": 102, "replay": 24, "test": 6, "regression": 6}
    # The failed real run logged /756; the former primary-only detector expected /612.
    assert faults.optimizer_progress(" 1%| | 8/756 [00:09<14:00]", counts, 12) == {
        "observed_step": 8, "expected_total_steps": 756, "mixed_rows": 126}
    assert faults.optimizer_progress("0/756 [00:00]", counts, 12) is None
    assert faults.optimizer_progress("8/612 [00:09]", counts, 12) is None
    assert faults.optimizer_progress("757/756 [00:09]", counts, 12) is None
    assert faults.optimizer_progress("Loading weights: 272/272", counts, 12) is None


def test_cancellation_preserves_primary_only_and_partial_batch_detection():
    assert faults.optimizer_progress("1/612", {"train": 102}, 12)["mixed_rows"] == 102
    assert faults.optimizer_progress("1/4", {"train": 2, "replay": 1, "test": 6}, 2)["mixed_rows"] == 3
