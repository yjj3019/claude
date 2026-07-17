#!/usr/bin/env python3
"""Validate route configuration, loading-map coverage, pack paths, and load limits."""
import re

from lib.routing import ROOT, detect, load_config, validate_selection

LOADING_MAP = ROOT / "docs" / "loading-map.md"


def loading_map_tasks() -> tuple[set[str], set[str]]:
    text = LOADING_MAP.read_text(encoding="utf-8-sig")
    table = text.split("## Task Map", 1)[1].split("\n## ", 1)[0]
    tasks = set()
    manual = set()
    for line in table.splitlines():
        if not line.startswith("|") or "---" in line or "Task Type" in line:
            continue
        task = line.strip("|").split("|", 1)[0].strip()
        if "manual-selection only" in task:
            task = re.sub(r"\s*\(manual-selection only.*\)$", "", task)
            manual.add(task)
        tasks.add(task)
    return tasks, manual


def main() -> int:
    config = load_config()
    errors = []
    ids = set()
    map_tasks, manual_tasks = loading_map_tasks()
    routed_tasks = set()
    for domain in config["domains"]:
        if not (ROOT / domain["path"]).is_file():
            errors.append(f"domain config references missing pack: {domain['path']}")
    for route in config["routes"]:
        if route["id"] in ids:
            errors.append(f"duplicate route id: {route['id']}")
        ids.add(route["id"])
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
        sample = detect(route["keywords"][0], config)
        if sample["task_type"] != route["id"]:
            errors.append(f"route is shadowed or undetectable: {route['id']}")
        errors.extend(f"{route['id']}: {error}" for error in validate_selection({
            "policies": route["policies"],
            "module": route["module"],
            "domains": [],
            "workflow": route["workflow"],
            "reviewer": route["reviewer"]
        }, config, ROOT))

    unmapped_rows = map_tasks - manual_tasks - routed_tasks
    if unmapped_rows:
        errors.append(f"loading-map rows have no route or manual-selection marker: {', '.join(sorted(unmapped_rows))}")

    if errors:
        print("Route validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Route validation passed: {len(config['routes'])} routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
