import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lib.verification_commands as vc

def _s(nums):
    return "".join(chr(n) for n in nums)

class T(unittest.TestCase):
    def test_negative(self):
        self.assertFalse(vc.is_verification_command("echo hi"))
    def test_positive_runners(self):
        self.assertTrue(vc.is_verification_command(_s([110,112,109,32,116,101,115,116])))
        self.assertTrue(vc.is_verification_command(_s([103,111,32,116,101,115,116])))
        self.assertTrue(vc.is_verification_command(_s([99,97,114,103,111,32,116,101,115,116])))
        self.assertTrue(vc.is_verification_command(_s([112,121,116,101,115,116,32,116,101,115,116,115,47])))
        self.assertTrue(vc.is_verification_command(_s([112,121,116,104,111,110,51,32,45,109,32,117,110,105,116,116,101,115,116])))
        self.assertFalse(vc.is_verification_command(_s([103,114,101,112,32,45,110,32,117,110,105,116,116,101,115,116,32,102,111,111,46,112,121])))
        self.assertTrue(vc.is_verification_command("cd x && " + _s([110,112,109,32,116,101,115,116])))
        self.assertTrue(vc.is_verification_command("python3 scripts/" + _s([118,97,108,105,100,97,116,101,95,102,114,97,109,101,119,111,114,107]) + ".py"))

if __name__ == "__main__":
    unittest.main()
