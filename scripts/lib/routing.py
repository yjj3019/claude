"""Deterministic FEF route detection using config/routes.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "routes.json"


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _matches(text: str, keywords: list[str]) -> list[str]:
    return [keyword for keyword in keywords if keyword.casefold() in text]


def detect(task: str, config: dict) -> dict:
    text = task.casefold()
    candidates = []
    for index, route in enumerate(config["routes"]):
        matches = _matches(text, route["keywords"])
        if matches:
            candidates.append((len(matches), -index, route, matches))

    if not candidates:
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
            "reasons": []
        }

    _, _, route, matches = max(candidates, key=lambda item: (item[0], item[1]))
    domains = []
    domain_reasons = []
    for domain in config["domains"]:
        found = _matches(text, domain["keywords"])
        if found:
            domains.append(domain["path"])
            domain_reasons.append(f"domain keywords: {', '.join(found)}")

    risk = route["risk_level"]
    high_risk = _matches(text, config.get("high_risk_keywords", []))
    if high_risk:
        risk = "high"

    result = {
        "task_type": route["id"],
        "risk_level": risk,
        "policies": route["policies"],
        "module": route["module"],
        "domains": domains,
        "workflow": route["workflow"],
        "reviewer": route["reviewer"],
        "unmapped": False,
        "kernel_only_safe": False,
        "warnings": [],
        "reasons": [f"task keywords: {', '.join(matches)}", *domain_reasons]
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
        "reviewers": [result["reviewer"]] if result.get("reviewer") else []
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
