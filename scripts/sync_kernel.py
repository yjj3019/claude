#!/usr/bin/env python3
"""Synchronize the generated Kernel block in CLAUDE.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "CLAUDE.md"
KERNEL_FILES = [
    ROOT / "kernel" / "CoreKernel.md",
    ROOT / "kernel" / "MetaRules.md",
    ROOT / "kernel" / "Checklist.md",
]
BEGIN = "<!-- BEGIN INLINED KERNEL (generated from kernel/ — do not edit here) -->"
END = "<!-- END INLINED KERNEL -->"


def normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()).rstrip()


def rendered_kernel() -> str:
    return "\n\n".join(normalize(path.read_text(encoding="utf-8-sig")) for path in KERNEL_FILES)


def synchronized_text(text: str) -> str:
    if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) >= text.index(END):
        raise ValueError("CLAUDE.md must contain exactly one ordered inlined Kernel marker pair")
    before, remainder = text.split(BEGIN, 1)
    _, after = remainder.split(END, 1)
    return f"{before}{BEGIN}\n{rendered_kernel()}\n{END}{after}"


def main() -> int:
    CLAUDE.write_text(synchronized_text(CLAUDE.read_text(encoding="utf-8-sig")), encoding="utf-8")
    print("Synchronized CLAUDE.md inlined Kernel.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
