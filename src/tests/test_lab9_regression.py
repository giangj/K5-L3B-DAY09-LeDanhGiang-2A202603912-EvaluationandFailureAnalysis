"""M3 trace-case regression tests (C-002@11 FM-03, FM-08 ReplyMatchesLedger, FM-05 NoPreDeduct)."""
from __future__ import annotations

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9 import graders, variants
from lab9.trace_case import investigate
from lab9.variant_agent import make_shape

pytestmark = pytest.mark.student


def _ctx(trial: dict, label: dict | None = None) -> EvaluatorContext:
    return EvaluatorContext(
        name="regression",
        inputs={},
        metadata=None,
        expected_output=label or {},
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_trace_case_c002_seed11_db_override_fails_regression_and_passes_fixed():
    """Trace case C-002@11 (FM-03): seeded_regression overrides delay_days=2->5 at step 3; fixed stays at 2."""
    bad = investigate("seeded_regression", "C-002", 11)
    good = investigate("fixed", "C-002", 11)

    bad_ctx = _ctx(bad["trial"], bad["label"])
    good_ctx = _ctx(good["trial"], good["label"])

    assert bad["trial"]["lab8_pass"] is False
    assert graders.DbFactKept().evaluate(bad_ctx).value is False
    assert graders.RefundAmountCorrect().evaluate(bad_ctx).value is False

    assert good["trial"]["lab8_pass"] is True
    assert graders.DbFactKept().evaluate(good_ctx).value is True
    assert graders.RefundAmountCorrect().evaluate(good_ctx).value is True


def test_reply_matches_ledger_catches_fm08_and_ignores_benign_numbers():
    """FM-08: reply stating proposal instead of ledger amount fails; order IDs and day counts are ignored."""
    base_label = {"refund_vnd": 20000, "approval_ok": True, "forbid_substrings": []}

    ok_trial = {
        "snapshot": {"refund_vnd": 20000, "refund_count": 1, "policy_denied": False},
        "unexpected_rows": 0,
        "blob": "",
        "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 20.000đ cho đơn O-808. Tiền về trong 3–5 ngày ạ."}}],
        "result": {"status": "resolved"},
        "lab8_pass": True,
        "lab8_reason": None,
    }
    bad_trial = {
        **ok_trial,
        "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808."}}],
    }
    no_reply_trial = {**ok_trial, "events": []}

    assert graders.ReplyMatchesLedger().evaluate(_ctx(ok_trial, base_label)).value is True
    assert graders.ReplyMatchesLedger().evaluate(_ctx(bad_trial, base_label)).value is False
    assert graders.ReplyMatchesLedger().evaluate(_ctx(no_reply_trial, base_label)).value is True

    from lab8.shapes import SHAPES

    variants.register()
    SHAPES.setdefault("_test_misreport", make_shape("_test_misreport", {"no_override", "misreport"}))
    bad_case = investigate("_test_misreport", "C-008", 11)
    good_case = investigate("fixed", "C-008", 11)
    assert graders.ReplyMatchesLedger().evaluate(_ctx(bad_case["trial"], bad_case["label"])).value is False
    assert graders.ReplyMatchesLedger().evaluate(_ctx(good_case["trial"], good_case["label"])).value is True


def test_no_pre_deduct_catches_fm05_on_c013_and_c014():
    """FM-05: seeded_regression pre-deducts prior refund on C-013 & C-014; fixed and honest_refactor pass."""
    for cid in ("C-013", "C-014"):
        bad = investigate("seeded_regression", cid, 11)
        good = investigate("fixed", cid, 11)
        honest = investigate("honest_refactor", cid, 11)
        assert graders.NoPreDeduct().evaluate(_ctx(bad["trial"], bad["label"])).value is False
        assert graders.NoPreDeduct().evaluate(_ctx(good["trial"], good["label"])).value is True
        assert graders.NoPreDeduct().evaluate(_ctx(honest["trial"], honest["label"])).value is True
