#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fills the '점검결과' (E) column of check_reconstructed.xlsx from an
OCP-HCK-Score.sh .txt report, matched by checklist item number.

Usage: python3 fill_checklist.py <report.txt> [template.xlsx] [output.xlsx]
  - template.xlsx 생략 시 이 스크립트와 같은 디렉터리의 check_reconstructed.xlsx 사용.
  - output.xlsx 생략 시 report.txt와 같은 이름(.xlsx 확장자)으로 저장.
    예) fill_checklist.py report.txt  ->  report.xlsx

Parsing logic (ITEM_HDR/RESULT_LINE/parse_items, section-2 pipe parsing) is
ported verbatim from the python heredoc embedded in OCP-HCK-Score.sh
(around lines 542-611) — do not re-derive it.
"""
import os
import re
import sys
import unicodedata

import openpyxl

DEFAULT_TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_reconstructed.xlsx")


def _use_utf8_console():
    # Windows 콘솔(cp949 등)에서 ✅/⚠/❌ 같은 이모지 출력 시 UnicodeEncodeError로 죽는 것 방지.
    # 모듈 임포트만으로 호출자의 stdout/stderr를 바꾸지 않도록 main()/self-check 진입 시에만 호출.
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")


DASH = "--------------------------------------------------------"
SEP = "════════════════════════════════════════════════════════"
SEC_RE = re.compile(r"^■ (\d+)\. (.+)$")
ITEM_HDR = re.compile(r"^\[(\d+-\d+(?:-\d+)?)\]\s+(.+)$")
RESULT_LINE = re.compile(r"^\[결과\]\s+(rc=(\d+)|skip|manual)\s*$")
ITEM_NUM_RE = re.compile(r"^\d+-\d+(-\d+)?$")
CO_LINE_RE = re.compile(r"^2-\d+\s*\|")

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
    """Split a section's body into item blocks delimited by DASH/[num] desc/Command.../DASH."""
    items = []
    i = 0
    n = len(body_lines)
    while i < n:
        if body_lines[i] == DASH and i + 1 < n and ITEM_HDR.match(body_lines[i + 1]):
            m = ITEM_HDR.match(body_lines[i + 1])
            num, desc = m.group(1), m.group(2)
            # 헤더 다음 DASH까지를 "Command : ..." 영역으로 건너뛴다 — Command 문자열이
            # 여러 줄로 표시되는 경우에도(item_header의 echo -e 이스케이프 등) 안전하도록
            # 고정 오프셋(옛 i+4) 대신 다음 DASH를 실제로 찾아서 그 뒤부터 본문으로 취급한다.
            k = i + 2
            while k < n and body_lines[k] != DASH:
                k += 1
            j = k + 1
            out = []
            result_tag = None
            while j < n and body_lines[j] != DASH:
                rm = RESULT_LINE.match(body_lines[j])
                if rm:
                    if result_tag is None:
                        result_tag = rm.group(1)
                    else:
                        print("[경고] 항목 %s에 [결과] 마커가 중복 — 첫 번째(%s)만 사용, 두 번째(%s) 무시" %
                              (num, result_tag, rm.group(1)), file=sys.stderr)
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
        elif cur is not None and ln != SEP:
            cur["lines"].append(ln)

    results = {}

    sec2 = next((s for s in sections if s["num"] == "2"), None)
    if sec2:
        for ln in sec2["lines"]:
            if CO_LINE_RE.match(ln):
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


def find_columns(ws):
    """Locates the '번호'/'점검 항목'/'점검결과' columns by header text (row 1) instead of
    assuming fixed positions — a template column insertion must not silently shift which
    column gets overwritten. Returns (num_idx, desc_idx, result_idx), 0-based, or None if
    the header row doesn't have all three."""
    header = {}
    for idx, cell in enumerate(next(ws.iter_rows(min_row=1, max_row=1))):
        v = (cell.value or "").strip() if isinstance(cell.value, str) else cell.value
        if v:
            header[v] = idx
    if "번호" not in header or "점검결과" not in header:
        return None
    return header["번호"], header.get("점검 항목"), header["점검결과"]


