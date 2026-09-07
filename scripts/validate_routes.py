#!/usr/bin/env python3
"""Validate route configuration, loading-map coverage, pack paths, and load limits."""
import re

from lib.routing import ROOT, detect, load_config, validate_selection

LOADING_MAP = ROOT / "docs" / "loading-map.md"

# Packs a loading-map row states without an "optional" qualifier immediately
# before the backtick are read as mandatory. Domains are excluded: the Domain
# column is free-text guidance, not tied 1:1 to a route (domains are matched
# globally, see config/routes.json "domains").
_PACK_PATH = re.compile(r"(optional\s+)?`((?:policies|modules|workflows|reviewers)/[^`]+\.md)`", re.IGNORECASE)


def parse_loading_map() -> tuple[set[str], set[str], dict[str, str]]:
    text = LOADING_MAP.read_text(encoding="utf-8-sig")
    table = text.split("## Task Map", 1)[1].split("\n## ", 1)[0]
    tasks = set()
    manual = set()
    rows = {}
    for line in table.splitlines():
        if not line.startswith("|") or "---" in line or "Task Type" in line:
            continue
        task = line.strip("|").split("|", 1)[0].strip()
        if "manual-selection only" in task:
            task = re.sub(r"\s*\(manual-selection only.*\)$", "", task)
            manual.add(task)
        tasks.add(task)
        rows[task] = line
    return tasks, manual, rows


def mandatory_paths_in_row(row_text: str) -> set[str]:
    return {path for is_optional, path in _PACK_PATH.findall(row_text) if not is_optional}


def route_mandatory_paths(route: dict) -> set[str]:
    paths = set(route.get("policies", []))
    paths.update(route[key] for key in ("module", "workflow", "reviewer") if route.get(key))
    return paths


def check_row_mandatory_packs(route: dict, row_text: str) -> list[str]:
    """Compare a loading-map row's non-optional pack references against what
    the route actually loads unconditionally, so the two documents cannot
    silently drift the way they have before (see PROGRESS.md)."""
    expected = route_mandatory_paths(route)
    actual = mandatory_paths_in_row(row_text)
    errors = []
    missing = expected - actual
    if missing:
        errors.append(
            f"loading-map row for {route['id']} does not show as mandatory: {', '.join(sorted(missing))} "
            "(route always loads these)"
        )
    extra = actual - expected
    if extra:
        errors.append(
            f"loading-map row for {route['id']} shows as mandatory but the route does not always load: "
            f"{', '.join(sorted(extra))}"
        )
    return errors


def main() -> int:
    config = load_config()
    errors = []
    ids = set()
    priorities = {}
    map_tasks, manual_tasks, map_rows = parse_loading_map()
    routed_tasks = set()
    domain_paths = {domain["path"] for domain in config["domains"]}
    for domain in config["domains"]:
        if not (ROOT / domain["path"]).is_file():
            errors.append(f"domain config references missing pack: {domain['path']}")
        invalid = set(domain.get("subsumes", [])) - domain_paths
        if invalid:
            errors.append(f"{domain['path']} subsumes unknown domains: {', '.join(sorted(invalid))}")
    for route in config["routes"]:
        if route["id"] in ids:
            errors.append(f"duplicate route id: {route['id']}")
        ids.add(route["id"])
        priority = route.get("priority")
        if not isinstance(priority, int):
            errors.append(f"route has no integer priority: {route['id']}")
        elif priority in priorities:
            errors.append(f"duplicate priority {priority}: {priorities[priority]} and {route['id']}")
        else:
            priorities[priority] = route["id"]
        declared_tasks = set(route.get("loading_map_tasks", []))
        if not declared_tasks:
            errors.append(f"route has no loading-map row mapping: {route['id']}")
        missing_rows = declared_tasks - map_tasks
        if missing_rows:
            errors.append(f"{route['id']} references missing loading-map rows: {', '.join(sorted(missing_rows))}")
        duplicate_rows = declared_tasks & routed_tasks
        if duplicate_rows:
            errors.append(f"loading-map rows mapped by multiple routes: {', '.join(sorted(duplicate_rows))}")
        routed_tasks.update(declared_tasks)
        for task in declared_tasks & map_rows.keys():
            errors.extend(check_row_mandatory_packs(route, map_rows[task]))
        # Primary keywords must detect the route. Fallback keywords that require
        # code-context (S4-03) are checked with a synthetic path suffix.
        for keyword in route["keywords"]:
            sample = detect(keyword, config)
            if sample["task_type"] != route["id"]:
                errors.append(
                    f"route is shadowed or undetectable: {route['id']} "
                    f"(keyword {keyword!r} resolved to {sample['task_type']!r})"
                )
        gated = bool(
            route.get("fallback_requires_any") or route.get("fallback_requires_pattern")
        )
        for keyword in route.get("fallback_keywords", []):
            probe = f"{keyword} in main.py" if gated else keyword
            sample = detect(probe, config)
            if sample["task_type"] != route["id"]:
                errors.append(
                    f"route is shadowed or undetectable: {route['id']} "
                    f"(fallback keyword {keyword!r} resolved to {sample['task_type']!r})"
                )
        sample = detect(route["keywords"][0], config)
        errors.extend(
            f"{route['id']}: {error}"
            for error in validate_selection(sample, config, ROOT)
        )

    unmapped_rows = map_tasks - manual_tasks - routed_tasks
    if unmapped_rows:
        errors.append(f"loading-map rows have no route or manual-selection marker: {', '.join(sorted(unmapped_rows))}")

    # S4-06: gate lists must live in config and drive behavior (not Python-only).
    gate = config.get("high_risk_gate") or {}
    for key in ("action_verbs", "trivia_patterns", "question_markers"):
        if not gate.get(key):
            errors.append(f"high_risk_gate.{key} missing or empty in routes.json")
    coding = next((r for r in config["routes"] if r["id"] == "coding"), None)
    if coding is None:
        errors.append("coding route missing")
    else:
        if not coding.get("fallback_requires_any") and not coding.get("fallback_requires_pattern"):
            errors.append("coding route missing fallback_requires_any/pattern (S4-03)")
    signals = config.get("effort_signals") or {}
    for tier in ("L0", "L1", "L2", "L3"):
        if not signals.get(tier):
            errors.append(f"effort_signals.{tier} missing or empty in routes.json")

    # Intent samples: config-driven gates must fire / not fire as designed.
    from lib.routing import high_risk_hits
    hi_sample = "고객사 운영 환경에 패치 배포 절차 알려줘"
    if not high_risk_hits(hi_sample.casefold(), config.get("high_risk_keywords", []), config):
        errors.append(f"S4-04 sample should be high-risk: {hi_sample!r}")
    benign = "production 이라는 단어 뜻이 뭐야?"
    if high_risk_hits(benign.casefold(), config.get("high_risk_keywords", []), config):
        errors.append(f"S3-06/S4-04 benign should not elevate: {benign!r}")
    prose = detect("회의록에 에러 내용 정리해줘", config)
    if prose.get("task_type") == "coding":
        errors.append("S4-03 prose+에러 must not route to coding")
    code_ask = detect("what is causing this error in main.py?", config)
    if code_ask.get("task_type") != "coding":
        errors.append("S4-03 main.py error ask should route to coding")

    if errors:
        print("Route validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Route validation passed: {len(config['routes'])} routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
