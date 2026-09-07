"""Adaptive Effort / Complexity Router helpers (L0–L3).

L0–L3 primarily select MODEL. Pack selection follows docs/loading-map.md /
kernel_only_safe when a mapped route needs Integrity policies or workflows.
Escalate model before packs. Default when unsure is Sonnet (L1). Haiku (L0)
is a narrow gate for light Notion/doc recording only.

Risk coupling (sim round-2 / meta-review):
- High risk ⇒ ban L0 (Haiku); floor at L1 (Sonnet) minimum.
- Do NOT blanket-floor all high-risk asks to L2/Opus.
- Raise to L2+ only when L2/L3 text signals (or clear multi-step/high-stakes
  phrases) are also present — classify_tier already encodes those signals.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

LOAD_LIMITS = {
    "modules": 1,
    "domains": 2,
    "workflows": 1,
    "reviewers": 1,
    "policies": 3,
}

# L0 may load at most one Notion/doc-ish module section (not Coding/RCA/etc.).
L0_MODULE_ALLOWLIST = frozenset(
    {
        "modules/Meeting.md",
    }
)

# Integrity Policies must never be stripped from mapped L1 coding (or similar)
# just to obey a stale Adaptive pack cap.
INTEGRITY_POLICY_SUFFIXES = (
    "Evidence.md",
    "FileHandling.md",
    "Freshness.md",
    "ToolExecution.md",
)

FORBIDDEN_PRELOAD_L0_L1 = (
    "docs/model-usage.md",
    "docs/adaptive-effort.md",
    "README.md",
    "CHANGELOG.md",
    "PROGRESS.md",
    "SESSION_LOG.md",
)


@dataclass(frozen=True)
class EffortTier:
    id: str
    model: str
    max_modules: int
    max_domains: int
    max_workflows: int
    max_reviewers: int
    max_policies: int
    kernel_only: bool
    allow_preload_model_docs: bool


# Pack caps for L1–L3 match loading-map Load Limits. L0 stays Notion/doc-tight.
# Model assignment is the primary L0–L3 job; packs come from the map when mapped.
TIERS: dict[str, EffortTier] = {
    "L0": EffortTier(
        id="L0",
        model="Haiku 4.5",
        max_modules=1,
        max_domains=0,
        max_workflows=0,
        max_reviewers=0,
        max_policies=0,
        kernel_only=False,
        allow_preload_model_docs=False,
    ),
    "L1": EffortTier(
        id="L1",
        model="Sonnet 5",
        max_modules=LOAD_LIMITS["modules"],
        max_domains=LOAD_LIMITS["domains"],
        max_workflows=LOAD_LIMITS["workflows"],
        max_reviewers=LOAD_LIMITS["reviewers"],
        max_policies=LOAD_LIMITS["policies"],
        kernel_only=False,
        allow_preload_model_docs=False,
    ),
    "L2": EffortTier(
        id="L2",
        model="Opus 5 (1M)",
        max_modules=LOAD_LIMITS["modules"],
        max_domains=LOAD_LIMITS["domains"],
        max_workflows=LOAD_LIMITS["workflows"],
        max_reviewers=LOAD_LIMITS["reviewers"],
        max_policies=LOAD_LIMITS["policies"],
        kernel_only=False,
        allow_preload_model_docs=True,
    ),
    "L3": EffortTier(
        id="L3",
        model="Fable 5.1",
        max_modules=LOAD_LIMITS["modules"],
        max_domains=LOAD_LIMITS["domains"],
        max_workflows=LOAD_LIMITS["workflows"],
        max_reviewers=LOAD_LIMITS["reviewers"],
        max_policies=LOAD_LIMITS["policies"],
        kernel_only=False,
        allow_preload_model_docs=True,
    ),
}

# Signal keywords (casefold). Order matters: highest tier wins.
# Authority: config/routes.json "effort_signals" (S4-05 / S4-06). Hardcoded
# defaults below are fallbacks if the JSON key is missing.
_DEFAULT_L3_SIGNALS = (
    "deep rca",
    "root cause",
    "large refactor",
    "multi-hour",
    "multi hour",
    "long-running",
    "long running",
    "high-stakes",
    "high stakes",
    "security audit",
    "architecture overhaul",
    "근본 원인",
    "대규모 리팩터",
    "대규모 리팩토링",
    "보안 감사",
    "장기 작업",
    "장시간 작업",
    "심층 원인",
    "고위험",
)
_DEFAULT_L2_SIGNALS = (
    "multi-file",
    "multi file",
    "multi-step",
    "multi step",
    "architecture review",
    "architecture lite",
    "careful review",
    "code review",
    "multi-file refactor",
    "multi file refactor",
    "incident response",
    "incident review",
    "incident analysis",
    "원인 분석",
    "장애 원인",
    "장애 대응",
    "장애 분석",
    "제안서 작성",
    "제안서 검토",
    "제안서 일관성",
    "다중 파일",
    "멀티 파일",
    "다단계",
    "멀티 스텝",
    "아키텍처 검토",
    "아키텍처 리뷰",
    "신중한 검토",
    "코드 리뷰",
)
_DEFAULT_L1_SIGNALS = (
    "edit",
    "fix",
    "patch",
    "summary",
    "summarize",
    "one-file",
    "one file",
    "implement",
    "coding",
    "code",
    "q&a",
    "question",
    "refactor",
    "수정",
    "편집",
    "패치",
    "요약",
    "구현",
    "코딩",
    "코드",
    "질문",
    "리팩터",
    "리팩토링",
)
_DEFAULT_L0_SIGNALS = (
    "notion note",
    "notion notes",
    "notion row",
    "notion rows",
    "notion page",
    "notion record",
    "notion filing",
    "short doc",
    "short document",
    "doc capture",
    "document capture",
    "trivial filing",
    "simple filing",
    "checklist tick",
    "checklist ticks",
    "tick checklist",
    "file a note",
    "log a note",
    "append a row",
    "add a notion",
    "meeting notes",
    "meeting note",
    "checklist for",
    "simple checklist",
    "노션",
    "메모 추가",
    "메모해",
    "체크리스트",
)

_L3_SIGNALS = _DEFAULT_L3_SIGNALS
_L2_SIGNALS = _DEFAULT_L2_SIGNALS
_L1_SIGNALS = _DEFAULT_L1_SIGNALS
_L0_SIGNALS = _DEFAULT_L0_SIGNALS


def load_effort_signals(config: dict | None = None) -> None:
    """Load L0–L3 signal lists from routes.json effort_signals (S4-06)."""
    global _L3_SIGNALS, _L2_SIGNALS, _L1_SIGNALS, _L0_SIGNALS
    if config is None:
        try:
            from lib.routing import load_config as _load
            config = _load()
        except Exception:
            try:
                import json
                from pathlib import Path as _Path
                cfg_path = _Path(__file__).resolve().parents[2] / "config" / "routes.json"
                config = json.loads(cfg_path.read_text(encoding="utf-8"))
            except Exception:
                return
    signals = (config or {}).get("effort_signals") or {}
    if signals.get("L3"):
        _L3_SIGNALS = tuple(signals["L3"])
    if signals.get("L2"):
        _L2_SIGNALS = tuple(signals["L2"])
    if signals.get("L1"):
        _L1_SIGNALS = tuple(signals["L1"])
    if signals.get("L0"):
        _L0_SIGNALS = tuple(signals["L0"])


# Load from config at import when available.
try:
    load_effort_signals()
except Exception:
    pass



def _compact(text: str) -> str:
    """Remove whitespace/common separators for spacing-tolerant KO/EN matching."""
    return re.sub(r"[\s\u00a0\u3000_\-·./]+", "", text.casefold())


def _signal_in(text: str, signal: str) -> bool:
    """True if signal appears in text, allowing flexible spacing/separators.

    ASCII signals use word boundaries so `incident` ≠ `incidental` (S4-05).
    Non-ASCII (KO) keeps compact substring matching.
    """
    s = signal.casefold()
    t = text.casefold()
    if signal.isascii() or s.isascii():
        if re.search(rf"(?<![a-z0-9_]){re.escape(s)}(?![a-z0-9_])", t):
            return True
        return False
    if s in t:
        return True
    return _compact(s) in _compact(t)


def classify_tier(ask: str) -> str:
    """Classify from user ask text only (object + risk signals).

    When unsure, return L1 (Sonnet). Haiku (L0) only for clear light
    Notion/doc recording — not general quick facts.
    """
    text = ask.casefold()
    for signal in _L3_SIGNALS:
        if _signal_in(text, signal):
            return "L3"
    for signal in _L2_SIGNALS:
        if _signal_in(text, signal):
            return "L2"
    # L0 before L1 so Notion/doc phrases win over generic edit/summary
    # only when the ask clearly matches the narrow Haiku gate.
    for signal in _L0_SIGNALS:
        if _signal_in(text, signal):
            return "L0"
    for signal in _L1_SIGNALS:
        if _signal_in(text, signal):
            return "L1"
    # Default when unsure: Sonnet (L1), never Haiku for general quick facts.
    return "L1"


def _has_l2_or_l3_signals(ask: str) -> bool:
    text = ask.casefold()
    for signal in _L3_SIGNALS:
        if _signal_in(text, signal):
            return True
    for signal in _L2_SIGNALS:
        if _signal_in(text, signal):
            return True
    return False


def _selection_is_substantial(selection: dict | None) -> bool:
    """True when route load is beyond Notion/light-doc (R2-P2-L0-LEAK)."""
    if not selection:
        return False
    module = selection.get("module")
    if module and module not in L0_MODULE_ALLOWLIST:
        return True
    if selection.get("workflow") or selection.get("reviewer"):
        return True
    if selection.get("domains"):
        return True
    policies = selection.get("policies") or []
    if policies:
        return True
    if selection.get("kernel_only_safe") is False and (
        module or policies or selection.get("workflow")
    ):
        return True
    return False


def effective_tier(
    ask: str,
    *,
    risk_level: str = "low",
    selection: dict | None = None,
) -> tuple[str, str | None]:
    """Return (tier_id, reason) after risk floor + L0-leak guards.

    High risk bans L0/Haiku (floor L1/Sonnet). Does **not** blanket-raise
    high-risk to L2/Opus — L2+ only when L2/L3 text signals already classify
    there (or equivalent multi-step/high-stakes phrases in the signal lists).
    """
    raw = classify_tier(ask)
    tier = raw
    reason: str | None = None

    # R2-P2-L0-LEAK: Notion/light filing only; substantial packs or high-risk → ≥L1
    if tier == "L0":
        if risk_level == "high":
            tier = "L1"
            reason = "high-risk floor: ban L0/Haiku → L1/Sonnet"
        elif _selection_is_substantial(selection):
            tier = "L1"
            reason = "L0 leak: substantial Manual/coding/security packs → L1"

    # R2-P1-RISK-TIER-DECOUPLED: high risk ⇒ ban L0 only (already handled);
    # if somehow still L0, floor again. Never blanket to L2.
    if risk_level == "high" and tier == "L0":
        tier = "L1"
        reason = "high-risk floor: ban L0/Haiku → L1/Sonnet"

    # Documented path: L2+ only via text signals (already in raw). If high-risk
    # ask also carries L2/L3 signals, raw is already L2/L3 — no extra bump.
    if risk_level == "high" and tier == "L1" and _has_l2_or_l3_signals(ask):
        # classify_tier should have returned L2/L3; if L1 won (e.g. L0 path
        # then floored), re-classify ignoring L0 for the raise decision.
        bumped = classify_tier(ask)
        if bumped in ("L2", "L3"):
            tier = bumped
            reason = (
                f"high-risk + {bumped} text signals → {bumped} "
                "(not a blanket high-risk→L2 floor)"
            )

    return tier, reason


def tier_for(ask: str) -> EffortTier:
    return TIERS[classify_tier(ask)]


def is_integrity_policy(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return name in INTEGRITY_POLICY_SUFFIXES


def missing_integrity_policies(
    policy_paths: Iterable[str], required: Iterable[str]
) -> list[str]:
    """Return errors when trigger-required Integrity policies were stripped."""
    present = set(policy_paths)
    return [
        f"missing required Integrity policy: {path}"
        for path in required
        if path not in present
    ]


def validate_pack_load(
    tier_id: str,
    *,
    modules: int = 0,
    domains: int = 0,
    workflows: int = 0,
    reviewers: int = 0,
    policies: int = 0,
    preloaded: Iterable[str] = (),
    kernel_only_safe: bool | None = None,
    module_paths: Iterable[str] = (),
    policy_paths: Iterable[str] = (),
) -> list[str]:
    """Return error strings if the proposed load violates Adaptive Effort + Load Limits.

    L0–L3 select model; when kernel_only_safe is False (mapped route), pack
    caps are loading-map Load Limits. L0 stays Notion/doc-tight with an
    allowlist. Never strip Integrity Policies required by mapped coding.
    """
    tier = TIERS[tier_id]
    errors: list[str] = []
    counts = {
        "modules": modules,
        "domains": domains,
        "workflows": workflows,
        "reviewers": reviewers,
        "policies": policies,
    }
    # When a mapped route is in play, L1 uses map caps (already on the tier).
    # When kernel_only_safe, any multi-pack load is wrong for L0/L1.
    if kernel_only_safe is True and tier_id in ("L0", "L1"):
        if sum(counts.values()) > 0:
            errors.append(
                f"{tier_id} with kernel_only_safe must stay Kernel-only "
                f"(got packs {counts})"
            )
    caps = {
        "modules": tier.max_modules,
        "domains": tier.max_domains,
        "workflows": tier.max_workflows,
        "reviewers": tier.max_reviewers,
        "policies": tier.max_policies,
    }
    for key, value in counts.items():
        if value > caps[key]:
            errors.append(f"{tier_id} exceeds {key} cap {caps[key]} (got {value})")
    # Global Load Limits floor (never exceed map caps).
    for key, limit in LOAD_LIMITS.items():
        if counts[key] > limit:
            errors.append(
                f"{tier_id} exceeds Load Limits {key}≤{limit} (got {counts[key]})"
            )
    if tier.kernel_only and sum(counts.values()) > 0:
        errors.append(f"{tier_id} forbids multi-pack load (Kernel only)")
    # L0: Kernel only or Kernel + ≤1 allowlisted Notion/doc section.
    if tier_id == "L0":
        if domains or workflows or reviewers or policies:
            errors.append(
                "L0 allows Kernel only or Kernel + 1 Notion/doc section "
                "(no domains/workflows/reviewers/policies)"
            )
        if modules > 1:
            errors.append("L0 exceeds Notion/doc section cap 1 (got %s)" % modules)
        paths = [p for p in module_paths if p]
        if paths:
            for path in paths:
                if path not in L0_MODULE_ALLOWLIST:
                    errors.append(
                        f"L0 module not allowlisted for Notion/doc gate: {path}"
                    )
    if not tier.allow_preload_model_docs:
        for path in preloaded:
            if path in FORBIDDEN_PRELOAD_L0_L1:
                errors.append(f"{tier_id} must not preload {path}")
    return errors


def escalate_model(tier_id: str) -> str | None:
    order = ["L0", "L1", "L2", "L3"]
    idx = order.index(tier_id)
    if idx >= len(order) - 1:
        return None
    return order[idx + 1]


def counts_from_selection(selection: dict) -> dict[str, int]:
    """Pack counts from a detect()/selected_packs-style selection dict."""
    return {
        "modules": 1 if selection.get("module") else 0,
        "domains": len(selection.get("domains") or []),
        "workflows": 1 if selection.get("workflow") else 0,
        "reviewers": 1 if selection.get("reviewer") else 0,
        "policies": len(selection.get("policies") or []),
    }
