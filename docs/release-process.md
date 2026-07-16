# Release and Versioning

FEF uses Semantic Versioning:

- MAJOR: incompatible Pack structure or runtime contract changes.
- MINOR: backward-compatible Pack, workflow, Golden Test, or automation features.
- PATCH: typo, rule-conflict fix, test correction, or documentation improvement.

The current harness work is a backward-compatible automation addition, so the proposed next release is v1.3.0. Do not create or push a tag until release review approves the version and migration notes.

This small repository uses a manually reviewed CHANGELOG plus a release template; Conventional Commits and a release-drafter dependency are not required.

## Release Checklist

1. Run the three commands in `scripts/README.md`.
2. Review warnings, CHANGELOG, compatibility, migration needs, and known limitations.
3. Confirm the target commit and version.
4. Create the annotated tag and GitHub Release only after approval.
5. Use `.github/RELEASE_TEMPLATE.md` for the release body.
