# Precise Post-Merge Analysis — Claude FEF / Prompt Pack

**Repo:** `/workspace/claude` @ `1ecaa7b` (`Merge pull request #17 from yjj3019/fix/sim-10-claude-optimize`)  
**Date:** 2026-09-06 (KST / UTC+9)  
**Scope:** Post-merge analysis artifact (findings F-01–F-12). Fixes land on `fix/adaptive-map-align`.

**Validation run (this checkout):**
- `sync_kernel.py --check` → pass
- `validate_framework.py` → pass
- `validate_routes.py` → pass (10 routes)
- `measure_load.py` → Kernel entry **6980 B** (~1745 tok); anti-pattern full dump **~149446 B** (~8.8× heaviest route)
- `unittest discover` → **76 OK**
- Adaptive scenario sims (classify_tier) → **10/10 PASS** on happy-path; edge cases expose underspec (below)

---

## 1. Executive Summary (요약)

- **Cold-start 목표 달성:** `CLAUDE.md` = **6980 / 7000 B** (여유 **20 B**); Latency Contract + Adaptive pointer가 entry에 존재하고, simple Q&A는 `kernel_only_safe=true`로 남음.
- **PR #17 구조 이슈(sim-10 P0/P1)는 대체로 해결:** install_pack, Model-Invariant Floor, Fable 5.1 notes, Context Budget, measure_load, fence-aware sections, README.ko — mechanical PASS.
- **신규 핵심 모순 (P0):** Adaptive Effort **L1 로드 캡**(module≤1, workflow/reviewer/policy=0)과 `loading-map` / `routes.json`의 **코딩·리서치 등 실질 루트**가 충돌 — 샘플 10 루트 중 **6/10**이 `validate_pack_load(L1, …)` FAIL. 모델은 Sonnet(L1)인데 팩은 L2급.
- **Haiku 게이트 문서 드리프트 (P1):** Adaptive/roster는 “Haiku = light Notion/docs only”, 그러나 `docs/model-usage.md` Haiku Runtime Notes는 extraction/classification/routing/brief summaries 등 **넓은 Haiku 사용**을 계속 권장 → 런타임 over-route 또는 under-route 혼란.
- **Enforceability 구멍 (P1):** `adaptive_effort.validate_pack_load` / `classify_tier`가 `detect_task`·`validate_routes`·`validate_framework`에 **미연결**. Adaptive validator는 **문구 존재 검사만** → false green 가능.
- **sim-10 리포트 stale (P1):** SIM-01이 여전히 “Haiku fast path”를 서술 — #17의 Sonnet-default 개정과 불일치.
- **Floor 긴장 (P1/P2):** Model-Invariant Floor는 “모델이 팩 선택을 바꾸지 않음”인데 Adaptive L0/L1은 맵보다 **더 빡센 캡**을 둠 — 해석 규칙이 문서에 명시되지 않음.
- **CI:** `validate_repository` → `validate_framework`는 간접 포함. **`measure_load` / `sync_kernel --check` 단독 스텝 없음** (다만 inlined-kernel sync는 validate_framework가 검사).

---

## 2. Strengths post-#17 (강점)

| Area | Evidence |
|---|---|
| Cold-start budget | `CLAUDE.md` 6980 B ≤ `MAX_CLAUDE_ENTRY_BYTES=7000`; `measure_load` / `test_latency_lightness` 일치 |
| Latency Contract | Entry에 “Latency > completeness…”, heavy paths Task Map/routes 제외 (`HEAVY_NON_DEFAULT_PATHS`) |
| Adaptive 문서 골격 | `docs/adaptive-effort.md` L0–L3, unsure→Sonnet, Haiku narrow gate; CLAUDE/AGENTS/model-usage 포인터 |
| Model roster + floor | Opus 5 (1M) / Fable 5.1 / Sonnet 5 / Haiku 4.5; escalate≠expand 문구 검증됨 |
| Install path | `install_pack.py --auto` + unittest; docs/scripts/config 포함 |
| Mechanical tooling | fence-aware `markdown_sections`; `measure_load` anti-pattern ratio ~8.8× |
| Unit coverage growth | `test_adaptive_effort`, `test_latency_lightness`, `test_install_pack` 등 76 tests green |
| Pack-light entry behavior | `detect_task("What is Kubernetes?")` → `kernel_only_safe=true`, unmapped |

