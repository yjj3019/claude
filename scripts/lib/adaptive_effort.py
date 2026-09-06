"""Adaptive Effort / Complexity Router helpers (L0–L3).

Classifies request complexity from the user ask (object + risk), not from
available files. Escalate model before expanding packs. L0 stays Kernel-only;
L2–L3 obey loading-map Load Limits.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

LOAD_LIMITS = {
    "modules": 1,
    "domains": 2,
    "workflows": 1,
    "reviewers": 1,
    "policies": 3,
}

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


TIERS: dict[str, EffortTier] = {
    "L0": EffortTier(
        id="L0",
        model="Haiku 4.5",
        max_modules=0,
        max_domains=0,
        max_workflows=0,
        max_reviewers=0,
        max_policies=0,
        kernel_only=True,
        allow_preload_model_docs=False,
    ),
    "L1": EffortTier(
        id="L1",
        model="Sonnet 5",
        max_modules=1,
        max_domains=0,
        max_workflows=0,
        max_reviewers=0,
        max_policies=0,
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
_L3_SIGNALS = (
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
)
_L2_SIGNALS = (
    "multi-file",
    "multi file",
    "multi-step",
    "multi step",
    "architecture",
    "careful review",
    "code review",
    "proposal",
    "rca",
    "incident",
    "refactor",
)
_L1_SIGNALS = (
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
)
_L0_SIGNALS = (
    "what is",
    "define",
    "definition",
    "yes or no",
    "yes/no",
    "lookup",
    "quick",
)


def classify_tier(ask: str) -> str:
    """Classify from user ask text only (object + risk signals)."""
    text = ask.casefold()
    for signal in _L3_SIGNALS:
        if signal in text:
            return "L3"
    for signal in _L2_SIGNALS:
        if signal in text:
            return "L2"
    for signal in _L1_SIGNALS:
        if signal in text:
            return "L1"
    for signal in _L0_SIGNALS:
        if signal in text:
            return "L0"
    # Default: routine if looks like a short fact question, else L1-safe.
    words = text.split()
    if len(words) <= 8 and ("?" in ask or text.startswith(("who ", "when ", "where ", "which "))):
        return "L0"
    return "L1"


def tier_for(ask: str) -> EffortTier:
    return TIERS[classify_tier(ask)]


def validate_pack_load(
    tier_id: str,
    *,
    modules: int = 0,
    domains: int = 0,
    workflows: int = 0,
    reviewers: int = 0,
    policies: int = 0,
    preloaded: Iterable[str] = (),
) -> list[str]:
    """Return error strings if the proposed load violates Adaptive Effort + Load Limits."""
    tier = TIERS[tier_id]
    errors: list[str] = []
    counts = {
        "modules": modules,
        "domains": domains,
        "workflows": workflows,
        "reviewers": reviewers,
        "policies": policies,
    }
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
    # Global Load Limits floor for L2/L3 (and never exceed map caps).
    for key, limit in LOAD_LIMITS.items():
        if counts[key] > limit:
            errors.append(f"{tier_id} exceeds Load Limits {key}≤{limit} (got {counts[key]})")
    if tier.kernel_only and sum(counts.values()) > 0:
        errors.append(f"{tier_id} forbids multi-pack load (Kernel only)")
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
