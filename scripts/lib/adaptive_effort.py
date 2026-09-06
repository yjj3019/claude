"""Adaptive Effort / Complexity Router helpers (L0–L3).

L0–L3 primarily select MODEL. Pack selection follows docs/loading-map.md /
kernel_only_safe when a mapped route needs Integrity policies or workflows.
Escalate model before packs. Default when unsure is Sonnet (L1). Haiku (L0)
is a narrow gate for light Notion/doc recording only.
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
# Softened: no bare "refactor" / bare "architecture" / bare "rca" (overfire).
_L2_SIGNALS = (
    "multi-file",
    "multi file",
    "multi-step",
    "multi step",
    "architecture review",
    "architecture lite",
    "careful review",
    "code review",
    "proposal",
    "incident",
    "multi-file refactor",
    "multi file refactor",
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
    "q&a",
    "question",
    "refactor",  # mild refactor stays Sonnet (L1); large/multi-file escalate above
)
# Narrow Haiku gate: light Notion / document recording only (EN + KO).
_L0_SIGNALS = (
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
    # Korean Notion / light-doc synonyms
    "노션",
    "메모 추가",
    "메모해",
    "체크리스트",
)


def classify_tier(ask: str) -> str:
    """Classify from user ask text only (object + risk signals).

    When unsure, return L1 (Sonnet). Haiku (L0) only for clear light
    Notion/doc recording — not general quick facts.
    """
    text = ask.casefold()
    for signal in _L3_SIGNALS:
        if signal in text:
            return "L3"
    for signal in _L2_SIGNALS:
        if signal in text:
            return "L2"
    # L0 before L1 so Notion/doc phrases win over generic edit/summary
    # only when the ask clearly matches the narrow Haiku gate.
    for signal in _L0_SIGNALS:
        if signal in text:
            return "L0"
    for signal in _L1_SIGNALS:
        if signal in text:
            return "L1"
    # Default when unsure: Sonnet (L1), never Haiku for general quick facts.
    return "L1"


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
