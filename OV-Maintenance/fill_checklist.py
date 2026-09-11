#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fills the '점검결과' (E) column of check_reconstructed.xlsx from an
OCP-HCK-Score.sh .txt report, matched by checklist item number.

Usage: python3 fill_checklist.py <report.txt> <template.xlsx> [output.xlsx]

Parsing logic (ITEM_HDR/RESULT_LINE/parse_items, section-2 pipe parsing) is
ported verbatim from the python heredoc embedded in OCP-HCK-Score.sh
(around lines 542-611) — do not re-derive it.
"""
import re
import sys
import unicodedata
from datetime import datetime

import openpyxl

# Windows 콘솔(cp949 등)에서 ✅/⚠/❌ 같은 이모지 출력 시 UnicodeEncodeError로 죽는 것 방지.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

DASH = "--------------------------------------------------------"
SEC_RE = re.compile(r"^■ (\d+)\. (.+)$")
ITEM_HDR = re.compile(r"^\[([0-9]-[0-9](?:-[0-9])?)\]\s+(.+)$")
RESULT_LINE = re.compile(r"^\[결과\]\s+(rc=(\d+)|skip|manual)\s*$")
ITEM_NUM_RE = re.compile(r"^\d+-\d+(-\d+)?$")

STATUS_MAP = {"ok": "정상", "attention": "확인필요", "skip": "건너뜀", "manual": "수동확인"}

SHEET_BY_SECTION = {
    "1": "1.Cluster구성",
    "2": "2.ClusterOperator",
    "3": "3.API연동",
    "4": "4.Network",
    "5": "5.Virtualization",
}

# OCP-HCK-Score.sh(33행)의 색상 팔레트와 동일 — 리포트와 브리핑 출력의 시각 언어를 통일.
RED, GREEN, YELLOW, BLUE, DIM, BOLD, NC = (
    "\033[0;31m", "\033[0;32m", "\033[1;33m", "\033[0;34m", "\033[2m", "\033[1m", "\033[0m")
_USE_COLOR = sys.stdout.isatty()


def _color(text, code):
    return "%s%s%s" % (code, text, NC) if _USE_COLOR else text


def display_width(text):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def pad_display(text, width):
    """Right-pads text to `width` display columns (CJK-aware, unlike '%-Ns')."""
    return text + " " * max(0, width - display_width(text))


def truncate_display(text, width):
    out = ""
    w = 0
    for c in text:
        cw = 2 if unicodedata.east_asian_width(c) in "WF" else 1
        if w + cw > width:
            return out + "…"
        out += c
        w += cw
    return out


def status_color(status_text):
    if "이상" in status_text or "실패" in status_text:
        return RED
    if "확인필요" in status_text or "주의" in status_text:
        return YELLOW
    if "정상" in status_text:
        return GREEN
    return BLUE  # 건너뜀 / 수동확인 / 기타


def skip_or_attention(body):
    if "건너뜀" in body:
        return "skip"
    if re.search(r"\berror:|Error from server|unauthorized|command not found|no such", body, re.I):
        return "attention"
    return "ok"


def parse_items(body_lines):
    """Split a section's body into item blocks delimited by DASH/[num] desc/Command/DASH."""
    items = []
    i = 0
    n = len(body_lines)
    while i < n:
        if body_lines[i] == DASH and i + 3 < n and ITEM_HDR.match(body_lines[i + 1]):
            m = ITEM_HDR.match(body_lines[i + 1])
            num, desc = m.group(1), m.group(2)
            j = i + 4
            out = []
            result_tag = None
            while j < n and body_lines[j] != DASH:
                rm = RESULT_LINE.match(body_lines[j])
                if rm and result_tag is None:
                    result_tag = rm.group(1)
                else:
                    out.append(body_lines[j])
                j += 1
            body_text = "\n".join(out).strip("\n")
            if result_tag == "skip":
                status = "skip"
            elif result_tag == "manual":
                status = "manual"
            elif result_tag is not None:
                status = "ok" if result_tag.split("=", 1)[1] == "0" else "attention"
            else:
                status = skip_or_attention(body_text)
            items.append({"num": num, "desc": desc, "status": status})
            i = j
        else:
            i += 1
    return items


