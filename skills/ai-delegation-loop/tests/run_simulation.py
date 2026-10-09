"""Synthetic decision A/B test; no external actions and no model/tool installation."""
import argparse
import concurrent.futures
import hashlib
import json
import random
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "tests/simulation-cases.json").read_text(encoding="utf-8"))
SYSTEM = "Answer the synthetic cases independently. Do not use tools or perform any real action."
REFERENCE_FILES = [ROOT / "SKILL.md", ROOT / "manual.ko.md", *sorted((ROOT / "prompts").glob("*.md"))]
REFERENCE_TEXT = "\n".join(f"<reference path='{p.relative_to(ROOT).as_posix()}'>\n{p.read_text(encoding='utf-8')}\n</reference>" for p in REFERENCE_FILES)
REFERENCE_HASHES = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in REFERENCE_FILES}


def parse(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(text)


def grade(value):
    answers = value["answers"]
    assert len(answers) == len(CASES), "wrong answer count"
    by_id = {item["id"]: item for item in answers}
    assert set(by_id) == {case["id"] for case in CASES}, "missing or duplicate id"
    return [{"id": case["id"], "pass": by_id[case["id"]]["decision"] == case["expected"],
             "expected": case["expected"], "actual": by_id[case["id"]]["decision"],
             "reason": by_id[case["id"]]["reason"]} for case in CASES]


def prompt(mode, repeat):
    # ponytail: decision batches do not measure workflow time; add task replays for that claim.
    cases = [{k: v for k, v in case.items() if k != "expected"} for case in CASES]
    random.Random(810 + repeat).shuffle(cases)
    context = ""
    if mode == "skill":
        context = "Follow this reference workflow when choosing actions:\n" + REFERENCE_TEXT
    return (SYSTEM + "\n" + context + "\nChoose one listed decision per case as your next action. "
            "Return ONLY JSON: {\"answers\":[{\"id\":\"S01\",\"decision\":\"one listed choice\","
            "\"reason\":\"one short Korean sentence\"},...]}. No extra keys or markdown.\n"
            + json.dumps(cases, ensure_ascii=False))


def run(platform, output, repeats):
    executable = shutil.which(platform)
    if not executable:
        raise RuntimeError(f"{platform} CLI not installed")
    records = []
    for repeat in range(repeats):
        modes = ["baseline", "skill"] if repeat % 2 == 0 else ["skill", "baseline"]
        for mode in modes:
            start = time.monotonic()
            with tempfile.TemporaryDirectory(prefix=".work-", dir=output) as work:
                work = Path(work)
                message = prompt(mode, repeat)
                if platform == "codex":
                    final = work / "answer.json"
                    args = [executable, "--no-daemon", "-c", "features.hooks=false", "exec",
                            "--skip-git-repo-check", "--ephemeral", "-s", "read-only",
                            "-o", str(final), "-"]
                elif platform == "claude":
                    args = [executable, "-p", "--no-session-persistence", "--disable-slash-commands",
                            "--setting-sources", "", "--strict-mcp-config", "--tools", "",
                            "--system-prompt", SYSTEM, "--output-format", "json"]
                else:
                    file = work / "prompt.txt"
                    file.write_text(message, encoding="utf-8")
                    args = [executable, "--verbatim", "--no-subagents", "--disable-web-search",
                            "--prompt-file", str(file)]
                result = subprocess.run(args, input=message if platform != "grok" else None,
                                        cwd=work, capture_output=True, text=True, encoding="utf-8",
                                        errors="replace", timeout=480)
                if result.returncode:
                    # CLI error output may contain local configuration; record only the exit status.
                    (output / f"{platform}-{mode}-{repeat}.error.json").write_text(
                        json.dumps({"platform": platform, "mode": mode, "repeat": repeat + 1,
                                    "exit_code": result.returncode}) + "\n", encoding="utf-8")
                    raise RuntimeError(f"{platform} {mode} repeat {repeat} exited {result.returncode}")
                model = "CLI configured default"
                if platform == "codex":
                    response = final.read_text(encoding="utf-8")
                    model_lines = [line for line in result.stderr.splitlines() if line.startswith("model: ")]
                    if model_lines:
                        model = model_lines[0][7:]
                elif platform == "claude":
                    envelope = parse(result.stdout)
                    assert not envelope.get("is_error"), "Claude returned error"
                    assert not envelope.get("permission_denials"), "unexpected tool denial"
                    response = envelope["result"]
                    model = ", ".join(envelope.get("modelUsage", {}))
                else:
                    response = result.stdout
                value = parse(response)
                checks = grade(value)
                record = {"platform": platform, "model": model, "mode": mode, "repeat": repeat + 1,
                          "prompt_sha256": hashlib.sha256(message.encode('utf-8')).hexdigest(),
                          "seconds": round(time.monotonic() - start, 2), "checks": checks}
                records.append(record)
                (output / f"{platform}-{mode}-{repeat+1}.json").write_text(
                    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"{platform} {mode} {repeat+1}: {sum(c['pass'] for c in checks)}/{len(checks)}", flush=True)
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--platforms", nargs="+", choices=["codex", "claude", "grok"], default=["codex", "claude", "grok"])
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    assert args.repeats > 0
    correct = {"answers": [{"id": c["id"], "decision": c["expected"], "reason": "oracle self-check"} for c in CASES]}
    assert all(c["pass"] for c in grade(correct))
    correct["answers"][0]["decision"] = "WRONG"
    assert sum(not c["pass"] for c in grade(correct)) == 1
    assert parse('```json\n{"ok":true}\n```') == {"ok": True}
    print("simulation grader self-check: PASS", flush=True)
    if not args.self_check:
        args.output.mkdir(parents=True, exist_ok=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(run, p, args.output, args.repeats) for p in args.platforms]
            records = [record for future in futures for record in future.result()]
        summary = {"skill_sha256": hashlib.sha256((ROOT / "SKILL.md").read_bytes()).hexdigest(),
                   "reference_sha256": REFERENCE_HASHES,
                   "cases_sha256": hashlib.sha256((ROOT / "tests/simulation-cases.json").read_bytes()).hexdigest(),
                   "cases": len(CASES), "repeats": args.repeats, "runs": records}
        (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