---

## 3. Findings Table

| ID | Severity | Area | Evidence | Impact | Recommended fix (one-liner) |
|---|---|---|---|---|---|
| F-01 | **P0** | Adaptive vs Load Map | Coding/research/manual/prompt/blog/security sample asks → `classify_tier=L1` but route packs violate L1 caps (`workflows/reviewers/policies > 0`); **6/10 routes** fail `validate_pack_load` | Agents pick Sonnet + still dump full CodingWorkflow+policies, or skip integrity policies to “obey” L1 — either over-load or under-policy | Define L1 as **model tier**; pack load still follows loading-map when `kernel_only_safe=false` (or bump mapped substantial tasks to L2) |
| F-02 | **P1** | Haiku doc drift | Adaptive: “Haiku only light Notion/docs”; `model-usage` Haiku Notes: extraction, classification, routing, template filling, **brief summaries**, lightweight subtasks | Hosts following Notes over-route Q&A/summaries to Haiku against user preference | Rewrite Haiku Notes to defer to Adaptive gate; move extraction/summary to Sonnet (L1) |
| F-03 | **P1** | Enforceability / false green | `validate_adaptive_effort` = phrase checks only; no `classify_tier`/`validate_pack_load` import; `routing.py` has **zero** adaptive mentions | CI green while F-01 contradiction persists | Wire `validate_pack_load` into route samples + fail on L1/mapped mismatch |
| F-04 | **P1** | Signal underspec / KO | `노션에 메모 추가해줘` → **L1** (English-only `_L0_SIGNALS`); `meeting notes` / `checklist for onboarding` miss L0; `refactor one function` / bare `rca` / `architecture` → **L2** | Korean Notion under-routes off Haiku; small refactors over-escalate to Opus | Add KO Notion synonyms; soften L2 keywords with size/risk qualifiers |
| F-05 | **P1** | Model-Invariant Floor gap | Floor: “model choice does not change which packs load”; Adaptive L0/L1 tighten caps below map | Ambiguous precedence when Integrity policies (FileHandling/ToolExecution) are needed on L1 coding | Document: Floor = integrity+kernel invariant; Adaptive caps **model + optional trim**, never strip Integrity Policies required by triggers |
| F-06 | **P1** | sim-10 stale | `docs/simulation-10-report-2026-09-06.md` SIM-01 still “Haiku is the advisory fast path” | Future readers optimize for wrong default model | Errata section: post-7abcc92 Sonnet default / Haiku Notion-only |
| F-07 | **P2** | Cold-start headroom | 6980/7000 → **20 B** headroom; wrapper (non-kernel) ≈3445 B always on first turn | Any wording tweak can fail budget; Adaptive section itself costs cold-start bytes | Keep Adaptive to 2–3 lines in entry; move detail only to deferred doc (already mostly true) |
| F-08 | **P2** | Preload / tooling gaps | `FORBIDDEN_PRELOAD` includes `adaptive-effort.md` (good) but nothing enforces runtime preload; `measure_load` / explicit `sync_kernel --check` not in CI workflow steps | Preload leaks are policy-only; measure regressions may slip if tests skipped | Add CI steps: `measure_load.py --fail-over-cold-start` + `sync_kernel.py --check` |
| F-09 | **P2** | install_pack verify | `REQUIRED_FILES` only CLAUDE/AGENTS/README; scripts check list omits `measure_load.py` / `lib/adaptive_effort.py` (dir copy usually includes them) | Gutted install might pass if docs/scripts dirs exist but key helpers deleted | Extend verify to require `docs/adaptive-effort.md`, `scripts/measure_load.py`, `scripts/lib/adaptive_effort.py` |
| F-10 | **P2** | Scorecard drift | `tests/Scorecard.md` has Simulation protocol but **no Adaptive Effort** rubric | Adaptive regressions not scored in golden protocol | Add Adaptive L0–L3 + Haiku-gate checks to Scorecard |
| F-11 | **P2** | L0 “module” typing | L0 allows `modules=1` as “Notion/doc section” with no allowlist — any module path counts | Could load Coding.md under L0 if caller passes modules=1 | Restrict L0 module allowlist (Meeting/Notion-ish) or rename counter to `doc_sections` |
| F-12 | **P2** | MetaRules vs Adaptive naming | MetaRules: Low/Medium/High risk; Adaptive: L0–L3 models; Autoload: simple vs substantial | Triple taxonomy without mapping table | One-liner map in adaptive-effort: L0≈low docs, L1≈low/medium routine, L2≈medium complex, L3≈high |

