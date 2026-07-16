# FEF Reasoning Checklist

Use for substantial technical outputs.

## Before Answering

- What is the real operational problem?
- What does the user need to decide or do?
- What assumptions am I making?
- What evidence is available?
- What is uncertain?
- Does the task depend on a file, repository, tool result, command output, or current external fact that must be verified?
- Is the required evidence accessible, and which of analysis, execution, verification, and delivery apply?

## During Reasoning

- Separate facts from inferences.
- Consider one alternative explanation.
- Identify version and scope.
- Identify risks and failure modes.
- Confirm work targets the actual repository or artifact, not an assumed or temporary copy.
- Check file contents and command results rather than inferring them; separate failed actions from successful ones.

## Before Delivery

- Remove unsupported certainty.
- Mark `[unverified]` where needed.
- Align confidence with evidence.
- Ensure the output is actionable.
- Ensure every completion claim has observable evidence.
- Report unresolved limitations or verification failures and, when applicable, the artifact path, modified location, test result, or command outcome.
