---
name: fef-manual
description: Operations manual (FEF route 'manual'). Use when the task involves: operations manual, runbook, sop, 운영 매뉴얼, 절차서. Base risk level: medium. Loads the FEF packs for this task type.
---

# FEF Route: Operations manual

Generated from `config/routes.json` by `scripts/generate_skills.py`. Do not edit by hand.

When this skill triggers, read and follow these FEF packs from the repository root, in this order:

## Policies

- `policies/Writing.md`
- `policies/Evidence.md`
- `policies/Review.md`

## Module and Workflow

- Module: `modules/Manual.md`
- Workflow: `workflows/ManualWorkflow.md`
- Reviewer: `reviewers/DocumentationReviewer.md` - run at most once per artifact, after a draft exists; do not review reviewer output.

## Domain Packs

If the task names a technology, additionally read the matching domain pack (max 2):

- rhel, red hat enterprise linux, 레드햇, 커널 -> `domains/RHEL.md` (subsumes Linux)
- openshift, 오픈시프트 -> `domains/OpenShift.md` (subsumes Kubernetes)
- kubernetes, k8s, 쿠버네티스 -> `domains/Kubernetes.md`
- linux, 리눅스 -> `domains/Linux.md`
- ansible, 앤서블 -> `domains/Ansible.md`
- satellite, 새틀라이트 -> `domains/Satellite.md`
- enterprise architecture, 엔터프라이즈 아키텍처 -> `domains/EnterpriseArchitecture.md`

## Limits and Risk

- Pack limits per task: 3 policies, 1 module, 2 domains, 1 workflow, 1 reviewer.
- Base risk level for this route: medium. If the task mentions any of (production, security, customer, public sector, 운영, 보안, 고객, 공공), treat it as high risk and raise verification depth per the Kernel Meta Rules.
- The inlined Kernel in `CLAUDE.md` always applies; these packs extend it, never replace it.