def parse_report(text):
    """Returns {item_num: result_text} across all 5 sections."""
    lines = text.split("\n")
    sections = []
    cur = None
    for ln in lines:
        m = SEC_RE.match(ln)
        if m:
            cur = {"num": m.group(1), "lines": []}
            sections.append(cur)
        elif cur is not None and not ln.startswith("════"):
            cur["lines"].append(ln)

    results = {}

    sec2 = next((s for s in sections if s["num"] == "2"), None)
    if sec2:
        for ln in sec2["lines"]:
            if ln.startswith("2-") and "|" in ln:
                parts = [p.strip() for p in ln.split("|")]
                if len(parts) >= 6:
                    results[parts[0]] = parts[5]
                else:
                    results[parts[0]] = "[jq 없음 - 원본 확인]"

    for sec_num in ("1", "3", "4", "5"):
        sec = next((s for s in sections if s["num"] == sec_num), None)
        if not sec:
            continue
        for it in parse_items(sec["lines"]):
            results[it["num"]] = STATUS_MAP.get(it["status"], it["status"])

    return results


def fill_workbook(wb, results, verbose=False):
    """Writes results into each sheet's E column. Returns (filled, missing_in_report, summary).

    summary: [(sheet_name, {status_text: count})] in sheet order, for the closing table.
    """
    filled = []
    missing = []
    summary = []
    for sec_num, sheet_name in SHEET_BY_SECTION.items():
        if sheet_name not in wb.sheetnames:
            print("[경고] 시트 없음: %s" % sheet_name, file=sys.stderr)
            continue
        ws = wb[sheet_name]
        counts = {}
        header_printed = False
        for row in ws.iter_rows(min_row=2):
            num = row[0].value
            if not isinstance(num, str) or not ITEM_NUM_RE.match(num):
                continue
            desc = row[1].value or ""
            if num not in results:
                missing.append(num)
                print("[경고] 리포트에서 매칭 실패: %s (%s) %s" % (num, sheet_name, desc), file=sys.stderr)
                continue
            status = results[num]
            row[4].value = status
            filled.append(num)
            counts[status] = counts.get(status, 0) + 1
            if verbose:
                if not header_printed:
                    print(_color("\n■ %s" % sheet_name, BOLD + BLUE))
                    header_printed = True
                short_desc = truncate_display(desc, 44)
                print("  %s %s %s" % (
                    pad_display(num, 8), pad_display(short_desc, 46), _color(status, status_color(status))))
        if counts:
            summary.append((sheet_name, counts))
    return filled, missing, summary


def print_summary(summary, filled, missing):
    print(_color("\n■ 요약", BOLD))
    all_statuses = []
    for _, counts in summary:
        for s in counts:
            if s not in all_statuses:
                all_statuses.append(s)
    for sheet_name, counts in summary:
        parts = ["%s %d" % (_color(s, status_color(s)), n) for s, n in counts.items()]
        print("  %s %s" % (pad_display(sheet_name, 20), "  ".join(parts)))
    print("  " + "-" * 40)
    print("  총 %d개 채움, %d개 리포트 매칭 실패" % (len(filled), len(missing)))