def fill_workbook(wb, results, verbose=False):
    """Writes results into each sheet's 점검결과 column. Returns (filled, missing_in_report, summary).

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
        cols = find_columns(ws)
        if cols is None:
            print("[오류] %s: 헤더 행에서 '번호'/'점검결과' 열을 찾을 수 없음 — 스킵" % sheet_name, file=sys.stderr)
            continue
        num_idx, desc_idx, result_idx = cols
        counts = {}
        header_printed = False
        seen = set()
        for row in ws.iter_rows(min_row=2):
            raw_num = row[num_idx].value
            num = raw_num.strip() if isinstance(raw_num, str) else raw_num
            if not isinstance(num, str) or not ITEM_NUM_RE.match(num):
                continue
            if num in seen:
                print("[경고] %s: 항목번호 %s가 템플릿에 중복 — 두 번째 행은 건너뜀" % (sheet_name, num), file=sys.stderr)
                continue
            seen.add(num)
            desc = (row[desc_idx].value or "") if desc_idx is not None else ""
            if num not in results:
                missing.append(num)
                print("[경고] 리포트에서 매칭 실패: %s (%s) %s" % (num, sheet_name, desc), file=sys.stderr)
                continue
            status = results[num]
            target = row[result_idx]
            if isinstance(target, openpyxl.cell.cell.MergedCell):
                missing.append(num)
                print("[오류] %s: %s의 점검결과 셀이 병합되어 있어 쓸 수 없음 — 건너뜀" % (sheet_name, num), file=sys.stderr)
                continue
            target.value = status
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
    _use_utf8_console()
    if len(sys.argv) not in (2, 3, 4):
        print("usage: python3 fill_checklist.py <report.txt> [template.xlsx] [output.xlsx]",
              file=sys.stderr)
        sys.exit(2)
    report_path = sys.argv[1]
    template_path = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_TEMPLATE
    output_path = sys.argv[3] if len(sys.argv) == 4 else (
        os.path.splitext(report_path)[0] + ".xlsx")

    if not os.path.isfile(report_path):
        print("[오류] 리포트를 찾을 수 없음: %s" % report_path, file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(template_path):
        print("[오류] 템플릿을 찾을 수 없음: %s" % template_path, file=sys.stderr)
        sys.exit(1)
    if os.path.abspath(output_path) == os.path.abspath(template_path):
        print("[오류] 출력 경로가 템플릿과 동일함 — 템플릿을 덮어쓰지 않도록 output.xlsx를 다르게 지정할 것: %s"
              % template_path, file=sys.stderr)
        sys.exit(1)

    with open(report_path, encoding="utf-8-sig", errors="replace") as f:
        text = f.read()
    results = parse_report(text)

    wb = openpyxl.load_workbook(template_path)
    filled, missing, summary = fill_workbook(wb, results, verbose=True)
    wb.save(output_path)

    print_summary(summary, filled, missing)
    print("Result > %s" % output_path)
    if missing:
        sys.exit(1)


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
    _use_utf8_console()
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

    ws1.append([" 1-4 ", "d", "c", "s", None, None])  # regression: whitespace around the number must not silently vanish
    ws1.append(["1-1", "dup", "c", "s", None, None])  # regression: duplicate item number must not double-count

    ws4 = wb["4.Network"]
    ws4.append(["4-1", "d", "c", "s", None, None])
    ws4.merge_cells(start_row=2, start_column=4, end_row=2, end_column=5)  # D2:E2 -> E2(점검결과) becomes a MergedCell

    results["2-10"] = "✅ 정상"
    results["1-4"] = "정상"
    results["4-1"] = "정상"
    filled, missing, summary = fill_workbook(wb, results)
    assert any(name == "2.ClusterOperator" for name, _ in summary), summary
    assert ws1["E2"].value == "정상"
    assert ws1["E3"].value == "확인필요"
    assert "1-3" in missing
    assert ws3["A2"].value.startswith("3-1.") and ws3["E2"].value is None
    assert ws3["E3"].value == "정상"
    assert ws2["E2"].value == "✅ 정상", "two-digit item number (2-10) not matched by ITEM_NUM_RE"
    assert ws1["E5"].value == "정상", "whitespace-padded item number was silently dropped"
    assert filled.count("1-1") == 1, "duplicate item number was double-counted: %r" % filled
    assert "4-1" in missing, "merged 점검결과 cell should be reported, not silently skipped"

    # 헤더에 '번호'/'점검결과'가 없는 시트는 즉시 실패 보고하고 계속 진행해야 한다(크래시 금지).
    wb_bad = openpyxl.Workbook()
    wb_bad.remove(wb_bad.active)
    ws_bad = wb_bad.create_sheet("1.Cluster구성")
    ws_bad.append(["No", "Item", "Cmd", "Criteria", "Result", "Note"])  # 헤더 텍스트가 다름
    ws_bad.append(["1-1", "d", "c", "s", None, None])
    filled_bad, missing_bad, summary_bad = fill_workbook(wb_bad, results)
    assert filled_bad == [] and summary_bad == [], "헤더를 못 찾으면 아무것도 채우면 안 됨"

    print("self-check OK: filled=%d missing=%s" % (len(filled), missing))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-check":
        _self_check()
    else:
        main()
