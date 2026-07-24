import json
import re
import subprocess
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_FILE = SKILL_DIR / "SKILL.md"


class GoDevSkillTest(unittest.TestCase):
    def test_required_resources_exist(self) -> None:
        required = {
            "references/core-go.md",
            "references/errors-context.md",
            "references/logging-security.md",
            "references/http-api.md",
            "references/grpc.md",
            "references/persistence.md",
            "references/gorm-database.md",
            "references/testing.md",
            "sql-standards.md",
            "agents/openai.yaml",
            "evals/cases.json",
            "evals/baseline-review.md",
        }
        missing = sorted(path for path in required if not (SKILL_DIR / path).is_file())
        self.assertEqual([], missing)

    def test_skill_declares_precedence_and_style_layers(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")
        self.assertIn("## 规则优先级", text)
        self.assertIn("## 必须规则", text)
        self.assertIn("## 推荐风格", text)
        self.assertLess(text.index("仓库中的 `AGENTS.md`"), text.index("本 Skill 的推荐风格"))

    def test_no_private_or_unsafe_legacy_guidance(self) -> None:
        text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in SKILL_DIR.rglob("*")
            if path.is_file() and path.suffix in {".md", ".go", ".yaml", ".json"}
        )
        forbidden = {
            "gitlab-esd.leapmotor.com",
            "lp-go-tool.git",
            'log.Infof("request: %+v"',
            'log.Infof("resp: %+v"',
            "SetErrorWithMsg(codes.InternalServerError, err.Error())",
            "Db.Debug().WithContext(ctx)",
        }
        found = sorted(value for value in forbidden if value in text)
        self.assertEqual([], found)

    def test_description_is_go_specific(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")
        match = re.search(r"^description: (.+)$", text, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        description = match.group(1)
        self.assertIn("working in a Go repository", description)
        self.assertIn("repository actually uses that stack", description)

    def test_eval_set_has_trigger_and_near_miss_coverage(self) -> None:
        cases = json.loads((SKILL_DIR / "evals/cases.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 8)
        self.assertTrue(any(case["should_trigger"] for case in cases))
        self.assertTrue(any(not case["should_trigger"] for case in cases))
        for case in cases:
            self.assertTrue(case["prompt"])
            self.assertTrue(case["assertions"])
            if case["should_trigger"]:
                self.assertTrue(case["expected_refs"])
                for reference in case["expected_refs"]:
                    candidates = [SKILL_DIR / "references" / reference, SKILL_DIR / reference]
                    self.assertTrue(any(candidate.is_file() for candidate in candidates), reference)
            else:
                self.assertEqual([], case["expected_refs"])

    def test_go_examples_are_formatted(self) -> None:
        examples = sorted((SKILL_DIR / "examples").glob("*.go"))
        self.assertTrue(examples)
        result = subprocess.run(
            ["gofmt", "-d", *map(str, examples)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)


if __name__ == "__main__":
    unittest.main()
