#!/usr/bin/env python3
"""Detect a candidate FEF task route."""
import argparse
import json

from lib.adaptive_effort import TIERS, effective_tier
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

    # R2-P1-RISK-TIER-DECOUPLED: emit effective effort after risk floor / L0 leak.
    tier_id, effort_reason = effective_tier(
        args.task,
        risk_level=result.get("risk_level", "low"),
        selection=result,
    )
    result["effort_tier"] = tier_id
    result["model"] = TIERS[tier_id].model
    if effort_reason:
        result["effort_reason"] = effort_reason

    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