---

## 4. Area Deep-Dive (증거)

### 4.1 Entry / Kernel cold-start

| Metric | Value |
|---|---|
| `CLAUDE.md` | **6980 B** |
| Inlined kernel block | ~3535 B |
| Non-kernel wrapper (Latency/Adaptive/Autoload/Budget/…) | ~3445 B |
| kernel/ directory sources | 3430 B |
| Budget | ≤7000 B (structural, not wall-clock) |
| First-turn claim | Simple/low-risk = Kernel only (= this file); **never** autoload model-usage/README/PROGRESS/full packs |

**vs claim:** Structural claim holds (`measure_load` Kernel-only row; detect_task Q&A `kernel_only_safe`). Caveat: “Kernel only” still means **full CLAUDE.md** including Adaptive/Latency/Precedence prose (~7KB), not bare `kernel/` 3.4KB — acceptable per design, but headroom is razor-thin (20 B).

### 4.2 Adaptive Effort consistency

| Source | Default unsure | Haiku scope | L1 pack | Escalate |
|---|---|---|---|---|
| `docs/adaptive-effort.md` | Sonnet L1 | Notion/docs only | Kernel + ≤1 module | model before packs |
| `CLAUDE.md` / `AGENTS.md` | Sonnet L1 | light Notion/docs | pointer only | yes |
| `docs/model-usage.md` Adaptive table | Sonnet L1 | Notion/docs | same | yes |
| `docs/model-usage.md` Haiku Notes | — | **wide** (extraction, summaries, routing…) | — | — |
| `scripts/lib/adaptive_effort.py` | `return "L1"` | English `_L0_SIGNALS` | max_workflows=0 etc. | `escalate_model` |

**Contradictions:** F-01 (L1 packs), F-02 (Haiku Notes), F-04 (KO/signals), F-05 (Floor vs caps).

### 4.3 Loading map / Load Limits enforceability

- Map + `routes.json` limits: module 1 / domain ≤2 / workflow 1 / reviewer 1 / policies ≤3 — enforced by `validate_routes` / `validate_selection`.
- Adaptive tighter L0/L1 caps: **library-only**, not called from detect/validate.
- Preload leaks: heavy docs excluded from Task Map (tested); runtime “don’t open model-usage on L0–L1” is **honor-system**.

### 4.4 Model-invariant floor gaps

Preserved: same Kernel, Integrity intent, escalate≠expand, roster in entry docs.  
Gaps: (1) Adaptive caps vs “same loading map”; (2) Haiku Notes invite weaker-model shortcuts; (3) no mechanical test that Integrity policy triggers survive L1 coding.

### 4.5 install / validate / measure / tests

| Tool | Status | Hole |
|---|---|---|
| `install_pack.py` | Works; tests pass | Weak verify file list (F-09) |
| `validate_framework` | Pass; includes Adaptive phrases + 7KB budget | No pack/tier cross-check (F-03) |
| `validate_routes` | Pass | No adaptive |
| `measure_load` | Pass locally | Not in CI workflow YAML (F-08); covered partly by unittest |
| Unit tests | 76 OK | No test that coding route ⊆ Adaptive L1 caps (would fail today) |

### 4.6 Scenario simulations (Adaptive rules)

Happy path **10/10 PASS** (Q&A→L1, Notion→L0, multi-file arch→L2, deep RCA→L3, unsure→L1, quick fact→L1, coding keyword→L1 model, etc.).

