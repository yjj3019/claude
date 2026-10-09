#!/usr/bin/env python3
"""Record/check deterministic document-contract evidence; never invoke model CLIs."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "skills" / "ai-delegation-loop"
SOURCE_REF = "refs/remotes/origin/optimize/three-platforms"


def normalized_hash(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="execute checks and compare records without writing")
    args = parser.parse_args()
    commands = [
        ["-m", "unittest", "discover", "-s", "scripts/delegation", "-p", "test_prompt_contract.py"],
        ["skills/ai-delegation-loop/tests/run_simulation.py", "--output", "./sim", "--self-check"],
    ]
    for command in commands:
        result = subprocess.run([sys.executable, *command], cwd=ROOT, capture_output=True,
                                text=True, encoding="utf-8", errors="replace")
        if result.returncode:
            print(result.stdout + result.stderr)
            return 1
        print("PASS " + " ".join(command))

    from validate_skill import parse_frontmatter
    version = parse_frontmatter((PACKAGE / "SKILL.md").read_text(encoding="utf-8"))["metadata"]["version"]
    references = [PACKAGE / "SKILL.md", PACKAGE / "manual.ko.md", *sorted((PACKAGE / "prompts").glob("*.md"))]
    hashes = {p.relative_to(PACKAGE).as_posix(): normalized_hash(p) for p in references}
    historical = json.loads((PACKAGE / "tests/simulation-results.json").read_text(encoding="utf-8"))
    frozen = [r["data"] for r in historical["rounds"] if "reference_sha256" in r.get("data", {})][-1]
    archive = json.loads((ROOT / "docs/delegation-loop/source-history/manifest.json").read_text(encoding="utf-8"))
    source_files = {entry["path"]: entry for entry in archive["files"][SOURCE_REF]}
    artifact_paths = {
        "tests/simulation-results.json": "skills/ai-delegation-loop/tests/simulation-results.json",
        "tests/native-probe-results.json": "skills/ai-delegation-loop/tests/native-probe-results.json",
        "tests/simulation-report.v1.2.ko.md": "skills/ai-delegation-loop/tests/simulation-report.ko.md",
    }
    artifact_hashes = {}
    for name, original in artifact_paths.items():
        actual = hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
        if actual != source_files[original]["sha256"]:
            raise ValueError("historical artifact differs from archived original: " + name)
        artifact_hashes[name] = actual
    runner_paths = [ROOT / "scripts/delegation/test_prompt_contract.py", Path(__file__),
                    ROOT / "scripts/delegation/validate_skill.py",
                    PACKAGE / "tests/run_simulation.py"]
    input_paths = [PACKAGE / "templates/job-playbook/SKILL.template.md", PACKAGE / "tests/acceptance-cases.md"]
    acceptance = {
        "schema": 1, "package_version": version,
        "scope": "Static prompt contracts, isolated playbook format fixtures and oracle grader self-check; not model behavior",
        "level": "L3", "model_behavior": "UNVERIFIED", "model_cli_executed": False,
        "reference_sha256": hashes, "cases_sha256": normalized_hash(PACKAGE / "tests/simulation-cases.json"),
        "input_sha256": {p.relative_to(PACKAGE).as_posix(): normalized_hash(p) for p in input_paths},
        "runner_sha256": {p.relative_to(ROOT).as_posix(): normalized_hash(p) for p in runner_paths},
        "checks": {"A16-frontmatter-fallback": "PASS", "A17-proof-before-rerun": "PASS",
                   "A18-new-action-approval": "PASS", "A19-durable-protocol": "PASS",
                   "A20-multiple-and-external-causes": "PASS", "oracle-grader-self-check": "PASS"},
    }
    status = {
        "schema": 1, "package_version": version,
        "historical": {"package_version": "1.2", "status": "STALE_FOR_CURRENT_PACKAGE",
                       "source_commit": "01351414e10df3c177939e4fef8393609ece6c55",
                       "reference_sha256": frozen["reference_sha256"], "cases_sha256": frozen["cases_sha256"],
                       "artifact_sha256": artifact_hashes},
        "current": {"model_behavior": "UNVERIFIED", "model_cli_executed": False,
                    "acceptance_results": "tests/acceptance-results.json",
                    "acceptance_results_sha256": hashlib.sha256(encoded(acceptance)).hexdigest()},
    }
    changes = []
    for original, entry in sorted(source_files.items()):
        if not original.startswith("skills/ai-delegation-loop/"):
            continue
        actual = hashlib.sha256((ROOT / original).read_bytes()).hexdigest()
        record = {"path": original, "source_blob": entry["blob"], "source_sha256": entry["sha256"],
                  "current_sha256": actual, "classification": "UNCHANGED" if actual == entry["sha256"] else "MODIFIED"}
        if original.endswith("/tests/simulation-report.ko.md"):
            record["historical_copy"] = "skills/ai-delegation-loop/tests/simulation-report.v1.2.ko.md"
        changes.append(record)
    integration = {"schema": 1, "package_version": version, "source_version": "1.2",
                   "source_commit": status["historical"]["source_commit"],
                   "source_bundle_sha256": archive["artifacts"]["DelegationLoop.bundle"]["sha256"],
                   "historical_model_evidence": "STALE_FOR_CURRENT_PACKAGE", "current_model_behavior": "UNVERIFIED",
                   "original_files": changes}
    outputs = {PACKAGE / "tests/acceptance-results.json": acceptance,
               PACKAGE / "tests/evidence-status.json": status,
               ROOT / "docs/delegation-loop/integration-manifest.json": integration}
    for path, value in outputs.items():
        raw = encoded(value)
        if args.check:
            if not path.is_file() or path.read_bytes() != raw:
                print("FAIL deterministic evidence differs: " + path.relative_to(ROOT).as_posix())
                return 1
        else:
            path.write_bytes(raw)
    print("Deterministic evidence " + ("verified" if args.check else "recorded") +
          "; v1.2 model evidence HISTORICAL/STALE; current model behavior UNVERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
