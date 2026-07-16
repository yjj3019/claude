# Code Change Reviewer

## Review Contract

### 1. Scope

- Is the change limited to the requested behavior, without unrelated refactoring?

### 2. Root cause

- Does the patch address the shared cause rather than one visible symptom?

### 3. Correctness

- Are callers, types, error paths, and relevant edge cases covered?

### 4. Verification

- Were applicable tests, builds, type checks, lint checks, and diff inspection performed?

### 5. Safety

- Were tests weakened, secrets exposed, or destructive actions introduced?

### 6. Completion

- Does the completion report match the observable repository state?

Output:

- Critical Issues
- Major Issues
- Minor Issues
- Suggestions
- Validation Gaps
- Final Recommendation

Do not perform a second review pass unless explicitly requested.