Edge fails / risks:
- KO Notion → L1 (should be L0 if gate honored in Korean)
- Small `refactor` / bare `architecture` / `proposal` → L2 (Opus) may be over-escalation
- Pack-load: coding@L1 **FAIL** caps (F-01)

### 4.7 Prior sim-10 — still open after #17

| sim-10 ID | Post-#17 |
|---|---|
| P0-NO-INSTALL-PACK / P0-NO-MODEL-FLOOR / P0-NO-FABLE51-FLOOR | **Closed** |
| P1-NO-CONTEXT-BUDGET / P1-NO-MEASURE-LOAD / P1-NO-KO-README / P1-NO-FENCE-HELPER | **Closed** |
| P2-SCORECARD-NO-SIM | **Closed** (protocol exists) |
| SIM-01 Haiku path narrative | **Open / stale** (F-06) — behavioral preference flipped in 7abcc92 |
| New from Adaptive layer | **Open:** F-01–F-05, F-07–F-12 |

---

## 5. Contradictions / Drift Risks (모순·드리프트)

1. **L1 model vs L1 packs vs loading-map coding** — highest severity operational conflict.  
2. **Haiku narrow gate vs Haiku Runtime Notes wide gate.**  
3. **Model-Invariant Floor “same map” vs Adaptive tighter L0/L1 caps.**  
4. **sim-10 report Haiku default vs current Sonnet default.**  
5. **Triple taxonomy:** MetaRules risk × Autoload simple/substantial × Adaptive L0–L3.  
6. **English-only L0 signals** vs bilingual user (재전 유 / KO tasks).  
7. **Phrase-only validators** green-wash Adaptive regressions.  
8. **20 B cold-start headroom** — doc edits ↔ CI budget flapping.

---

## 6. Ordered Next-Iteration Plan (구현하지 말 것 — 제안만)

Smallest safe changes first:

1. **Docs-only errata (F-06, F-02):** Update sim-10 SIM-01 + trim Haiku Notes to Adaptive gate; zero code risk.  
2. **Clarify precedence one-pager (F-01, F-05, F-12):** In `adaptive-effort.md`, state explicitly: *L0–L3 select **model**; pack selection remains loading-map / `kernel_only_safe`; L1 “≤1 module” applies only when map says Kernel-light — mapped coding may use map packs with Sonnet.*  
3. **Align `TIERS["L1"]` caps OR reclassify mapped routes (F-01):** Prefer doc+code: either (a) L1 pack caps = map limits when route selected, or (b) `classify_tier` returns L2 when detect_task finds non-kernel route. Pick one; add failing test first.  
4. **Wire mechanical check (F-03):** `validate_framework` or new test: for each route id, `validate_pack_load(classify_tier(sample), counts)` must match chosen policy from step 3.  
5. **KO + signal hygiene (F-04):** Minimal KO L0 phrases (`노션`, `메모 추가`); require risk/size for L2 `refactor`/`architecture`.  
6. **CI harden (F-08):** Add `measure_load.py --fail-over-cold-start` and `sync_kernel.py --check`.  
7. **install verify + Scorecard (F-09, F-10):** Require adaptive/measure paths; Scorecard Adaptive row.  
8. **L0 allowlist (F-11):** Only after above — prevent arbitrary module under L0.  
9. **Headroom (F-07):** Only if entry edits needed — shave wrapper synonyms, don’t expand Adaptive in CLAUDE.md.

**Do not** expand CLAUDE.md; **do not** autoload model-usage; escalate model before packs remains the north star.

---

## 7. Tooling Snapshot (재현)

```text
HEAD=1ecaa7b93fcbf71c4d8ac275ed2aa51f4c21d654
CLAUDE.md=6980 bytes
measure_load anti-pattern ≈ 8.8× heaviest mapped route
unittest: 76 OK
Adaptive happy-path sims: 10/10; route×tier pack mismatches: 6/10
```

---

*End of analysis. Implementation tracked on branch `fix/adaptive-map-align`.*
