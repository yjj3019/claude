# Claude Projects Guide

UI labels and file limits can change by Claude version; use the equivalent Project instructions and knowledge/file controls available in the current UI.

1. Clone this repository or download a release ZIP.
2. Create a Claude Project for the target workstream.
3. Use `CLAUDE.md` as Project Instructions or the primary runtime file.
4. Add `kernel/CoreKernel.md`, `kernel/MetaRules.md`, `kernel/Checklist.md`, and `docs/loading-map.md` to Project Knowledge.
5. Add only the policies, module, domain, workflow, and Reviewer needed for the project. Preserve their repository paths or filenames.
6. When file count or size is limited, prioritize Kernel → loading map → Integrity Policies → primary Module/Domain → Workflow → one Reviewer.
7. Start with a representative request, such as “Use the RHEL RCA route and state which Packs are loaded.”
8. Confirm normal loading by checking that the response names no missing required file, selects no more than one Reviewer, and does not exceed Pack limits.
9. If loading fails, check filenames, stale duplicates, missing referenced Packs, and whether `CLAUDE.md` was placed in instructions rather than only uploaded as unused knowledge.
10. For updates, compare the release notes, replace changed runtime files, remove stale duplicates, and repeat the representative loading check.

Do not upload every Domain Pack by default. Keep Project instructions short and task knowledge selective.
