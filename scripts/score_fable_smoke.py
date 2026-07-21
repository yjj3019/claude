#!/usr/bin/env python3
"""Deterministically score blinded smoke responses and preserve human ballots."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / "tests" / "benchmarks" / "pilot"


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _safe_child(parent: Path, name: str) -> Path:
    if not ID_RE.fullmatch(name):
        raise ValueError(f"unsafe identifier: {name!r}")
    parent = parent.resolve()
    child = (parent / name).resolve()
    if child.parent != parent:
        raise ValueError("path escapes output directory")
    return child


def _normalized(text: str) -> str:
    return " ".join(text.strip().split()).casefold()


def score_response(scenario_id: str, response: str, checks: dict, *, tool_calls: int | None = None) -> dict:
    """Score text as inert data. No content in response is ever executed or interpreted as instructions."""
    if scenario_id == "PB001":
        folded = _normalized(response)
        required = {item: _normalized(item) in folded for item in checks["required_concepts"]}
        forbidden = {item: _normalized(item) in folded for item in checks["forbidden_claims"]}
        passed = all(required.values()) and not any(forbidden.values())
        return {
            "automatic_pass": passed,
            "required_concepts": required,
            "forbidden_claims": forbidden,
            "manual_required": not passed,
        }
    if scenario_id == "PB002":
        normalized = _normalized(response)
        accepted = [_normalized(item) for item in checks["accepted_outputs"]]
        exact = normalized in accepted
        line_count = len(response.strip().splitlines()) if response.strip() else 0
        line_ok = line_count <= checks["maximum_output_lines"]
        tool_ok = None if tool_calls is None else tool_calls <= checks["maximum_tool_calls"]
        return {
            "automatic_pass": exact and line_ok and tool_ok is True,
            "exact_match": exact,
            "manual_equivalence_required": not exact,
            "line_count": line_count,
            "line_constraint_pass": line_ok,
            "tool_calls": tool_calls,
            "tool_constraint_pass": tool_ok,
            "manual_required": not exact or tool_ok is None,
        }
    raise ValueError(f"unsupported smoke scenario: {scenario_id}")


def score_corpus(corpus_dir: Path, output_path: Path, *, checks_root: Path = CHECKS) -> dict:
    corpus_dir = corpus_dir.resolve()
    ballot_path = corpus_dir / "ballot.json"
    source_kind = "blinded_corpus"
    if ballot_path.is_file():
        ballot = json.loads(ballot_path.read_text(encoding="utf-8"))
        if not isinstance(ballot, list):
            raise ValueError("ballot.json must contain a list")
    else:
        source_kind = "imported_corpus"
        ballot = []
        for metadata_path in sorted(corpus_dir.glob("*.json")):
            metadata = _load_object(metadata_path)
            if metadata.get("status") != "imported":
                continue
            ballot.append({
                "blind_id": metadata.get("run_id"),
                "scenario_id": metadata.get("scenario_id"),
                "response_path": metadata.get("response_path"),
                "response_sha256": metadata.get("response_sha256"),
                "tool_calls": metadata.get("tool_calls"),
            })
        if not ballot:
            raise ValueError("no eligible blinded or imported responses")
    results = []
    seen = set()
    for entry in ballot:
        blind_id, scenario_id = entry.get("blind_id"), entry.get("scenario_id")
        if not ID_RE.fullmatch(blind_id or "") or blind_id in seen:
            raise ValueError("invalid or duplicate blind_id")
        seen.add(blind_id)
        response_path = (corpus_dir / entry["response_path"]).resolve()
        if response_path.parent != corpus_dir or not response_path.is_file():
            raise ValueError(f"unsafe or missing response for {blind_id}")
        raw = response_path.read_bytes()
        if _hash(raw) != entry.get("response_sha256"):
            raise ValueError(f"response hash mismatch for {blind_id}")
        response = raw.decode("utf-8")
        checks = _load_object(checks_root / scenario_id / "checks.json")
        result = score_response(scenario_id, response, checks, tool_calls=entry.get("tool_calls"))
        result.update({"blind_id": blind_id, "scenario_id": scenario_id, "response_sha256": _hash(raw)})
        results.append(result)
    document = {"schema_version": "1.0", "source": source_kind, "results": results}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as handle:
        json.dump(document, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return document


def preserve_ballot(ballot_path: Path, output_dir: Path) -> Path:
    ballot = _load_object(ballot_path)
    rater_id, ballot_id = ballot.get("rater_id"), ballot.get("ballot_id")
    if not ID_RE.fullmatch(rater_id or "") or not ID_RE.fullmatch(ballot_id or ""):
        raise ValueError("ballot requires safe rater_id and ballot_id")
    ratings = ballot.get("ratings")
    if not isinstance(ratings, list) or not ratings:
        raise ValueError("ballot ratings must be a non-empty list")
    stored = dict(ballot)
    stored["preserved_at_utc"] = datetime.now(timezone.utc).isoformat()
    stored["source_sha256"] = _hash(ballot_path.read_bytes())
    rater_dir = _safe_child(output_dir, rater_id)
    rater_dir.mkdir(parents=True, exist_ok=True)
    destination = _safe_child(rater_dir, f"{ballot_id}.json")
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(stored, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return destination


def preserve_adjudication(adjudication_path: Path, output_dir: Path) -> Path:
    record = _load_object(adjudication_path)
    adjudication_id = record.get("adjudication_id")
    sources = record.get("source_ballot_sha256")
    if not ID_RE.fullmatch(adjudication_id or ""):
        raise ValueError("adjudication requires a safe adjudication_id")
    if not isinstance(sources, list) or len(sources) < 2 or any(not re.fullmatch(r"[0-9a-f]{64}", x or "") for x in sources):
        raise ValueError("adjudication requires at least two source ballot hashes")
    destination = _safe_child(output_dir, f"{adjudication_id}.json")
    output_dir.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score")
    score.add_argument("--corpus-dir", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    ballot = sub.add_parser("preserve-ballot")
    ballot.add_argument("--ballot", type=Path, required=True)
    ballot.add_argument("--output-dir", type=Path, required=True)
    adjudicate = sub.add_parser("preserve-adjudication")
    adjudicate.add_argument("--adjudication", type=Path, required=True)
    adjudicate.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "score":
        result = score_corpus(args.corpus_dir, args.output)
        print(json.dumps({"scored": len(result["results"]), "output": str(args.output)}, indent=2))
    elif args.command == "preserve-ballot":
        print(preserve_ballot(args.ballot, args.output_dir))
    else:
        print(preserve_adjudication(args.adjudication, args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
