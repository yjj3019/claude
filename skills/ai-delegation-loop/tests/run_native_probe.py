"""Install only in disposable folders; exercise explicit skill calls without external actions."""
import concurrent.futures
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests/native-probe-results.json"
WORK_ROOT = ROOT.parents[1] / ".simulation/native"
REQUEST = ("이번 시험은 합성 주간 고객 보고 업무다. 매주 반복하고 오류를 수치로 판정하며 20분 내 설명 가능하다. "
           "아직 인터뷰 답변은 0개이고 인터뷰 완료 선언도 없다. 선택한 스킬과 그 안의 prompts/01-interview.md를 "
           "읽고 인터뷰 첫 질문 하나만 한국어로 해라. 이 시험 폴더 밖 파일을 읽거나 웹·외부 앱·하위 에이전트를 "
           "사용하지 마라. 파일을 생성·수정하지 마라. 저장했다고 말하지 마라. "
           "읽기가 차단되면 같은 명령을 반복하지 말고, 이 시험 폴더의 SKILL.md와 prompts/01-interview.md "
           "읽기만 승인 경로에 요청해라. ACL·보안 정책을 변경하거나 샌드박스를 비활성화하지 마라.")


def probe(platform):
    assert platform in {"codex", "claude", "grok"}
    assert WORK_ROOT.resolve().is_relative_to(ROOT.parents[1].resolve()), "test directory escapes the workspace"
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{platform}-", dir=WORK_ROOT) as folder:
        work = Path(folder)
        prefix = {"codex": ".agents", "claude": ".claude", "grok": ".grok"}[platform]
        installed = work / prefix / "skills/ai-delegation-loop"
        shutil.copytree(ROOT, installed)
        # A real repository boundary keeps parent skill discovery out of the fixture.
        git = shutil.which("git")
        assert git, "Git is required for the disposable repository boundary"
        subprocess.run([git, "init", "-q", str(work)], check=True, capture_output=True)
        call = "$ai-delegation-loop" if platform == "codex" else "/ai-delegation-loop"
        message = call + "\n" + REQUEST
        executable = shutil.which(platform)
        if not executable:
            raise RuntimeError(f"{platform} not installed")
        if platform == "codex":
            final = work / "answer.txt"
            args = [executable, "--no-daemon", "-c", "features.hooks=false", "-a", "on-request",
                    "-c", 'approvals_reviewer="auto_review"', "exec", "--ephemeral",
                    "--skip-git-repo-check", "-s", "read-only", "--json", "-o", str(final), "-"]
        elif platform == "claude":
            args = [executable, "-p", "--no-session-persistence", "--setting-sources", "project",
                    "--strict-mcp-config", "--tools", "Skill,Read", "--allowedTools", "Skill,Read",
                    "--system-prompt", "Work only on the synthetic test in the current folder.",
                    "--output-format", "stream-json", "--verbose"]
        else:
            file = work / "prompt.txt"
            file.write_text(message, encoding="utf-8")
            args = [executable, "--no-subagents", "--disable-web-search", "--permission-mode", "plan",
                    "--output-format", "streaming-messages-json", "--prompt-file", str(file)]
        try:
            result = subprocess.run(args, input=message if platform != "grok" else None,
                                    cwd=work, text=True, capture_output=True, encoding="utf-8",
                                    errors="replace", timeout=480)
        except subprocess.TimeoutExpired:
            return {"platform": platform, "status": "UNVERIFIED", "reason": "CLI timeout after 480 seconds",
                    "install_path": f"{prefix}/skills/ai-delegation-loop", "invocation": call,
                    "interview_prompt_read": False, "answer": None, "other_created_files": None,
                    "skill_trace": []}
        if result.returncode:
            (WORK_ROOT / f"{platform}.error.json").write_text(
                json.dumps({"platform": platform, "exit_code": result.returncode}) + "\n", encoding="utf-8")
            raise RuntimeError(f"{platform} native call failed ({result.returncode}); see error status file")
        events = [json.loads(line) for line in result.stdout.splitlines() if line.startswith("{")]
        # Save observable read calls, never reasoning blocks, signatures, or machine configuration.
        calls, results, model, listed = [], {}, "CLI configured default", False
        for event in events:
            if event.get("subtype") == "init":
                listed = "ai-delegation-loop" in event.get("slash_commands", [])
                model = event.get("model", model)
            message_event = event.get("message", event)
            model = message_event.get("model", model)
            for block in message_event.get("content", []):
                if block.get("type") == "tool_use" and "ai-delegation-loop" in json.dumps(block.get("input", {})):
                    calls.append({"id": block["id"], "tool": block["name"], "input": block["input"]})
                if block.get("type") == "tool_result":
                    results[block["tool_use_id"]] = {"ok": not block.get("is_error", False),
                                                     "excerpt": str(block.get("content", ""))[:160]}
            item = event.get("item", {})
            if event.get("type") == "item.completed" and item.get("type") == "command_execution" and "ai-delegation-loop" in item.get("command", ""):
                calls.append({"id": item["id"], "tool": "command_execution", "input": item["command"]})
                text = item.get("aggregated_output", "")
                results[item["id"]] = {"ok": item.get("exit_code") == 0 and "denied" not in text.lower(), "excerpt": text[:160]}
        matching = [{**call, **results.get(call["id"], {"ok": False})} for call in calls]
        prompt_read = any(c["ok"] and "01-interview.md" in json.dumps(c["input"]) for c in matching)
        if platform == "codex":
            answer = final.read_text(encoding="utf-8")
        else:
            texts = []
            for event in events:
                if event.get("type") == "assistant":
                    message_event = event.get("message", event)
                    texts.extend(block["text"] for block in message_event.get("content", []) if block.get("type") == "text")
                if event.get("type") == "result" and event.get("result"):
                    texts = [event["result"]]
            answer = "\n".join(texts)
        assert answer.strip(), f"{platform} answer not captured"
        created = [p.relative_to(work).as_posix() for p in work.rglob("*") if p.is_file()
                   and not p.is_relative_to(installed) and not p.is_relative_to(work / ".git")
                   and p.name not in {"answer.txt", "prompt.txt"}]
        print(f"{platform} native prompt read: {'PASS' if prompt_read else 'UNVERIFIED'}", flush=True)
        return {"platform": platform, "model": model, "listed_at_start": listed,
                "status": "PASS" if prompt_read and not created else "UNVERIFIED",
                "interview_prompt_read": prompt_read,
                "approval_review": "on-request + auto_review; read-only sandbox" if platform == "codex" else "CLI read tools",
                "install_path": f"{prefix}/skills/ai-delegation-loop",
                "invocation": call, "answer": answer, "other_created_files": created,
                "skill_trace": json.loads(json.dumps(matching, ensure_ascii=False).replace(str(work).replace("\\", "\\\\"), "<temporary-folder>"))}


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(probe, ["codex", "claude", "grok"]))
    OUTPUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert all(not result["other_created_files"] for result in results), "unexpected files created"
    assert all(result["interview_prompt_read"] for result in results), "some interview prompt reads remain unverified"
    for result in results:
        print(f"{result['platform']}: captured answer and {len(result['skill_trace'])} skill trace events", flush=True)
