import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.validate_fable_holdout as target


class FableHoldoutTest(unittest.TestCase):
    def make_manifest(self, count=1, *, tamper=False, canary=True):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        fixtures = root / "fixtures"
        fixtures.mkdir()
        entries = []
        for index in range(count):
            raw = f"private scenario {index}".encode()
            path = fixtures / f"P-{index}.md"
            path.write_bytes(raw + (b" changed" if tamper else b""))
            entries.append({
                "scenario_id": f"P-{index}", "suite": "evidence", "fixture_path": f"fixtures/P-{index}.md",
                "sha256": hashlib.sha256(raw).hexdigest(), "provenance": "private_holdout",
                "independently_authored": True, "exposed_to_distillation": False,
                "canary_sha256": hashlib.sha256(f"canary-{index}".encode()).hexdigest() if canary else None,
            })
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({"manifest_version": "1.0", "dataset_id": "D-1", "created_at": "2026-07-21", "custodian_id": "C-1", "entries": entries}), encoding="utf-8")
        return temp, root, manifest

    def run_local(self, manifest, root, minimum=5):
        with patch.object(target, "LOCAL_HOLDOUT", root.resolve()):
            return target.validate(manifest, minimum)

    def test_valid_but_underfilled_is_not_promotion_ready(self):
        temp, root, manifest = self.make_manifest()
        self.addCleanup(temp.cleanup)
        result = self.run_local(manifest, root)
        self.assertTrue(result["valid"])
        self.assertFalse(result["intake_gate_ready"])
        self.assertFalse(result["benchmark_promotion_ready"])

    def test_five_with_canaries_is_ready_at_intake_gate(self):
        temp, root, manifest = self.make_manifest(5)
        self.addCleanup(temp.cleanup)
        result = self.run_local(manifest, root)
        self.assertTrue(result["intake_gate_ready"])
        self.assertFalse(result["benchmark_promotion_ready"])

    def test_hash_tamper_fails(self):
        temp, root, manifest = self.make_manifest(tamper=True)
        self.addCleanup(temp.cleanup)
        self.assertFalse(self.run_local(manifest, root)["valid"])

    def test_missing_canary_blocks_promotion(self):
        temp, root, manifest = self.make_manifest(5, canary=False)
        self.addCleanup(temp.cleanup)
        result = self.run_local(manifest, root)
        self.assertTrue(result["valid"])
        self.assertFalse(result["intake_gate_ready"])


if __name__ == "__main__":
    unittest.main()
