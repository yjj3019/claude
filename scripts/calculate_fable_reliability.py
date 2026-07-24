#!/usr/bin/env python3
"""Calculate hash-bound inter-rater reliability for two blinded Fable ballots."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "fable-benchmark.json"
SCORES = (0, 1, 2)


def _load_ballot(path: Path) -> tuple[str, dict[tuple[str, str], int], str, list[str]]:
    raw = path.read_bytes()
    document = json.loads(raw.decode("utf-8-sig"))
    rater_id, ratings = document.get("rater_id"), document.get("ratings")
    if not isinstance(rater_id, str) or not rater_id or not isinstance(ratings, list) or not ratings:
        raise ValueError(f"invalid ballot: {path}")
    indexed = {}
    for rating in ratings:
        if not isinstance(rating, dict):
            raise ValueError(f"invalid rating in {path}")
        blind_id = rating.get("blind_id")
        dimension = rating.get("dimension", "overall")
        score = rating.get("score")
        key = (blind_id, dimension)
        if (not isinstance(blind_id, str) or not blind_id or
                not isinstance(dimension, str) or not dimension or
                not isinstance(score, int) or isinstance(score, bool) or score not in SCORES or key in indexed):
            raise ValueError(f"invalid or duplicate rating in {path}")
        indexed[key] = score
    batch_ids = document.get("batch_ids", [])
    if (not isinstance(batch_ids, list) or len(batch_ids) != len(set(batch_ids))
            or any(not isinstance(item, str) or not item for item in batch_ids)):
        raise ValueError(f"invalid batch_ids in {path}")
    return rater_id, indexed, hashlib.sha256(raw).hexdigest(), batch_ids


def weighted_kappa(left: list[int], right: list[int]) -> float:
    count = len(left)
    span = SCORES[-1] - SCORES[0]
    observed = sum(((a - b) / span) ** 2 for a, b in zip(left, right)) / count
    left_counts = {score: left.count(score) for score in SCORES}
    right_counts = {score: right.count(score) for score in SCORES}
    expected = sum(
        left_counts[a] * right_counts[b] / count ** 2 * ((a - b) / span) ** 2
        for a, b in itertools.product(SCORES, repeat=2)
    )
    if expected == 0:
        return 1.0 if observed == 0 else 0.0
    return 1 - observed / expected


def calculate(ballot_paths: list[Path], config_path: Path = CONFIG) -> dict:
    if len(ballot_paths) != 2:
        raise ValueError("exactly two blinded rater ballots are required")
    ballots = [_load_ballot(path) for path in ballot_paths]
    if ballots[0][0] == ballots[1][0]:
        raise ValueError("ballots must come from distinct raters")
    if set(ballots[0][1]) != set(ballots[1][1]):
        raise ValueError("ballots must rate identical blind_id/dimension items")
    if ballots[0][3] != ballots[1][3]:
        raise ValueError("ballots must identify identical batch_ids")
    keys = sorted(ballots[0][1])
    kappa = weighted_kappa([ballots[0][1][key] for key in keys], [ballots[1][1][key] for key in keys])
    observed_by_rater = [sorted(set(ballot[1].values())) for ballot in ballots]
    threshold = json.loads(config_path.read_text(encoding="utf-8-sig"))["gates"]["minimum_inter_rater_reliability"]
    return {
        "schema_version": "1.0", "method": "quadratic_weighted_cohen_kappa",
        "rater_ids": [ballot[0] for ballot in ballots], "ballot_sha256": [ballot[2] for ballot in ballots],
        "batch_ids": ballots[0][3],
        "rated_item_count": len(keys), "score_scale": list(SCORES),
        "observed_scores_by_rater": observed_by_rater,
        "all_raters_observed_full_scale": all(scores == list(SCORES) for scores in observed_by_rater),
        "reliability": kappa,
        "minimum_required": threshold, "reliability_gate_pass": kappa >= threshold,
        "benchmark_promotion_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ballot", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = calculate(args.ballot)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps(result, indent=2))
    return 0 if result["reliability_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
