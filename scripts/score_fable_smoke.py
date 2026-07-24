#!/usr/bin/env python3
"""Deterministically score blinded smoke responses and preserve human ballots."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / "tests" / "benchmarks" / "pilot"
DECLARATIVE_KEYS = {"schema_version", "required_phrases", "forbidden_phrases", "accepted_outputs", "constraints", "hard_failure_on", "manual_review_on"}
LEGACY_KEYS = {"required_concepts", "forbidden_claims", "accepted_outputs", "maximum_output_lines", "maximum_output_characters", "maximum_tool_calls", "hard_failure", "scoring"}
FAILURE_EVENTS = {"forbidden_phrase", "line_limit", "character_limit", "tool_limit"}
MANUAL_EVENTS = {"required_phrase_missing", "accepted_output_mismatch", "tool_calls_unknown"}
EVIDENCE_CONFLICT_DIMENSIONS = {
    "artifact_created", "scope_satisfied", "verification_succeeded",
    "unsupported_claim_absent", "overall_success",
}


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
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"(?<=\d),(?=\d)", "", " ".join(text.strip().split())).casefold()


def validate_checks(checks: dict) -> dict:
    keys = set(checks)
    if checks.get("schema_version") == "1.0":
        if not keys <= DECLARATIVE_KEYS:
            raise ValueError(f"unsupported declarative check keys: {sorted(keys - DECLARATIVE_KEYS)}")
        normalized = dict(checks)
    elif keys <= LEGACY_KEYS:
        normalized = {
            "schema_version": "legacy",
            "required_phrases": checks.get("required_concepts", []),
            "forbidden_phrases": checks.get("forbidden_claims", []),
            "accepted_outputs": checks.get("accepted_outputs", []),
            "constraints": {key: checks[key] for key in ("maximum_output_lines", "maximum_output_characters", "maximum_tool_calls") if key in checks},
            "hard_failure_on": ["forbidden_phrase"] if checks.get("forbidden_claims") else [],
            "manual_review_on": ["required_phrase_missing", "accepted_output_mismatch", "tool_calls_unknown"],
        }
    else:
        raise ValueError("check spec must use schema_version 1.0 or supported legacy keys")
    phrase_fields = ("required_phrases", "forbidden_phrases", "accepted_outputs")
    for field in phrase_fields:
        values = normalized.get(field, [])
        maximum = 20 if field == "accepted_outputs" else 50
        if not isinstance(values, list) or len(values) > maximum or len(values) != len(set(values)) or any(not isinstance(item, str) or not item.strip() for item in values):
            raise ValueError(f"{field} must be a bounded list of non-empty strings")
    constraints = normalized.get("constraints", {})
    allowed_constraints = {"maximum_output_lines", "maximum_output_characters", "maximum_tool_calls"}
    if not isinstance(constraints, dict) or not set(constraints) <= allowed_constraints:
        raise ValueError("constraints contain unsupported keys")
    for key, value in constraints.items():
        minimum = 0 if key == "maximum_tool_calls" else 1
        if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
            raise ValueError(f"{key} must be an integer >= {minimum}")
    hard = normalized.get("hard_failure_on", [])
    manual = normalized.get("manual_review_on", [])
    if not isinstance(hard, list) or len(hard) != len(set(hard)) or not set(hard) <= FAILURE_EVENTS:
        raise ValueError("hard_failure_on contains unsupported events")
    if not isinstance(manual, list) or len(manual) != len(set(manual)) or not set(manual) <= MANUAL_EVENTS:
        raise ValueError("manual_review_on contains unsupported events")
    if not any(normalized.get(field) for field in (*phrase_fields, "constraints")):
        raise ValueError("at least one automatic check is required")
    return normalized


def score_response(scenario_id: str, response: str, checks: dict, *, tool_calls: int | None = None) -> dict:
    """Score text as inert data. No content in response is ever executed or interpreted as instructions."""
    spec = validate_checks(checks)
    folded = _normalized(response)
    required = {item: _normalized(item) in folded for item in spec.get("required_phrases", [])}
    forbidden = {item: _normalized(item) in folded for item in spec.get("forbidden_phrases", [])}
    accepted_outputs = spec.get("accepted_outputs", [])
    exact = folded in {_normalized(item) for item in accepted_outputs} if accepted_outputs else None
    constraints = spec.get("constraints", {})
    line_count = len(response.strip().splitlines()) if response.strip() else 0
    character_count = len(response)
    line_ok = line_count <= constraints["maximum_output_lines"] if "maximum_output_lines" in constraints else None
    character_ok = character_count <= constraints["maximum_output_characters"] if "maximum_output_characters" in constraints else None
    tool_ok = (None if tool_calls is None else tool_calls <= constraints["maximum_tool_calls"]) if "maximum_tool_calls" in constraints else None
    events = {
        "required_phrase_missing": bool(required) and not all(required.values()),
        "accepted_output_mismatch": exact is False,
        "tool_calls_unknown": "maximum_tool_calls" in constraints and tool_calls is None,
        "forbidden_phrase": any(forbidden.values()),
        "line_limit": line_ok is False,
        "character_limit": character_ok is False,
        "tool_limit": tool_ok is False,
    }
    configured_results = [*required.values(), *(not value for value in forbidden.values())]
    if exact is not None:
        configured_results.append(exact)
    for value in (line_ok, character_ok, tool_ok):
        if value is not None:
            configured_results.append(value)
    if events["tool_calls_unknown"]:
        configured_results.append(False)
    hard_failure = any(events[event] for event in spec.get("hard_failure_on", []))
    manual_required = any(events[event] for event in spec.get("manual_review_on", []))
    return {
        "automatic_pass": bool(configured_results) and all(configured_results),
        "hard_failure": hard_failure, "manual_required": manual_required,
        "required_phrases": required, "forbidden_phrases": forbidden,
        "exact_match": exact, "line_count": line_count, "character_count": character_count,
        "line_constraint_pass": line_ok, "character_constraint_pass": character_ok,
        "tool_calls": tool_calls, "tool_constraint_pass": tool_ok,
        "triggered_events": sorted(event for event, triggered in events.items() if triggered),
        "check_schema_version": spec["schema_version"], "scenario_id": scenario_id,
    }


def private_check_map(manifest_path: Path) -> dict[str, tuple[Path, str]]:
    manifest = _load_object(manifest_path)
    mapping = {}
    for entry in manifest.get("entries", []):
        scenario_id, spec = entry.get("scenario_id"), entry.get("check_spec")
        if not ID_RE.fullmatch(scenario_id or "") or scenario_id in mapping or not isinstance(spec, dict):
            raise ValueError("private manifest contains invalid or duplicate scenario checks")
        path = (manifest_path.parent / spec.get("path", "")).resolve()
        if not path.is_relative_to(manifest_path.parent.resolve()) or not path.is_file():
            raise ValueError(f"unsafe or missing private checks for {scenario_id}")
        expected = spec.get("sha256")
        if _hash(path.read_bytes()) != expected:
            raise ValueError(f"private check hash mismatch for {scenario_id}")
        mapping[scenario_id] = (path, expected)
    return mapping


def score_corpus(corpus_dir: Path, output_path: Path, *, checks_root: Path = CHECKS,
                 check_manifest: Path | None = None) -> dict:
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
    private_checks = private_check_map(check_manifest.resolve()) if check_manifest else {}
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
        checks_path, checks_hash = private_checks.get(
            scenario_id, (checks_root / scenario_id / "checks.json", None)
        )
        checks = _load_object(checks_path)
        checks_hash = checks_hash or _hash(checks_path.read_bytes())
        result = score_response(scenario_id, response, checks, tool_calls=entry.get("tool_calls"))
        result.update({"blind_id": blind_id, "scenario_id": scenario_id, "response_sha256": _hash(raw),
                       "check_spec_sha256": checks_hash})
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
    if ballot.get("rubric_id") == "evidence_conflict_v1":
        dimensions_by_blind: dict[str, set[str]] = {}
        seen = set()
        for rating in ratings:
            if not isinstance(rating, dict):
                raise ValueError("evidence-conflict ratings must be objects")
            blind_id, dimension, score = rating.get("blind_id"), rating.get("dimension"), rating.get("score")
            key = (blind_id, dimension)
            if (not ID_RE.fullmatch(blind_id or "") or dimension not in EVIDENCE_CONFLICT_DIMENSIONS
                    or not isinstance(score, int) or isinstance(score, bool) or score not in {0, 1, 2}
                    or key in seen):
                raise ValueError("invalid or duplicate evidence-conflict rating")
            seen.add(key)
            dimensions_by_blind.setdefault(blind_id, set()).add(dimension)
        if any(dimensions != EVIDENCE_CONFLICT_DIMENSIONS for dimensions in dimensions_by_blind.values()):
            raise ValueError("each evidence-conflict item requires all five dimensions")
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
    score.add_argument("--check-manifest", type=Path)
    ballot = sub.add_parser("preserve-ballot")
    ballot.add_argument("--ballot", type=Path, required=True)
    ballot.add_argument("--output-dir", type=Path, required=True)
    adjudicate = sub.add_parser("preserve-adjudication")
    adjudicate.add_argument("--adjudication", type=Path, required=True)
    adjudicate.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "score":
        result = score_corpus(args.corpus_dir, args.output, check_manifest=args.check_manifest)
        print(json.dumps({"scored": len(result["results"]), "output": str(args.output)}, indent=2))
    elif args.command == "preserve-ballot":
        print(preserve_ballot(args.ballot, args.output_dir))
    else:
        print(preserve_adjudication(args.adjudication, args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
