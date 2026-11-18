"""Additional Advanced/Expert tests for M5-M7 (hidden traps, ratchet, and reliability edge cases)."""
from __future__ import annotations

import copy
import pytest

from lab9 import gate, stats

pytestmark = pytest.mark.student

ROWS = [
    {"item_id": f"E-{i:03d}", "seed": s, "pass_rate": True, "approval_bypass": False, "slices": ["money_movement"] if i < 2 else ["denial"]}
    for i in range(4)
    for s in (1, 2)
]
SPEC = {
    "eval_set_version": "v2",
    "metrics": [
        {"id": "pass_rate", "kind": "capability", "blocking": True, "threshold": {"min": 0.85, "no_significant_drop": True}},
        {"id": "approval_bypass", "kind": "safety", "blocking": True, "threshold": {"max": 0}},
    ],
    "slices": [
        {"name": "money_movement", "metric": "pass_rate", "min": 0.95, "no_significant_drop": True, "blocking": True}
    ],
}


def _rep(rows, metrics=None, failures=None, seeds=(1, 2)):
    return {
        "manifest": {"eval_set_sha": "abc", "items": 4, "seeds": list(seeds)},
        "rows": rows,
        "metrics": metrics or {"pass_rate": 1.0, "approval_bypass": 0},
        "evaluator_failures": failures or [],
    }


def test_integrity_blocks_duplicate_rows_and_evaluator_failures():
    base = _rep(copy.deepcopy(ROWS))
    assert gate.integrity_check(base, base, SPEC) == []

    # Hidden trap 1: drop failing row and duplicate a passing row to preserve row count
    dup_rows = copy.deepcopy(ROWS)
    dup_rows[-1] = copy.deepcopy(ROWS[0])
    assert gate.integrity_check(_rep(dup_rows), base, SPEC)

    # Hidden trap 2: non-empty evaluator_failures on an otherwise green report
    assert gate.integrity_check(_rep(copy.deepcopy(ROWS), failures=["E-001@1:TrialPass:crash"]), base, SPEC)


def test_integrity_blocks_inf_none_row_and_slice_relabel():
    base = _rep(copy.deepcopy(ROWS))
    assert gate.integrity_check(_rep(copy.deepcopy(ROWS), metrics={"pass_rate": float("inf"), "approval_bypass": 0}), base, SPEC)

    none_row = copy.deepcopy(ROWS)
    none_row[0]["pass_rate"] = None
    assert gate.integrity_check(_rep(none_row), base, SPEC)

    relabel = copy.deepcopy(ROWS)
    relabel[0]["slices"] = []
    assert gate.integrity_check(_rep(relabel), base, SPEC)


def test_integrity_ratchet_blocks_all_loosening_patterns():
    base = _rep(copy.deepcopy(ROWS))

    # Removing a metric, disabling blocking, raising max, dropping no_significant_drop, loosening slice
    rm_metric = copy.deepcopy(SPEC)
    rm_metric["metrics"] = [SPEC["metrics"][0]]
    assert gate.integrity_check(base, base, rm_metric, SPEC)

    non_block = copy.deepcopy(SPEC)
    non_block["metrics"][0]["blocking"] = False
    assert gate.integrity_check(base, base, non_block, SPEC)

    raised_max = copy.deepcopy(SPEC)
    raised_max["metrics"][1]["threshold"]["max"] = 1
    assert gate.integrity_check(base, base, raised_max, SPEC)

    dropped_nsd = copy.deepcopy(SPEC)
    dropped_nsd["metrics"][0]["threshold"].pop("no_significant_drop")
    assert gate.integrity_check(base, base, dropped_nsd, SPEC)

    loose_slice = copy.deepcopy(SPEC)
    loose_slice["slices"][0]["min"] = 0.80
    assert gate.integrity_check(base, base, loose_slice, SPEC)

    # Different eval_set_version allows new thresholds
    v3_spec = copy.deepcopy(loose_slice)
    v3_spec["eval_set_version"] = "v3"
    assert gate.integrity_check(base, base, v3_spec, SPEC) == []


def test_pass_hat_k_rejects_bad_args():
    for args in [(0, 0, 1), (5, -1, 1), (5, 6, 1), (5, 2, 0), (3, 1, 4)]:
        with pytest.raises(ValueError):
            stats.pass_hat_k(*args)
