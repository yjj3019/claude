#!/usr/bin/env python3
"""Validate the ai-delegation-loop skill package.

Standard library only, Python 3.9+. PyYAML, when installed, cross-checks the
built-in frontmatter parser. Exit status is 1 when any check fails.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

SKILL = "ai-delegation-loop"
# The only frontmatter keys accepted by every surface; claude.ai uploads reject the rest.
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
OPENAI_SECTIONS = {
    "interface": {"display_name", "short_description", "default_prompt",
                  "icon_small", "icon_large", "brand_color"},
    "policy": {"allow_implicit_invocation"},
}
SKIP_PARTS = {".git", "dist", "__pycache__", ".simulation", "sim", "simulation-results"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FENCE_RE = re.compile(r"^(```|~~~)")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
LEAK_PATTERNS = [
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
    ("API secret key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("Windows user path", re.compile(r"[A-Za-z]:\\+Users\\+[A-Za-z0-9_.-]+")),
    ("POSIX home path", re.compile(r"/(?:home|Users)/[A-Za-z][A-Za-z0-9_.-]*/")),
    ("email address", re.compile(r"(?<![A-Za-z0-9._%+-])(?!noreply@)[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}")),
]
TEXT_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".toml"}

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")


class FrontmatterError(Exception):
    pass


def read_text(path):
    return path.read_text(encoding="utf-8")


def normalized_sha256(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def project_files(root):
    scopes = [root / "skills" / SKILL, root / "scripts" / "delegation",
              root / "docs" / "delegation-loop", root / ".github" / "workflows" / "delegation.yml"]
    paths = [p for scope in scopes for p in ([scope] if scope.is_file() else scope.rglob("*"))]
    for path in sorted(paths, key=lambda p: p.as_posix()):
        rel = path.relative_to(root)
        if path.is_file() and not any(part in SKIP_PARTS for part in rel.parts):
            yield path


def split_frontmatter(text):
    lines = text.replace("\r\n", "\n").split("\n")
    if lines[0].rstrip() != "---":
        raise FrontmatterError("file must start with '---' on line 1")
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            return lines[1:index]
    raise FrontmatterError("closing '---' not found")


def scalar(raw, where, string_only=False):
    raw = raw.strip()
    if not raw:
        raise FrontmatterError("%s: empty value" % where)
    if raw[0] in "\"'":
        quote = raw[0]
        if len(raw) < 2 or raw[-1] != quote:
            raise FrontmatterError("%s: unterminated quote" % where)
        body = raw[1:-1]
        if quote == "'":
            if "'" in body.replace("''", ""):
                raise FrontmatterError("%s: unescaped single quote" % where)
            return body.replace("''", "'")
        out, index = [], 0
        while index < len(body):
            char = body[index]
            if char == "\\":
                if index + 1 >= len(body) or body[index + 1] not in "\"\\":
                    raise FrontmatterError("%s: unsupported escape sequence" % where)
                out.append(body[index + 1])
                index += 2
                continue
            if char == '"':
                raise FrontmatterError("%s: unescaped double quote" % where)
            out.append(char)
            index += 1
        return "".join(out)
    if raw[0] in "[{&*!|>%@`" or raw.startswith("- "):
        raise FrontmatterError("%s: unsupported YAML construct; use a quoted single-line string" % where)
    if ": " in raw or " #" in raw or raw.endswith(":"):
        raise FrontmatterError("%s: unquoted value contains ': ' or ' #', which breaks YAML; quote it" % where)
    if string_only and re.match(r"^(true|false|null|yes|no|on|off|~|[-+]?[0-9][0-9._]*([eE][-+]?[0-9]+)?)$", raw, re.I):
        raise FrontmatterError("%s: value would parse as a non-string; quote it" % where)
    return raw


def parse_mapping(lines):
    data, index = {}, 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if "\t" in line:
            raise FrontmatterError("line %d contains a tab" % (index + 1))
        if line[0] == " ":
            raise FrontmatterError("line %d: unexpected indentation" % (index + 1))
        match = re.match(r"^([A-Za-z0-9_-]+):(?:[ ]+(.*))?$", line)
        if not match:
            raise FrontmatterError("line %d is not 'key: value'" % (index + 1))
        key, rest = match.group(1), match.group(2)
        if key in data:
            raise FrontmatterError("duplicate key %s" % key)
        if rest is None or not rest.strip():
            nested, cursor = {}, index + 1
            while cursor < len(lines) and (lines[cursor].startswith("  ") or not lines[cursor].strip()):
                if lines[cursor].strip():
                    sub = re.match(r"^  ([A-Za-z0-9_-]+):[ ]+(.*)$", lines[cursor])
                    if not sub:
                        raise FrontmatterError("line %d: nested entries must be '  key: value'" % (cursor + 1))
                    nested[sub.group(1)] = scalar(sub.group(2), "%s.%s" % (key, sub.group(1)), string_only=True)
                cursor += 1
            if not nested:
                raise FrontmatterError("key %s has no value" % key)
            data[key] = nested
            index = cursor
        else:
            data[key] = scalar(rest, key)
            index += 1
    return data


def parse_frontmatter(text):
    lines = split_frontmatter(text)
    data = parse_mapping(lines)
    try:
        import yaml  # optional cross-check
    except ImportError:
        return data
    loaded = yaml.safe_load("\n".join(lines))
    if loaded != data:
        raise FrontmatterError("built-in parser and PyYAML disagree: %r vs %r" % (data, loaded))
    return data


def check_skill_md(path, require_dir_name):
    problems = []
    try:
        data = parse_frontmatter(read_text(path))
    except FrontmatterError as error:
        return ["%s: %s" % (path.name, error)]
    unknown = sorted(set(data) - ALLOWED_KEYS)
    if unknown:
        problems.append("%s: unsupported frontmatter keys %s (claude.ai upload rejects them)"
                        % (path.name, ", ".join(unknown)))
    name, description = data.get("name"), data.get("description")
    if not isinstance(name, str) or not name:
        problems.append("%s: name is required" % path.name)
    else:
        if len(name) > 64 or not NAME_RE.match(name):
            problems.append("%s: name %r must be 1-64 lowercase letters, digits and single hyphens" % (path.name, name))
        if require_dir_name and name != path.parent.name:
            problems.append("%s: name %r must equal the folder name %r" % (path.name, name, path.parent.name))
    if not isinstance(description, str) or not description.strip():
        problems.append("%s: description is required" % path.name)
    elif len(description) > 1024:
        problems.append("%s: description is %d characters; the limit is 1024" % (path.name, len(description)))
    compat = data.get("compatibility")
    if compat is not None and (not isinstance(compat, str) or len(compat) > 500):
        problems.append("%s: compatibility must be a string of at most 500 characters" % path.name)
    if "metadata" in data and not isinstance(data["metadata"], dict):
        problems.append("%s: metadata must be a map of strings" % path.name)
    return problems


def check_frontmatter(root):
    skill = root / "skills" / SKILL / "SKILL.md"
    template = root / "skills" / SKILL / "templates" / "job-playbook" / "SKILL.template.md"
    problems = []
    for path, need_dir in ((skill, True), (template, False)):
        if not path.is_file():
            problems.append("missing %s" % path.relative_to(root).as_posix())
        else:
            problems.extend(check_skill_md(path, need_dir))
    return problems


def check_size(root):
    skill = root / "skills" / SKILL / "SKILL.md"
    if not skill.is_file():
        return ["SKILL.md is missing"]
    count = len(read_text(skill).splitlines())
    return ["SKILL.md has %d lines; keep it under 500" % count] if count >= 500 else []


def strip_code(text):
    out, fenced = [], False
    for line in text.replace("\r\n", "\n").split("\n"):
        if FENCE_RE.match(line.strip()):
            fenced = not fenced
            continue
        if not fenced:
            out.append(re.sub(r"`[^`]*`", "", line))
    return out


def slug(heading):
    heading = re.sub(r"`([^`]*)`", r"\1", heading)
    heading = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    heading = heading.replace("*", "").lower()
    kept = "".join(ch for ch in heading if ch.isalnum() or ch in " -_")
    return kept.replace(" ", "-")


def anchors_of(path, cache):
    if path not in cache:
        seen, found = {}, set()
        for line in strip_code(read_text(path)):
            match = HEADING_RE.match(line)
            if match:
                base = slug(match.group(1))
                count = seen.get(base, 0)
                seen[base] = count + 1
                found.add(base if count == 0 else "%s-%d" % (base, count))
        cache[path] = found
    return cache[path]


def check_links(root):
    problems, cache = [], {}
    docs = [p for p in project_files(root) if p.suffix == ".md"]
    for doc in docs:
        for line in strip_code(read_text(doc)):
            for href in LINK_RE.findall(line):
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href):
                    continue
                target, _, anchor = href.partition("#")
                resolved = doc if not target else (doc.parent / unquote(target)).resolve()
                shown = doc.relative_to(root).as_posix()
                if not resolved.exists():
                    problems.append("%s: broken link %s" % (shown, href))
                elif anchor and resolved.suffix == ".md":
                    if unquote(anchor).lower() not in anchors_of(resolved, cache):
                        problems.append("%s: broken anchor %s" % (shown, href))
    return problems


def check_json(root):
    problems = []
    for path in project_files(root):
        if path.suffix != ".json":
            continue
        try:
            json.loads(read_text(path))
        except ValueError as error:
            problems.append("%s: invalid JSON (%s)" % (path.relative_to(root).as_posix(), error))
    cases_path = root / "skills" / SKILL / "tests" / "simulation-cases.json"
    if cases_path.is_file():
        try:
            cases = json.loads(read_text(cases_path))
        except ValueError:
            return problems
        ids = [case.get("id") for case in cases]
        if len(ids) != len(set(ids)):
            problems.append("simulation-cases.json: duplicate ids")
        for case in cases:
            if case.get("expected") not in case.get("choices", []):
                problems.append("simulation-cases.json: %s expected value is not among its choices" % case.get("id"))
    return problems


def check_evidence(root):
    tests = root / "skills" / SKILL / "tests"
    results = tests / "simulation-results.json"
    if not results.is_file():
        return ["simulation-results.json is missing"]
    try:
        rounds = json.loads(read_text(results)).get("rounds", [])
    except ValueError:
        return ["simulation-results.json is invalid"]
    frozen = [r["data"] for r in rounds if "reference_sha256" in r.get("data", {})]
    if not frozen:
        return ["no round with reference_sha256 found in simulation-results.json"]
    data, problems = frozen[-1], []
    base = root / "skills" / SKILL
    status_path = tests / "evidence-status.json"
    if status_path.is_file():
        try:
            status = json.loads(read_text(status_path))
            history = status["historical"]
            if (history["status"] != "STALE_FOR_CURRENT_PACKAGE" or history["package_version"] != "1.2"
                    or history["reference_sha256"] != data["reference_sha256"]
                    or history["cases_sha256"] != data["cases_sha256"]):
                problems.append("historical evidence status/version/frozen hashes differ")
            expected_paths = {"tests/simulation-results.json", "tests/native-probe-results.json",
                              "tests/simulation-report.v1.2.ko.md"}
            if set(history["artifact_sha256"]) != expected_paths:
                problems.append("historical artifact inventory differs")
            for name, recorded in history["artifact_sha256"].items():
                if name not in expected_paths or not (base / name).is_file():
                    problems.append("historical artifact missing or unsupported")
                elif hashlib.sha256((base / name).read_bytes()).hexdigest() != recorded:
                    problems.append(name + " historical bytes changed")
            archive_path = root / "docs/delegation-loop/source-history/manifest.json"
            archive = json.loads(read_text(archive_path))
            originals = {entry["path"]: entry["sha256"] for entry in
                         archive["files"]["refs/remotes/origin/optimize/three-platforms"]}
            for name in expected_paths:
                original = name.replace("simulation-report.v1.2.ko.md", "simulation-report.ko.md")
                if history["artifact_sha256"].get(name) != originals["skills/" + SKILL + "/" + original]:
                    problems.append(name + " differs from archived source hash")
            report = read_text(tests / "simulation-report.ko.md")
            for marker in ("HISTORICAL", "STALE_FOR_CURRENT_PACKAGE", "UNVERIFIED"):
                if marker not in report:
                    problems.append("current report must declare " + marker)
        except (ValueError, KeyError, TypeError, OSError) as error:
            return ["invalid historical evidence declaration: " + str(error)]
        return problems
    for name, recorded in sorted(data["reference_sha256"].items()):
        path = base / name
        if not path.is_file() or normalized_sha256(path) != recorded:
            problems.append("%s changed since the recorded simulation run" % name)
    cases = tests / "simulation-cases.json"
    if normalized_sha256(cases) != data.get("cases_sha256"):
        problems.append("tests/simulation-cases.json changed since the recorded simulation run")
    if problems:
        problems.append("re-run run_simulation.py and update the report, or state in the report that the "
                        "evidence predates this change and pass --allow-stale-evidence")
    return problems


def check_current_evidence(root):
    base = root / "skills" / SKILL
    status_path = base / "tests/evidence-status.json"
    if not status_path.is_file():
        return ["current evidence status is missing"]
    problems = []
    try:
        status = json.loads(read_text(status_path))
        version = parse_frontmatter(read_text(base / "SKILL.md"))["metadata"]["version"]
        current = status["current"]
        if status.get("schema") != 1 or status["package_version"] != version or current["model_behavior"] != "UNVERIFIED" or current["model_cli_executed"] is not False:
            problems.append("current version/model evidence declaration is inaccurate")
        if current["acceptance_results"] != "tests/acceptance-results.json":
            return ["unsupported acceptance results path"]
        results_path = base / current["acceptance_results"]
        if hashlib.sha256(results_path.read_bytes()).hexdigest() != current["acceptance_results_sha256"]:
            problems.append("current acceptance result bytes changed")
        result = json.loads(read_text(results_path))
        if result.get("schema") != 1 or result["package_version"] != version or result["model_behavior"] != "UNVERIFIED" or result["model_cli_executed"] is not False:
            problems.append("acceptance result claims wrong version or model execution")
        if result.get("level") != "L3" or result.get("scope") != "Static prompt contracts, isolated playbook format fixtures and oracle grader self-check; not model behavior":
            problems.append("acceptance result overclaims deterministic verification scope")
        expected_refs = {"SKILL.md", "manual.ko.md"} | {p.relative_to(base).as_posix() for p in (base / "prompts").glob("*.md")}
        if set(result["reference_sha256"]) != expected_refs:
            problems.append("current reference inventory differs")
        for name, recorded in result["reference_sha256"].items():
            if name not in expected_refs or normalized_sha256(base / name) != recorded:
                problems.append(name + " changed since current acceptance checks")
        if normalized_sha256(base / "tests/simulation-cases.json") != result["cases_sha256"]:
            problems.append("current simulation cases changed")
        allowed_inputs = {"templates/job-playbook/SKILL.template.md", "tests/acceptance-cases.md"}
        allowed_runners = {"scripts/delegation/test_prompt_contract.py", "scripts/delegation/refresh_evidence.py",
                           "scripts/delegation/validate_skill.py",
                           "skills/ai-delegation-loop/tests/run_simulation.py"}
        for field, allowed, prefix in (("input_sha256", allowed_inputs, base), ("runner_sha256", allowed_runners, root)):
            if set(result[field]) != allowed:
                problems.append(field + " inventory differs")
            for name, recorded in result[field].items():
                if name not in allowed or normalized_sha256(prefix / name) != recorded:
                    problems.append(name + " changed since current acceptance checks")
        required_checks = {"A16-frontmatter-fallback", "A17-proof-before-rerun", "A18-new-action-approval",
                           "A19-durable-protocol", "A20-multiple-and-external-causes", "oracle-grader-self-check"}
        if set(result["checks"]) != required_checks or set(result["checks"].values()) != {"PASS"}:
            problems.append("current acceptance checks missing or failed")
    except (ValueError, KeyError, TypeError, OSError, FrontmatterError) as error:
        problems.append("invalid current evidence: " + str(error))
    return problems


def check_version(root):
    skill = root / "skills" / SKILL / "SKILL.md"
    try:
        version = parse_mapping(split_frontmatter(read_text(skill))).get("metadata", {}).get("version")
    except FrontmatterError:
        return ["cannot read SKILL.md version"]
    if not version:
        return ["SKILL.md metadata.version is missing"]
    marker, problems = "v%s" % version, []
    readme = read_text(root / "skills" / SKILL / "README.md")
    manual_head = read_text(root / "skills" / SKILL / "manual.ko.md").splitlines()[0]
    if marker not in readme:
        problems.append("README.md does not mention %s" % marker)
    if marker not in manual_head:
        problems.append("manual.ko.md title does not mention %s" % marker)
    return problems


def check_leaks(root):
    problems = []
    for path in project_files(root):
        if path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            problems.append("%s: not valid UTF-8" % path.relative_to(root).as_posix())
            continue
        for label, pattern in LEAK_PATTERNS:
            if pattern.search(text):
                problems.append("%s: looks like a %s" % (path.relative_to(root).as_posix(), label))
    return problems


def check_openai_yaml(root):
    path = root / "skills" / SKILL / "agents" / "openai.yaml"
    if not path.is_file():
        return []
    try:
        data = parse_mapping(read_text(path).replace("\r\n", "\n").split("\n"))
    except FrontmatterError as error:
        return ["agents/openai.yaml: %s" % error]
    problems = []
    for section, body in data.items():
        if section not in OPENAI_SECTIONS or not isinstance(body, dict):
            problems.append("agents/openai.yaml: unknown or malformed section %s" % section)
            continue
        extra = sorted(set(body) - OPENAI_SECTIONS[section])
        if extra:
            problems.append("agents/openai.yaml: unknown keys under %s: %s" % (section, ", ".join(extra)))
    return problems


def check_agent_files(root):
    problems = []
    if not (root / "AGENTS.md").is_file():
        problems.append("AGENTS.md is missing")
    claude = root / "CLAUDE.md"
    if not claude.is_file():
        problems.append("CLAUDE.md is missing")
    # Root FEF entry points have their own validator and generated Kernel.
    # Do not impose the source repository's single-line import contract here.
    return problems


CHECKS = [
    ("frontmatter", check_frontmatter),
    ("skill-size", check_size),
    ("links", check_links),
    ("json", check_json),
    ("evidence", check_evidence),
    ("current-evidence", check_current_evidence),
    ("version", check_version),
    ("leaks", check_leaks),
    ("openai-yaml", check_openai_yaml),
    ("agent-files", check_agent_files),
]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the %s package." % SKILL)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--allow-stale-evidence", action="store_true",
                        help="report stale simulation evidence as a warning instead of a failure")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    failed = False
    for name, check in CHECKS:
        problems = check(root)
        if not problems:
            print("PASS %s" % name)
            continue
        if name == "evidence" and args.allow_stale_evidence and not (root / "skills" / SKILL / "tests/evidence-status.json").exists():
            print("WARN %s" % name)
        else:
            print("FAIL %s" % name)
            failed = True
        for problem in problems:
            print("  - %s" % problem)
    print("validation failed" if failed else "validation passed")
    if (root / "skills" / SKILL / "tests/evidence-status.json").is_file():
        print("Model evidence: v1.2 HISTORICAL/STALE_FOR_CURRENT_PACKAGE; current model behavior UNVERIFIED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
