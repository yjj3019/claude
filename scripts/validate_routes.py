#!/usr/bin/env python3
"""Validate route configuration, pack paths, and load limits."""
from lib.routing import ROOT, detect, load_config, validate_selection


def main() -> int:
    config = load_config()
    errors = []
    ids = set()
    for domain in config["domains"]:
        if not (ROOT / domain["path"]).is_file():
            errors.append(f"domain config references missing pack: {domain['path']}")
    for route in config["routes"]:
        if route["id"] in ids:
            errors.append(f"duplicate route id: {route['id']}")
        ids.add(route["id"])
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

    if errors:
        print("Route validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Route validation passed: {len(config['routes'])} routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
