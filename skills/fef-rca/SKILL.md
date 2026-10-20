---
name: fef-rca
description: Perform root-cause analysis for failures, incidents, or unexpected behavior. Use when investigating why something broke, especially in Linux/RHEL/OpenShift environments. Prefer primary evidence.
---

# FEF RCA Skill

Conduct evidence-based root cause analysis.

1. Gather symptoms, timeline, and relevant logs/metrics from primary sources.
2. Form competing hypotheses; test the most likely ones with targeted checks.
3. Identify the shared root cause and contributing factors.
4. Recommend the smallest durable fix and verification steps.
5. Document residual risk and unverified items as [unverified].

Load domain packs (e.g., RHEL, Linux) and Integrity Policies only when the task requires them. Find them through `${CLAUDE_PLUGIN_ROOT}/docs/loading-map.md` and resolve pack paths against `${CLAUDE_PLUGIN_ROOT}`, not the working project. Do not claim completion without observable evidence.
