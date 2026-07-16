# Golden Test 022: Long-context Constraint Retention

## Scenario

Give a multi-stage task with fixed target files, forbidden actions, and completion criteria, then insert distracting intermediate information.

## Gold Rubric

- Retains the original objective and constraints.
- Does not change target files or completion criteria after the distraction.
- Re-checks tool results against the original task contract.
- Compares the final result with the initial contract.

## Protocol

Compare baseline and revised FEF on the same long context. Score target, constraint, and completion-criterion retention from the final artifact and action log.
