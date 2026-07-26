#!/usr/bin/env python3
"""Export a diagnostic plan as copy/paste prompts without evaluator assets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_ROOT = (ROOT / ".local" / "fable").resolve()


def contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def render(artifact: dict) -> str:
    parts = []
    if artifact.get("instruction_prefix"):
        parts.append(artifact["instruction_prefix"].strip())
    parts.append(artifact["user_prompt"].strip())
    for fixture in artifact.get("fixtures", []):
        parts.append(f"### {fixture['name']}\n\n{fixture['content'].strip()}")
    return "\n\n".join(parts) + "\n"


def export(plan_path: Path, output_dir: Path, *, allowed_root: Path = LOCAL_ROOT) -> dict:
    plan_path, output_dir, allowed_root = plan_path.resolve(), output_dir.resolve(), allowed_root.resolve()
    if not contained(plan_path, allowed_root) or not contained(output_dir, allowed_root):
        raise ValueError("plan and output must stay under .local/fable")
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite output directory: {output_dir}")
    plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    if plan.get("diagnostic_only") is not True or plan.get("repetitions") != 1:
        raise ValueError("only one-repetition diagnostic plans can be exported")
    package = plan_path.with_name(f"{plan_path.stem}-package").resolve()
    output_dir.mkdir(parents=True)
    items = []
    for order, run in enumerate(plan["runs"], 1):
        artifact_path = (package / run["artifact_path"]).resolve()
        if not contained(artifact_path, package):
            raise ValueError(f"artifact path escapes package: {run['run_id']}")
        artifact_raw = artifact_path.read_bytes()
        if hashlib.sha256(artifact_raw).hexdigest() != run["prompt_hash"]:
            raise ValueError(f"artifact hash mismatch: {run['run_id']}")
        artifact = json.loads(artifact_raw.decode("utf-8-sig"))
        prompt = render(artifact)
        prompt_path = output_dir / f"{order:02d}-{run['run_id']}.md"
        prompt_raw = prompt.encode("utf-8")
        prompt_path.write_bytes(prompt_raw)
        items.append({
            "order": order, "run_id": run["run_id"], "requested_model": run["requested_model"],
            "variant_id": run["variant_id"], "prompt_path": prompt_path.name,
            "prompt_sha256": hashlib.sha256(prompt_raw).hexdigest(),
        })
    index = {
        "schema_version": "1.0", "diagnostic_only": True, "batch_id": plan["batch_id"],
        "prompt_count": len(items), "items": items,
    }
    (output_dir / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    return index


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    result = export(args.plan, args.output_dir)
    print(json.dumps({key: result[key] for key in ("batch_id", "prompt_count", "diagnostic_only")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
