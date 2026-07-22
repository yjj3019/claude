#!/usr/bin/env python3
"""Dependency-free leakage checks for benchmark candidate and reference texts."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def normalized_tokens(text: str) -> list[str]:
    return re.findall(r"[\w-]+", text.casefold(), flags=re.UNICODE)


def shingles(tokens: list[str], size: int) -> set[str]:
    if len(tokens) < size:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[index:index + size]) for index in range(len(tokens) - size + 1)}


def minhash_signature(values: set[str], permutations: int = 128) -> list[int]:
    if not values:
        return []
    signature = []
    for seed in range(permutations):
        signature.append(min(int(hashlib.sha256(f"{seed}:{value}".encode()).hexdigest(), 16) for value in values))
    return signature


def minhash_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    a, b = minhash_signature(left), minhash_signature(right)
    return sum(x == y for x, y in zip(a, b)) / len(a)


def load_texts(paths: list[Path]) -> list[dict]:
    records = []
    for path in paths:
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
        records.append({"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "text": text})
    return records


def analyze(candidates: list[dict], references: list[dict], *, ngram_size: int, ceiling: float, canaries: list[str]) -> dict:
    pairs, failed = [], False
    for candidate in candidates:
        candidate_tokens = normalized_tokens(candidate["text"])
        candidate_shingles = shingles(candidate_tokens, ngram_size)
        found_canaries = [item for item in canaries if item.casefold() in candidate["text"].casefold()]
        if found_canaries:
            failed = True
        for reference in references:
            reference_shingles = shingles(normalized_tokens(reference["text"]), ngram_size)
            exact_hash = candidate["sha256"] == reference["sha256"]
            overlap = sorted(candidate_shingles & reference_shingles)
            similarity = minhash_similarity(candidate_shingles, reference_shingles)
            pair_failed = exact_hash or bool(overlap) or similarity > ceiling
            failed = failed or pair_failed
            pairs.append({
                "candidate_path": candidate["path"], "reference_path": reference["path"],
                "exact_hash_match": exact_hash, "normalized_ngram_overlap_count": len(overlap),
                "minhash_similarity": round(similarity, 6), "failed": pair_failed,
            })
    semantic = {"status": "not_run", "reason": "no_local_embedding_evidence"}
    return {
        "valid": not failed,
        "complete": False,
        "promotion_eligible": False,
        "promotion_blockers": ["semantic_similarity_not_run", "private_holdout_provenance_not_verified"],
        "candidate_count": len(candidates), "reference_count": len(references),
        "candidates": [{"path": item["path"], "sha256": item["sha256"]} for item in candidates],
        "references": [{"path": item["path"], "sha256": item["sha256"]} for item in references],
        "ngram_size": ngram_size, "minhash_similarity_ceiling": ceiling,
        "canary_hits": [
            {"candidate_path": item["path"], "values": [c for c in canaries if c.casefold() in item["text"].casefold()]}
            for item in candidates if any(c.casefold() in item["text"].casefold() for c in canaries)
        ],
        "canary_sha256s": sorted(hashlib.sha256(item.encode("utf-8")).hexdigest() for item in canaries),
        "semantic_similarity": semantic,
        "pairs": pairs,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", action="append", required=True, type=Path)
    parser.add_argument("--reference", action="append", required=True, type=Path)
    parser.add_argument("--canary", action="append", default=[])
    parser.add_argument("--ngram-size", type=int, default=8)
    parser.add_argument("--minhash-ceiling", type=float, default=0.80)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.ngram_size < 2 or not 0 <= args.minhash_ceiling <= 1:
        parser.error("ngram size must be >=2 and minhash ceiling must be between 0 and 1")
    result = analyze(load_texts(args.candidate), load_texts(args.reference), ngram_size=args.ngram_size,
                     ceiling=args.minhash_ceiling, canaries=args.canary)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