def main():
    if len(sys.argv) not in (3, 4):
        print("usage: python3 fill_checklist.py <report.txt> <template.xlsx> [output.xlsx]",
              file=sys.stderr)
        sys.exit(2)
    report_path, template_path = sys.argv[1], sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) == 4 else (
        "checklist_filled_%s.xlsx" % datetime.now().strftime("%Y%m%d-%H%M"))

    with open(report_path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    results = parse_report(text)

    wb = openpyxl.load_workbook(template_path)
    filled, missing, summary = fill_workbook(wb, results, verbose=True)
    wb.save(output_path)

    print_summary(summary, filled, missing)
    print("  -> %s" % output_path)


SAMPLE_REPORT = """점검 대상 클러스터 : https://api.example:6443
점검 수행 계정     : kubeadmin
점검 시작 시각     : Fri Sep 11 09:00:00 KST 2026

════════════════════════════════════════════════════════
■ 1. Cluster 구성 확인
════════════════════════════════════════════════════════

--------------------------------------------------------
[1-1] Node Join 상태 확인
Command : oc get nodes
--------------------------------------------------------
[결과] rc=0
NAME   STATUS   ROLES
node1  Ready    master

--------------------------------------------------------
[1-2] 전체 Node Role 확인
Command : oc get nodes
--------------------------------------------------------
[결과] rc=1
error: some failure

════════════════════════════════════════════════════════
■ 2. Cluster Operator 상태 확인
════════════════════════════════════════════════════════

번호 | Operator | AVAILABLE | PROGRESSING | DEGRADED | 판정
--------------------------------------------------------------
2-1 | authentication | True | False | False | ✅ 정상
2-2 | baremetal | True | True | False | ⚠ 주의(Progressing)

════════════════════════════════════════════════════════
■ 3. API 연동 확인
════════════════════════════════════════════════════════

--------------------------------------------------------
[3-1-1] Namespace 목록 조회
Command : oc get ns
--------------------------------------------------------
[결과] rc=0
NAME   STATUS
default Active

════════════════════════════════════════════════════════
■ 4. Network 확인
════════════════════════════════════════════════════════

--------------------------------------------------------
[4-1] Node 인터페이스 확인
Command : oc debug node/n1
--------------------------------------------------------
[결과] skip
virtctl 미설치로 건너뜀

════════════════════════════════════════════════════════
■ 5. Virtualization 확인
════════════════════════════════════════════════════════

--------------------------------------------------------
[5-3] VM Console 접속 확인
Command : virtctl console vm1
--------------------------------------------------------
[결과] manual
수동 확인 필요

════════════════════════════════════════════════════════
점검 종료 시각 : Fri Sep 11 09:10:00 KST 2026
════════════════════════════════════════════════════════
"""


def _self_check():
    results = parse_report(SAMPLE_REPORT)
    assert results["1-1"] == "정상", results
    assert results["1-2"] == "확인필요", results
    assert results["2-1"] == "✅ 정상", results
    assert results["2-2"] == "⚠ 주의(Progressing)", results
    assert results["3-1-1"] == "정상", results
    assert results["4-1"] == "건너뜀", results
    assert results["5-3"] == "수동확인", results
    assert "1-3" not in results

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for sec_num, sheet_name in SHEET_BY_SECTION.items():
        ws = wb.create_sheet(sheet_name)
        ws.append(["번호", "점검 항목", "Command", "정상 판정 기준", "점검결과", "비고"])
    ws1 = wb["1.Cluster구성"]
    ws1.append(["1-1", "d", "c", "s", None, None])
    ws1.append(["1-2", "d", "c", "s", None, None])
    ws1.append(["1-3", "d", "c", "s", None, None])
    ws3 = wb["3.API연동"]
    ws3.append(["3-1. 배너 행", None, None, None, None, None])
    ws3.append(["3-1-1", "d", "c", "s", None, None])
    ws2 = wb["2.ClusterOperator"]
    ws2.append(["2-10", "d", "c", "s", None, None])  # regression: two-digit numbers (2-10..2-32) must still match

    results["2-10"] = "✅ 정상"
    filled, missing, summary = fill_workbook(wb, results)
    assert any(name == "2.ClusterOperator" for name, _ in summary), summary
    assert ws1["E2"].value == "정상"
    assert ws1["E3"].value == "확인필요"
    assert "1-3" in missing
    assert ws3["A2"].value.startswith("3-1.") and ws3["E2"].value is None
    assert ws3["E3"].value == "정상"
    assert ws2["E2"].value == "✅ 정상", "two-digit item number (2-10) not matched by ITEM_NUM_RE"
    print("self-check OK: filled=%d missing=%s" % (len(filled), missing))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-check":
        _self_check()
    else:
        main()
