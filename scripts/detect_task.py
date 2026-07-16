#!/usr/bin/env python3
"""Detect a candidate FEF task route."""
import argparse
import json

from lib.routing import detect, load_config, validate_selection


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Task description in Korean or English")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()

    config = load_config()
    result = detect(args.task, config)
    errors = validate_selection(result, config)
    result["valid"] = not errors
    result["errors"] = errors
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
