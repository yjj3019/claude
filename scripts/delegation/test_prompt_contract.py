"""Static prompt contracts and isolated generated-playbook fixtures, not model tests."""
import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "skills" / "ai-delegation-loop"
spec = importlib.util.spec_from_file_location("contract_validator", Path(__file__).with_name("validate_skill.py"))
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def text(name):
    return (PACKAGE / name).read_text(encoding="utf-8")


def standalone(name):
    return text("prompts/" + name).split("```text\n", 1)[1].split("\n```", 1)[0]


def approval_contract(body):
    actions = ("전송", "메일", "게시", "삭제", "결제", "배포", "계정", "권한 변경")
    return all(action in body for action in actions) and "이번" in body and "별도 명시 승인" in body


class PromptContractTests(unittest.TestCase):
    def test_A16_standalone_interview_fallback_produces_valid_frontmatter(self):
        body = standalone("01-interview.md")
        self.assertIn("templates/job-playbook/SKILL.template.md", body)
        self.assertIn("파일의 첫 줄", body)
        example = re.search(r"(?m)^---\nname:.*?\n---", body, re.S).group()
        generated = example.replace("[job-name]", "weekly-report").replace(
            "[이 업무를 언제 무엇을 위해 수행하는지 실제 호출 문장]", "매주 보고서 초안을 작성할 때 사용")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "weekly-report" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(generated + "\n\n# Weekly report\n", encoding="utf-8")
            self.assertEqual(validator.check_skill_md(path, True), [])
            path.write_text(generated.replace("weekly-report", "Bad_Name"), encoding="utf-8")
            self.assertTrue(validator.check_skill_md(path, True))

    def test_A17_toolbox_waits_for_saved_checks_and_human_review(self):
        body = standalone("02-toolbox.md")
        self.assertIn("이 단계에서는 업무를 다시 실행하지 마라", body)
        self.assertRegex(body, r"검증 항목.*SKILL\.md.*저장하고 사람이 확인한 뒤에만 두 번째 실행")
        self.assertNotIn("마지막으로 동일 업무를 처음부터 다시 실행해라", body)

    def test_A18_standalone_toolbox_covers_each_state_change_and_new_approval(self):
        body = standalone("02-toolbox.md")
        self.assertTrue(approval_contract(body))
        self.assertIn("첫 실행의 승인을 재사용하지", body)
        self.assertIn("승인이 없으면 초안·읽기 전용 확인·격리된 테스트", body)

    def test_A18_original_omitted_payment_and_permission_clause_is_rejected(self):
        old = "외부 전송·게시·삭제·배포는 이 프롬프트만으로 실행하지 마라."
        self.assertFalse(approval_contract(old))
        for action in ("결제", "권한 변경"):
            self.assertFalse(approval_contract(standalone("02-toolbox.md").replace(action, "")))

    def test_A19_proof_explicitly_persists_whole_protocol(self):
        body = standalone("03-proof.md")
        self.assertIn("전체를 [job-name]/SKILL.md에 영구 기록", body)
        self.assertIn("현재 채팅에서만", body)
        for requirement in ("PASS", "FAIL", "UNVERIFIED", "N/A", "L0~L4", "전체 검증", "세 항목 이상", "하나라도 실패", "별도 명시 승인"):
            self.assertIn(requirement, body)
        self.assertIn("저장과 사람의 확인이 끝나기 전에는 두 번째 업무 실행을 시작하지", body)

    def test_A19_template_keeps_protocol_in_an_isolated_playbook(self):
        generated = text("templates/job-playbook/SKILL.template.md").replace(
            "name: job-name", "name: weekly-report").replace(
            "[이 업무를 무엇을 위해 언제 수행하는지 실제 호출 문장으로 작성]", "주간 보고서 작성")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "weekly-report" / "SKILL.md"
            path.parent.mkdir()
            path.write_text(generated, encoding="utf-8")
            self.assertEqual(validator.check_skill_md(path, True), [])
            protocol = path.read_text(encoding="utf-8").split("## 매 실행의 검증·중단·승인 규칙", 1)[1]
            for requirement in ("PASS", "FAIL", "UNVERIFIED", "N/A", "L0~L4", "전체 검증", "3개 이상", "하나라도 실패", "결제", "권한 변경", "별도 명시 승인"):
                self.assertIn(requirement, protocol)

    def test_A20_taxonomy_allows_multiple_layers_and_external_conditions_everywhere(self):
        for name in ("SKILL.md", "manual.ko.md", "prompts/03-proof.md", "prompts/04-failure-loop.md"):
            body = text(name)
            with self.subTest(file=name):
                for layer in ("프로세스", "툴박스", "증명", "외부 조건"):
                    self.assertIn(layer, body)
                self.assertIn("하나 또는 여러 개", body)
                self.assertIn("UNVERIFIED", body)
                self.assertNotIn("원인을 하나의 레이어로 분류", body)

    def test_historical_model_report_is_not_current_evidence(self):
        body = text("tests/simulation-report.ko.md")
        for marker in ("v1.2.1", "HISTORICAL", "STALE_FOR_CURRENT_PACKAGE", "UNVERIFIED"):
            self.assertIn(marker, body)
        self.assertIn("simulation-report.v1.2.ko.md", body)


if __name__ == "__main__":
    unittest.main()
