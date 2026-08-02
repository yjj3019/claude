#!/usr/bin/env python3
"""Manual A/B run helper for the skills-migration experiment.

Wraps the per-session mechanics of docs/skills-ab-protocol.md so each of the
manual Claude Code sessions becomes: prepare -> run the session -> collect.
Scoring reuses run_golden_test_coding; the merge decision in `report` applies
the pre-registered rule and never merges anything itself.

Usage:
    # 1. Before a session: reset the arm clone's fixture and print the prompt
    python scripts/run_skills_ab.py prepare --arm A --arm-root ~/ab/arm-a --test 012

    # 2. Run the Claude Code session inside the arm clone with that prompt.

    # 3. After the session: copy the edited fixture out, score, append record
    python scripts/run_skills_ab.py collect --arm A --arm-root ~/ab/arm-a \
        --test 012 --run 1 --batch BATCH-1 --model <model> --skill-triggered unknown

    # 4. Any time: aggregate and apply the pre-registered decision rule
    python scripts/run_skills_ab.py report --batch BATCH-1
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_golden_test_coding import TEST_CONFIG  # noqa: E402

RESULTS_DIR = ROOT / "tests" / "results" / "skills-ab"
LOCAL_DIR = ROOT / ".local" / "skills-ab"
ARMS = ("A", "B")


def fixture_rel(test_id: str) -> Path:
    return Path("tests") / "fixtures" / TEST_CONFIG[test_id]["fixture"]


def check_arm_root(arm_root: Path) -> None:
    if not (arm_root / "CLAUDE.md").is_file() or not (arm_root / "kernel").is_dir():
        raise SystemExit(f"ERROR: {arm_root} is not an FEF repo root")
    if arm_root == ROOT:
        raise SystemExit(
            "ERROR: arm-root resolves to the helper checkout itself. Run the helper "
            "from the experiment checkout (e.g. ClaudeGit) with --arm-root pointing "
            "at a SEPARATE arm clone; scoring an arm against itself always reads as "
            "no code change."
        )


def git(arm_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=arm_root, capture_output=True, text=True, timeout=60)


def cmd_prepare(args) -> int:
    arm_root = args.arm_root.expanduser().resolve()
    check_arm_root(arm_root)
    rel = fixture_rel(args.test)
    reset = git(arm_root, "checkout", "--", str(rel))
    clean = git(arm_root, "clean", "-fd", "--", str(rel))
    if reset.returncode != 0 or clean.returncode != 0:
        print(reset.stderr + clean.stderr, file=sys.stderr)
        return 2
    branch = git(arm_root, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    prompt = (ROOT / "tests" / "prompts" / f"GT{args.test}-baseline.md").read_text(encoding="utf-8-sig")
    print(f"[prepare] arm={args.arm} test=GT{args.test} arm_root={arm_root} (branch: {branch})")
    print(f"[prepare] fixture reset: {rel}")
    print("[prepare] start a fresh Claude Code session IN THE ARM ROOT and paste this prompt:")
    print("-" * 60)
    print(prompt.rstrip())
    print("-" * 60)
    print(f"[prepare] after the session: run collect with --arm {args.arm} --test {args.test}")
    return 0


def cmd_collect(args) -> int:
    arm_root = args.arm_root.expanduser().resolve()
    check_arm_root(arm_root)
    rel = fixture_rel(args.test)
    src = arm_root / rel
    dest = LOCAL_DIR / args.batch / args.arm / f"GT{args.test}" / f"run{args.run}"
    if dest.exists():
        raise SystemExit(f"ERROR: {dest} already exists; refusing to overwrite a recorded run")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "answers"))
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_golden_test_coding.py"),
         "--test", args.test, "--edited-dir", str(dest)],
        capture_output=True, text=True, timeout=300,
    )
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print(proc.stdout + proc.stderr, file=sys.stderr)
        return 2
    record = {
        "arm": args.arm, "test": args.test, "run": args.run,
        "exit_code": proc.returncode,
        "mechanical_score_cap": result["mechanical_score_cap"],
        "cap_reasons": result["cap_reasons"],
        "model": args.model,
        "skill_triggered": args.skill_triggered,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    batch_file = RESULTS_DIR / f"{args.batch}.json"
    batch = json.loads(batch_file.read_text(encoding="utf-8")) if batch_file.is_file() else {"batch": args.batch, "records": []}
    for existing in batch["records"]:
        if (existing["arm"], existing["test"], existing["run"]) == (args.arm, args.test, args.run):
            raise SystemExit(f"ERROR: record arm={args.arm} test={args.test} run={args.run} already in {batch_file.name}")
    batch["records"].append(record)
    batch_file.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    status = "PASS" if proc.returncode == 0 else "FAIL"
    try:
        shown = batch_file.relative_to(ROOT)
    except ValueError:
        shown = batch_file
    print(f"[collect] {status} cap={result['mechanical_score_cap']} -> {shown} ({len(batch['records'])} records)")
    if result["cap_reasons"]:
        for r in result["cap_reasons"]:
            print(f"[collect]   reason: {r}")
    return 0


def cmd_report(args) -> int:
    batch_file = RESULTS_DIR / f"{args.batch}.json"
    if not batch_file.is_file():
        raise SystemExit(f"ERROR: no batch file {batch_file}")
    batch = json.loads(batch_file.read_text(encoding="utf-8"))
    records = batch["records"]
    print(f"[report] batch={args.batch} records={len(records)}")
    rates = {}
    for arm in ARMS:
        arm_records = [r for r in records if r["arm"] == arm]
        passes = sum(1 for r in arm_records if r["exit_code"] == 0)
        rates[arm] = (passes, len(arm_records))
        rate = f"{passes}/{len(arm_records)}" if arm_records else "0/0"
        print(f"[report] arm {arm}: pass {rate}")
        for test_id in sorted(TEST_CONFIG):
            trs = [r for r in arm_records if r["test"] == test_id]
            if trs:
                p = sum(1 for r in trs if r["exit_code"] == 0)
                print(f"[report]   GT{test_id}: {p}/{len(trs)}")
    b_only_failures = sorted({
        r["test"] for r in records
        if r["arm"] == "B" and r["exit_code"] != 0
        and all(x["exit_code"] == 0 for x in records if x["arm"] == "A" and x["test"] == r["test"])
    })
    a_pass, a_n = rates["A"]
    b_pass, b_n = rates["B"]
    if a_n == 0 or b_n == 0:
        print("[report] decision: INSUFFICIENT - both arms need recorded runs")
        return 0
    a_rate, b_rate = a_pass / a_n, b_pass / b_n
    if b_rate >= a_rate and not b_only_failures:
        print(f"[report] decision: MERGE-B eligible (B {b_rate:.0%} >= A {a_rate:.0%}, no B-only failure mode)")
    else:
        why = []
        if b_rate < a_rate:
            why.append(f"B {b_rate:.0%} < A {a_rate:.0%}")
        if b_only_failures:
            why.append("B-only failures on GT" + ", GT".join(b_only_failures))
        print(f"[report] decision: REJECT-B ({'; '.join(why)})")
    print("[report] note: per protocol, also review skill_triggered observations and transcripts before merging.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "collect"):
        p = sub.add_parser(name)
        p.add_argument("--arm", choices=ARMS, required=True)
        p.add_argument("--arm-root", type=Path, required=True)
        p.add_argument("--test", choices=sorted(TEST_CONFIG), required=True)
        if name == "collect":
            p.add_argument("--run", type=int, required=True)
            p.add_argument("--batch", required=True)
            p.add_argument("--model", default="unknown")
            p.add_argument("--skill-triggered", choices=("yes", "no", "unknown", "n/a"), default="unknown")
    p = sub.add_parser("report")
    p.add_argument("--batch", required=True)
    args = parser.parse_args(argv)
    return {"prepare": cmd_prepare, "collect": cmd_collect, "report": cmd_report}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
