"""Deterministic FEF route detection using config/routes.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "routes.json"


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _compact(text: str) -> str:
    """Strip whitespace/separators for spacing-tolerant non-ASCII matching."""
    return re.sub(r"[\s\u00a0\u3000_\-·./]+", "", text.casefold())


def _ascii_sep_flexible(text: str, keyword: str) -> bool:
    """Match multi-token ASCII with flexible space/hyphen/underscore (S4-01).

    `architecture review` ↔ `architecture-review` / `architecture_review`.
    Single-token keywords stay word-boundary only (`incident` ≠ `incidental`).
    """
    kf = keyword.casefold()
    if re.search(rf"(?<![a-z0-9_]){re.escape(kf)}(?![a-z0-9_])", text):
        return True
    tokens = [tok for tok in re.split(r"[\s_\-]+", kf) if tok]
    if len(tokens) < 2:
        return False
    pat = rf"(?<![a-z0-9]){r'[\s_\-]+'.join(re.escape(tok) for tok in tokens)}(?![a-z0-9])"
    return bool(re.search(pat, text))


def _matches(text: str, keywords: list[str]) -> list[str]:
    """Match keywords against casefolded text.

    ASCII: word-boundary aware, plus separator-flexible multi-token match
    (architecture-review ↔ architecture review). Non-ASCII (KO): substring
    match with spacing/separator tolerance (코드수정 ↔ 코드 수정).
    """
    compact_text = _compact(text)
    found: list[str] = []
    for keyword in keywords:
        kf = keyword.casefold()
        if keyword.isascii():
            if _ascii_sep_flexible(text, keyword):
                found.append(keyword)
        else:
            if kf in text or _compact(keyword) in compact_text:
                found.append(keyword)
    return found


def _gate(config: dict) -> dict:
    return config.get("high_risk_gate") or {}


def _is_definition_or_trivia(text: str, config: dict | None = None) -> bool:
    """True for definition / trivia asks that must not elevate to high risk."""
    t = text.casefold()
    patterns = list((_gate(config or {}).get("trivia_patterns") or []))
    for pattern in patterns:
        if pattern.casefold() in t:
            return True
    # "what does X mean" / "X means what"
    if re.search(r"\bwhat\s+does\b.+\bmean\b", t):
        return True
    if re.search(r"\b(mean|meaning|definition)\b", t) and (
        "?" in text or t.startswith("what") or "뭐" in t
    ):
        return True
    return False


def _has_action_verb(text: str, config: dict | None = None) -> bool:
    verbs = list((_gate(config or {}).get("action_verbs") or []))
    return bool(_matches(text, verbs))


def _is_question_form(text: str, config: dict | None = None) -> bool:
    stripped = text.strip()
    if stripped.endswith("?"):
        return True
    t = stripped.casefold()
    markers = list(
        (_gate(config or {}).get("question_markers") or ())
    )
    return any(marker in t for marker in markers)


def high_risk_hits(
    text: str,
    keywords: list[str],
    config: dict | None = None,
) -> list[str]:
    """Return high-risk keyword hits that also pass the S3-06/S4-04 gate.

    Order (S4-04):
      1) keyword hits 없으면 []
      2) action_verb 있으면 → hits 유지 (trivia 무시)
      3) else if definition/trivia(결합형) → []
      4) else if non-question → hits
      5) else []
    Trivia suppress only when: no action verb ∧ question/definition form.
    Gate lists load from config/routes.json high_risk_gate (S4-06).
    """
    hits = _matches(text, keywords)
    if not hits:
        return []
    if _has_action_verb(text, config):
        return hits
    if _is_definition_or_trivia(text, config):
        return []
    if not _is_question_form(text, config):
        return hits
    return []


def _fallback_context_ok(text: str, route: dict) -> bool:
    """S4-03: weak fallback fires only with code-context tokens or path regex."""
    requires_any = list(route.get("fallback_requires_any") or [])
    requires_pattern = list(route.get("fallback_requires_pattern") or [])
    if not requires_any and not requires_pattern:
        return True
    if requires_any and _matches(text, requires_any):
        return True
    # Also allow simple substring for non-ascii / spaced tokens in requires_any
    t = text.casefold()
    for token in requires_any:
        if token.casefold() in t:
            return True
    for pattern in requires_pattern:
        try:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return True
        except re.error:
            continue
    return False


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
            "also_matched": [],
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
        "also_matched": [],
        "warnings": ["Exact task route was not found."],
        "reasons": [],
    }


def detect(task: str, config: dict) -> dict:
    text = task.casefold()
    # R2-P0-UNMAPPED-HIGHRISK + S3-06/S4-04: evaluate gated high-risk before unmapped.
    high_risk = high_risk_hits(
        text, config.get("high_risk_keywords", []), config=config
    )

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
            # S4-03: coding (and any gated) fallback needs code-context allowlist.
            if not _fallback_context_ok(text, route):
                continue
            fallback_candidates.append(item)
        candidates = fallback_candidates

    if not candidates:
        return _unmapped_result(
            risk_level="high" if high_risk else "low",
            high_risk=high_risk,
        )

    ranked = sorted(candidates, key=lambda item: (item[0], item[1]))
    _, _, route, matches = ranked[-1]
    # S3-05: expose other matched routes (single total-order selection unchanged).
    also_matched = [
        {
            "id": other["id"],
            "risk_level": other.get("risk_level", "low"),
            "matches": other_matches,
        }
        for _, _, other, other_matches in ranked[:-1]
        if other["id"] != route["id"]
    ]

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
    if len(selected_domains) > domain_limit:
        def _rank_key(item: tuple) -> tuple:
            domain, found = item
            offsets = [text.find(f.casefold()) for f in found]
            offsets = [o for o in offsets if o >= 0]
            first = min(offsets) if offsets else 10**9
            return (-len(found), first, domain["path"])

        ranked_domains = sorted(selected_domains, key=_rank_key)
        kept = ranked_domains[:domain_limit]
        dropped = ranked_domains[domain_limit:]
        drop_names = ", ".join(domain["path"] for domain, _ in dropped)
        warnings.append(
            f"Domain overflow: kept top {domain_limit} by keyword-match rank; "
            f"dropped: {drop_names}. Narrow the task if a dropped domain is required."
        )
        selected_domains = kept

    # S3-05: if a silently dropped multi-intent route is high-risk, warn.
    for dropped in also_matched:
        if dropped.get("risk_level") == "high":
            warnings.append(
                f"Multi-intent: also matched high-risk route "
                f"{dropped['id']} (keywords: {', '.join(dropped['matches'])}); "
                f"selected {route['id']} only — narrow the task if the dropped "
                f"route is required."
            )

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
        "also_matched": also_matched,
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
