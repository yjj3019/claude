import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.validate_fable_provenance as target


class FableProvenanceTest(unittest.TestCase):
    def bundle(self, *, target_involved=False):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({"dataset_id": "D-1", "custodian_id": "C-1"}), encoding="utf-8")
        evidence = root / "provenance.json"
        evidence.write_text(json.dumps({
            "evidence_version": "1.0",
            "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
            "dataset_id": "D-1", "custodian_id": "C-1", "authoring_method": "human",
            "target_model_involved": target_involved, "distillation_material_access": False,
            "attestor_id": "A-1", "attested_at": "2026-07-24T00:00:00Z",
        }), encoding="utf-8")
        return temp, root, manifest, evidence

    def test_complete_attestation_passes(self):
        temp, root, manifest, evidence = self.bundle()
        self.addCleanup(temp.cleanup)
        with patch.object(target, "LOCAL_HOLDOUT", root.resolve()):
            self.assertTrue(target.validate(evidence, manifest)["provenance_evidence_complete"])

    def test_target_model_authorship_fails(self):
        temp, root, manifest, evidence = self.bundle(target_involved=True)
        self.addCleanup(temp.cleanup)
        with patch.object(target, "LOCAL_HOLDOUT", root.resolve()):
            self.assertFalse(target.validate(evidence, manifest)["valid"])


if __name__ == "__main__":
    unittest.main()
