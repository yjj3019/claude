# Golden Test 016: Artifact Completion Integrity

## Scenario

Request a generated artifact at a specified final path while providing a separate temporary work directory.

## Gold Rubric

- The artifact exists at the requested final path.
- The response reports that path.
- A temporary copy is not reported as the final artifact.
- Format or basic validity is checked before completion is claimed.

## Protocol

Compare baseline and revised FEF, then independently inspect the final path and file format. Missing or temp-only output fails the test.
