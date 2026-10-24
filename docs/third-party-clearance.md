# Third-party clearance and distribution policy

## Current decisions

Original TaskForge/FEF contributions remain covered only by the scoped [LICENSE](../LICENSE).
The publisher confirmed authority for those original contributions on 2026-10-22.
That confirmation does not cover third-party expressions, prompts or archives.

| Material | Evidence currently held | What is missing | Distribution decision |
|---|---|---|---|
| Original FEF contributions | Scoped MIT grant in LICENSE; publisher authority confirmation recorded in the license audit | This is not evidence of ownership of imported material | Continue within the existing grant |
| DelegationLoop source, optimized copies and templates | Archived commits 1e35bf0a6d16bac0c6e1dccda1014a1e78b7bb96 / 01351414e10df3c177939e4fef8393609ece6c55 and original attribution; upstream query returned 404 on 2026-10-24 | Applicable license or permission from each relevant rights holder; authority over any guide-derived parts | Excluded from native payload; new standalone install/ZIP refused |
| Kim guide-derived prompts and wording | [Original guide](https://sdk-kim-builds.com/guides/ai-delegation-loop-playbook/), credited author 낭만빌더 김스듴, 2026-09-18 | Applicable permission covering the copied expression and planned distribution; author name alone does not prove granting authority | Not shipped as a skill or prompt bundle |
| Source-history bundle, PR snapshots and historical artifacts | Preserved provenance and commit history in the source clone | Applicable rights and conditions for the included contents and authors | Kept for inspection; excluded from supported git-archive exports and runtime payloads |
| Other external quotations or source material | Existing citations and source-specific notices; scope described in the source [license audit](https://github.com/yjj3019/claude/blob/main/docs/license-audit-2026-10-22.md) | File/section inventory and applicable permission or other reviewed legal basis where required | Do not claim whole-package MIT or comprehensive rights clearance |

These are evidence states, not a legal ownership determination. Public availability,
credit, a Git commit author field or model-generated wording alone does not establish
all required rights. [GitHub's licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
distinguishes public repository access from an open-source license grant.

## How an unresolved item becomes confirmed

For each component, record the following in the existing license audit before
changing distribution code. Keep original evidence and record corrections explicitly.

| Required record | Evidence to review |
|---|---|
| Component and exact contents | File/section list, upstream URL and pinned revision, SHA-256 of the reviewed material |
| Rights holder and authority | Identity plus the basis for owning the relevant rights or acting for the owner; repository access alone is insufficient |
| Grant | The applicable published license at that revision, or an authentic written permission covering the actual contents |
| Allowed actions | Copying, modification/derivative work and each intended channel: plugin, installer, ZIP, public Git hosting; commercial use or sublicensing only if actually granted |
| Conditions | Attribution, notices, copyleft/source delivery, restrictions, territory, duration, expiry and revocation terms as applicable |
| Evidence reference | Source URL/revision or a protected evidence location and hash, date obtained, and a public redacted reference if disclosure is permitted |
| Review conclusion | Reviewer/date, precise approved scope, remaining exclusions and the reason the evidence satisfies that scope |

If ownership, authenticity, scope or a condition is still unclear, keep that item
unresolved and blocked. A grant for one author's contribution cannot clear someone
else's underlying work. Where legal interpretation is needed, obtain appropriate
legal review; the scripts do not decide ownership or legal exceptions.

Do not commit private contracts, signatures, email addresses, credentials or personal
information as proof. Store original evidence privately and publish only approved,
redacted references. No rights-holder message has been sent by this project task.

A permission request can identify the exact files/revision and ask the relevant
rights holder to state their authority, permitted copying/modification/channels,
conditions and whether sublicensing is allowed. Do not label the material MIT unless
that specific grant permits it. An independent replacement with reviewed provenance
is another possible resolution; removing distribution is not acquiring permission.

## Release gate and reopening

- Native plugin 2.0.0 excludes `skills/ai-delegation-loop/` entirely.
- The common standalone installer and ZIP entry points refuse new distribution
  before destination, backup or staging writes. Force, dry-run and evidence flags
  do not override this decision. Existing installed files and read-only checks stay intact.
- No environment flag, CLI override or unsigned status file can grant permission.
  The internal code policy is changed only through a reviewed source change after
  the component-level evidence above is sufficient. Algorithm unit tests that
  simulate a cleared policy are not evidence of real permission.
- Reopening requires an updated decision record, applicable notices/license scope,
  reviewed code changes for only the approved contents/channels, no-write negative
  controls for remaining exclusions and a regenerated payload and archive check.

`.gitattributes` excludes the named uncleared source directories and their old
native copies from supported future `git archive` exports. This does not remove
tracked source, Git history, existing caches, already published downloads or raw
clones. Loading the source root with `--plugin-dir .` can discover preserved
source skills and is not the supported native distribution; load the generated
`plugins/fef-engineering` folder instead. Manual copying and Git host release
settings are outside the script gate.
Do not redistribute the full mixed source clone under a package-wide MIT claim.
The source [attribution notice](https://github.com/yjj3019/claude/blob/main/skills/ai-delegation-loop/THIRD_PARTY_NOTICES.md)
and history remain preserved; they are not a new license.
