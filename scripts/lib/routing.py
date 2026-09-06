"""Deterministic FEF route detection using config/routes.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "routes.json"

# R2-P1-FALLBACK-OVERFIRE: weak coding fallbacks must not pull the Coding full
# pack for prose/Q&A/typo-fix asks. Primary keywords still match normally.
_CODING_FALLBACK_BLOCKERS = (
    "what is",
    "what are",
    "what's",
    "concept",
    "개념",
    "오탈자",
    "typo",
    "typos",
    "proofread",
    "맞춤법",
    "spelling",
    "grammar",
    "error budget",
    "문서의 오탈",
    "오탈자 수정",
)


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _compact(text: str) -> str:
    """Strip whitespace/separators for spacing-tolerant non-ASCII matching."""
    return re.sub(r"[\s\u00a0\u3000_\-·./]+", "", text.casefold())


def _matches(text: str, keywords: list[str]) -> list[str]:
    """Match keywords against casefolded text.

    ASCII: word-boundary aware. Non-ASCII (KO): substring match with
    spacing/separator tolerance (코드수정 ↔ 코드 수정).
    """
    compact_text = _compact(text)
    found: list[str] = []
    for keyword in keywords:
        kf = keyword.casefold()
        if keyword.isascii():
            if re.search(
                rf"(?<![a-z0-9_]){re.escape(kf)}(?![a-z0-9_])",
                text,
            ):
                found.append(keyword)
        else:
            if kf in text or _compact(keyword) in compact_text:
                found.append(keyword)
    return found


def _coding_fallback_blocked(text: str) -> bool:
    """True when coding fallback keywords should not fire (Q&A / typo prose)."""
    return any(blocker in text for blocker in _CODING_FALLBACK_BLOCKERS)


def _unmapped_result(
    *,
    risk_level: str,
    high_risk: list[str],
) -> dict:
    """Kernel-light for low-risk unmapped; minimal safety for high-risk unmapped.

    R2-P0-UNMAPPED-HIGHRISK: never return the lightest Kernel-only config for
    high-risk asks — attach Evidence + warning, kernel_only_safe=False.
    """
    if high_risk or risk_level == "high":
        reasons = []
        if high_risk:
            reasons.append(f"high-risk keywords: {', '.join(high_risk)}")
        return {
            "task_type": "unknown",
            "risk_level": "high",
            "policies": ["policies/Evidence.md"],
            "module": None,
            "domains": [],
            "workflow": None,
            "reviewer": None,
            "unmapped": True,
            "kernel_only_safe": False,
            "warnings": [
                "Exact task route was not found.",
                "High-risk unmapped ask: attached minimal safety "
                "(policies/Evidence.md); do not use Kernel-only light config.",
            ],
            "reasons": reasons,
        }
    return {
        "task_type": "unknown",
        "risk_level": "low",
        "policies": [],
        "module": None,
        "domains": [],
        "workflow": None,
        "reviewer": None,
        "unmapped": True,
        "kernel_only_safe": True,
        "warnings": ["Exact task route was not found."],
        "reasons": [],
    }


def detect(task: str, config: dict) -> dict:
    text = task.casefold()
    # R2-P0-UNMAPPED-HIGHRISK: evaluate high-risk BEFORE early unmapped return.
    high_risk = _matches(text, config.get("high_risk_keywords", []))

    def candidates_for(key: str) -> list[tuple]:
        candidates = []
        for route in config["routes"]:
            matches = _matches(text, route.get(key, []))
            if matches:
                candidates.append((len(matches), -route["priority"], route, matches))
        return candidates

    candidates = candidates_for("keywords")
    if not candidates:
        fallback_candidates = []
        for item in candidates_for("fallback_keywords"):
            route = item[2]
            # R2-P1-FALLBACK-OVERFIRE: gate weak coding fallbacks.
            if route.get("id") == "coding" and _coding_fallback_blocked(text):
                continue
            fallback_candidates.append(item)
        candidates = fallback_candidates

    if not candidates:
        return _unmapped_result(
            risk_level="high" if high_risk else "low",
            high_risk=high_risk,
        )

    _, _, route, matches = max(candidates, key=lambda item: (item[0], item[1]))
    matched_domains = []
    for domain in config["domains"]:
        found = _matches(text, domain["keywords"])
        if found:
            matched_domains.append((domain, found))
    subsumed = {
        path
        for domain, _ in matched_domains
        for path in domain.get("subsumes", [])
    }
    selected_domains = [
        (domain, found)
        for domain, found in matched_domains
        if domain["path"] not in subsumed
    ]

    warnings: list[str] = []
    domain_limit = config.get("limits", {}).get("domains", 2)
    # R2-P1-DOMAIN-OVERFLOW: rank-based top-N with explicit warning (no silent trim).
    # Rank: more keyword hits first, then earlier mention in the ask (never hide drops).
    if len(selected_domains) > domain_limit:
        def _rank_key(item: tuple) -> tuple:
            domain, found = item
            offsets = [text.find(f.casefold()) for f in found]
            offsets = [o for o in offsets if o >= 0]
            first = min(offsets) if offsets else 10**9
            return (-len(found), first, domain["path"])

        ranked = sorted(selected_domains, key=_rank_key)
        kept = ranked[:domain_limit]
        dropped = ranked[domain_limit:]
        drop_names = ", ".join(domain["path"] for domain, _ in dropped)
        warnings.append(
            f"Domain overflow: kept top {domain_limit} by keyword-match rank; "
            f"dropped: {drop_names}. Narrow the task if a dropped domain is required."
        )
        selected_domains = kept

    domains = [domain["path"] for domain, _ in selected_domains]
    domain_reasons = [
        f"domain keywords: {', '.join(found)}"
        for _, found in selected_domains
    ]

    risk = route["risk_level"]
    if high_risk:
        risk = "high"

    result = {
        "task_type": route["id"],
        "risk_level": risk,
        "policies": list(route["policies"]),
        "module": route["module"],
        "domains": domains,
        "workflow": route["workflow"],
        "reviewer": route["reviewer"],
        "unmapped": False,
        "kernel_only_safe": False,
        "warnings": warnings,
        "reasons": [f"task keywords: {', '.join(matches)}", *domain_reasons],
    }
    if high_risk:
        result["reasons"].append(f"high-risk keywords: {', '.join(high_risk)}")
    return result


def selected_packs(result: dict) -> dict[str, list[str]]:
    return {
        "policies": result.get("policies", []),
        "modules": [result["module"]] if result.get("module") else [],
        "domains": result.get("domains", []),
        "workflows": [result["workflow"]] if result.get("workflow") else [],
        "reviewers": [result["reviewer"]] if result.get("reviewer") else [],
    }


def validate_selection(result: dict, config: dict, root: Path = ROOT) -> list[str]:
    errors = []
    for category, paths in selected_packs(result).items():
        limit = config["limits"][category]
        if len(paths) > limit:
            errors.append(f"{category} pack count exceeds limit: {len(paths)} > {limit}")
        for rel in paths:
            if not (root / rel).is_file():
                errors.append(f"selected pack does not exist: {rel}")
    return errors
