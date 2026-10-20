#!/usr/bin/env python3
"""Synchronize or verify the generated Kernel block in CLAUDE.md."""
import argparse
import sys
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
    missing = [str(path.relative_to(ROOT)) for path in KERNEL_FILES if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing Kernel source files: {', '.join(missing)}")
    return "\n\n".join(normalize(path.read_text(encoding="utf-8-sig")) for path in KERNEL_FILES)


def synchronized_text(text: str) -> str:
    if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(BEGIN) >= text.index(END):
        raise ValueError("CLAUDE.md must contain exactly one ordered inlined Kernel marker pair")
    before, remainder = text.split(BEGIN, 1)
    _, after = remainder.split(END, 1)
    return f"{before}{BEGIN}\n{rendered_kernel()}\n{END}{after}"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify the inlined Kernel without writing; exit 1 on drift")
    args = parser.parse_args(argv)
    try:
        current = CLAUDE.read_text(encoding="utf-8-sig")
        expected = synchronized_text(current)
    except (OSError, ValueError) as error:
        print(f"sync_kernel error: {error}", file=sys.stderr)
        return 2
    if args.check:
        if current == expected:
            print("CLAUDE.md inlined Kernel is in sync.")
            return 0
        print("CLAUDE.md inlined Kernel is out of sync; run python scripts/sync_kernel.py", file=sys.stderr)
        return 1
    if current == expected:
        print("CLAUDE.md inlined Kernel already in sync; no write needed.")
        return 0
    CLAUDE.write_text(expected, encoding="utf-8")
    print("Synchronized CLAUDE.md inlined Kernel.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
