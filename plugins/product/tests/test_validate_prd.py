"""validate_prd.py가 PRD 구조 지적과 종료 코드를 규칙대로 내는지 확인한다."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/to-prd/scripts/validate_prd.py"
TEMPLATE = ROOT / "skills/to-prd/assets/prd-template.md"
VALID = textwrap.dedent("""\
    ---
    id: PRD-0007
    title: 완료 항목 숨기기
    status: draft
    workflow_status: conditional
    revision: 2
    owners: []
    sources:
      - 대화 요청
    ---

    # 완료 항목 숨기기

    ## 문제와 기대 결과

    완료 항목이 섞여 진행 중인 일을 찾기 어렵다. [기대 결과](#요구사항)

    ## 요구사항

    ### REQ-001: 완료 항목을 숨길 수 있다

    - 수용 기준:
      - 토글을 켜면 완료 항목이 사라진다.
    - 관련 품질 기대: 목표 미정(OPEN-001)

    ## 미결정

    | ID | 내용 |
    | --- | --- |
    | OPEN-001 | 응답 시간 목표 |

    | 흐름 | 요구사항 |
    | --- | --- |
    | REQ-001 | 토글 |

    `REQ-999`는 코드 예시라 검사하지 않는다.

    ```text
    <작성 안내> REQ-998
    ```
""")
FULL = textwrap.dedent("""\
    ---
    id: PRD-0012
    title: 예약 취소 수수료 안내
    status: draft
    workflow_status: conditional
    revision: 1
    owners: [예약팀]
    sources:
      - 2026-10-01 고객 문의 집계
    ---

    # 예약 취소 수수료 안내

    ## 문제와 기대 결과

    - 대상 사용자: 캠핑장 예약자
    - 현재 문제와 확인 근거: 취소 수수료 문의가 전체 문의의 30%다.
    - 현재 해결 방식과 남은 불편(확인된 경우): 고객센터에 전화로 묻는다.
    - 기대하는 사용자·제품 결과: 예약자가 취소 전에 수수료를 직접 확인한다.

    ## 제품 경계

    ### 포함 범위

    - 취소 화면의 수수료 안내

    ### 비목표

    - 수수료율 변경

    ### 외부 시스템과 운영 책임

    - 결제 대행사 환불 처리는 운영팀이 맡는다.

    ## 제품 동작과 규칙

    ### 정상 동작

    - 사용 계기 → 핵심 행동 → 얻는 결과·종료: 취소 버튼 → 수수료 확인 → 취소 확정

    ### 실패와 예외

    - 수수료 계산 실패 시 취소 확정을 막고 다시 시도하게 한다.

    ### 권한, 취소와 재시도

    - 예약자 본인만 취소할 수 있다.

    ## 품질 기대

    | ID | 영역 | 기대 | 근거 또는 OPEN ID |
    | --- | --- | --- | --- |
    | NFR-001 | 성능 체감 | 수수료가 즉시 보인다 | OPEN-001 |

    ## 요구사항

    ### REQ-001: 예약자가 취소 전에 수수료 기준을 확인한다

    - 상위 목표: 취소 문의 감소
    - 우선순위: P1
    - 관련 품질 기대: NFR-001
    - 행위자: 예약자
    - 계기 또는 조건: 취소 버튼을 누른다.
    - 결과: 적용될 수수료와 기준이 보인다.
    - 근거 ID: OPEN-001
    - 수용 기준: 취소 확정 전에 수수료 금액이 표시된다.
    - 검증 방법: `cancel_fee_viewed`

    ## 성공 신호

    | ID | 신호 | 측정 방법 | 기준 | 근거 또는 결정 주체 |
    | --- | --- | --- | --- | --- |
    | SUCCESS-001 | 수수료 문의 감소 | 고객센터 분류 | 미결정 | 운영팀 |

    ## 가정, 충돌과 미결정 항목

    | ID | 종류 | 내용 | 영향 | 다음 행동 |
    | --- | --- | --- | --- | --- |
    | OPEN-001 | 미결정 | 응답 시간 목표 | NFR-001 수치 | 운영팀 확인 |
    | RISK-001 | 위험 | 수수료율 변경 | 안내 문구 갱신 | 변경 알림 구독 |

    ## 준비 상태

    | 영역 | 상태 | 근거 |
    | --- | --- | --- |
    | 제품 합의 | conditional | OPEN-001 남음 |
    | 디자인 | not-ready | 화면 미정 |
    | 엔지니어링 | not-ready | API 미정 |
    | QA | not-ready | 기준 미정 |
    | 운영 | not-ready | 담당 미정 |

    ## 관련 문서와 승격 후보

    - 관련 설계 문서: 없음
    - 관련 도메인 문서: 없음
    - 관련 ADR: 없음
    - 제품 도메인 정본 후보: 취소 수수료
    - ADR 후보: 없음

    ## 승인 근거

    - 승인 주체: 없음
    - 권한 근거: 없음
    - 승인한 범위: 없음
    - 승인한 리비전: 없음
    - 확인 시점: 없음
    - 승인 근거: 없음
""")


class ValidatePrdTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.docs = self.root / "docs/prd"
        self.docs.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        path = self.docs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_tool(self, *args):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)], capture_output=True,
                                text=True, check=False)
        report = json.loads(result.stdout) if result.stdout else None
        return result, report

    def codes(self, report, index=0):
        return [item["code"] for item in report["files"][index]["findings"]]

    def test_valid_document_passes(self):
        path = self.write("prd.md", VALID)
        result, report = self.run_tool(path, "--allowed-root", self.docs)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(report["files"][0]["findings"], [])
        self.assertEqual(report["checks"], {"allowed_paths": "checked", "document_ids": "inputs-only"})

    def test_unfilled_template_reports_placeholders(self):
        result, report = self.run_tool(TEMPLATE)
        self.assertEqual(result.returncode, 1)
        messages = [item["message"] for item in report["files"][0]["findings"] if item["code"] == "placeholder"]
        self.assertTrue(any("PRD-XXXX" in message for message in messages))
        self.assertTrue(any("<제품 또는 기능 이름>" in message for message in messages))
        self.assertIn("작성 안내 주석", messages)
        self.assertIn("빈 표 칸", messages)
        self.assertIn("빈 목록 필드", messages)
        self.assertTrue(any("unselected priority choice" in message for message in messages))
        self.assertTrue(any(message == "unfilled OPEN ID: (OPEN ID)" for message in messages))

    def test_filled_template_with_quality_table_passes(self):
        result, report = self.run_tool(self.write("prd.md", FULL))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(report["files"][0]["findings"], [])

    def test_inline_code_values_are_not_empty(self):
        text = VALID.replace("| REQ-001 | 토글 |", "| REQ-001 | `status` |")
        text = text.replace("- 관련 품질 기대:", "- 엔드포인트: `POST /orders`\n- 관련 품질 기대:")
        result, report = self.run_tool(self.write("prd.md", text))
        self.assertEqual(result.returncode, 0, result.stdout)
        empty = self.write("empty.md", VALID.replace("- 관련 품질 기대: 목표 미정(OPEN-001)",
                                                     "- `status`:\n- 관련 품질 기대: 목표 미정(OPEN-001)"))
        _, report = self.run_tool(empty)
        self.assertIn("빈 목록 필드", [item["message"] for item in report["files"][0]["findings"]])

    def test_heading_slug_keeps_inline_code_text(self):
        text = VALID + "\n## `status` 필드\n\n[상태](#status-필드)\n"
        result, report = self.run_tool(self.write("prd.md", text))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_indentless_yaml_block_list(self):
        text = VALID.replace("sources:\n  - 대화 요청", "sources:\n- 대화 요청")
        result, report = self.run_tool(self.write("prd.md", text))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_list_scalar_metadata_reports_finding(self):
        cases = {
            "id": VALID.replace("id: PRD-0007", "id: [PRD-1]"),
            "workflow_status": VALID.replace("workflow_status: conditional", "workflow_status:\n  - conditional"),
            "status": VALID.replace("status: draft", "status: [draft]"),
        }
        for key, text in cases.items():
            with self.subTest(key=key):
                result, report = self.run_tool(self.write(f"{key}.md", text))
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn({"code": "metadata", "line": 1, "message": f"값이 문자열이 아님: {key}"},
                              report["files"][0]["findings"])
        self.write("old/listed.md", cases["id"])
        path = self.write("new.md", VALID)
        result, report = self.run_tool(path, "--existing", self.docs / "old")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_comparison_operators_are_not_placeholders(self):
        text = VALID.replace("| OPEN-001 | 응답 시간 목표 |",
                            "| OPEN-001 | 응답 시간 목표 |\n| NFR-001 | p95 < 300ms, 가용성 > 99.9% |")
        result, report = self.run_tool(self.write("prd.md", text))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_metadata_rules(self):
        text = VALID.replace("workflow_status: conditional", "workflow_status: approved")
        text = text.replace("revision: 2\n", "").replace("sources:\n  - 대화 요청", "sources: []")
        result, report = self.run_tool(self.write("prd.md", text))
        self.assertEqual(result.returncode, 1)
        messages = [item["message"] for item in report["files"][0]["findings"] if item["code"] == "metadata"]
        self.assertIn("필수 키 없음: revision", messages)
        self.assertIn("sources가 비어 있음", messages)
        self.assertIn("workflow_status approved에는 status stable가 필요함: draft", messages)

    def test_missing_frontmatter_and_custom_keys(self):
        path = self.write("prd.md", VALID.split("---\n", 2)[2])
        _, report = self.run_tool(path)
        self.assertIn("metadata", self.codes(report))
        custom = self.write("custom.md", "---\nkey: PRD-1\nstate: draft\n---\n\n# 제목\n")
        result, _ = self.run_tool(custom, "--metadata-keys", "key,state")
        self.assertEqual(result.returncode, 0)

    def test_duplicate_definition_and_undefined_reference(self):
        text = VALID.replace("| OPEN-001 | 응답 시간 목표 |", "| OPEN-001 | 응답 시간 목표 |\n| OPEN-001 | 중복 |")
        text = text.replace("목표 미정(OPEN-001)", "목표 미정(OPEN-002)")
        _, report = self.run_tool(self.write("prd.md", text))
        findings = report["files"][0]["findings"]
        self.assertIn(("duplicate-id", "OPEN-001"),
                      {(item["code"], item["message"].split()[0]) for item in findings})
        self.assertIn("정의되지 않은 ID: OPEN-002", [item["message"] for item in findings])
        self.assertNotIn("정의되지 않은 ID: REQ-999", [item["message"] for item in findings])

    def test_reference_followed_by_korean_particle(self):
        text = VALID.replace("목표 미정(OPEN-001)", "OPEN-002의 영향, REQ-003은 미정")
        _, report = self.run_tool(self.write("prd.md", text))
        messages = [item["message"] for item in report["files"][0]["findings"]]
        self.assertIn("정의되지 않은 ID: OPEN-002", messages)
        self.assertIn("정의되지 않은 ID: REQ-003", messages)

    def test_definition_list_forms(self):
        nested = VALID.replace("  - 토글을 켜면 완료 항목이 사라진다.\n",
                               "  - 토글을 켜면 완료 항목이 사라진다.\n- 근거 ID:\n"
                               "  - OPEN-001: 응답 시간 목표 미정\n  - RISK-001: 하위 정의\n")
        result, report = self.run_tool(self.write("nested.md", nested + "\nRISK-001 참조\n"))
        self.assertEqual(result.returncode, 0, result.stdout)
        numbered = VALID + "\n1. NFR-001: 즉시 보인다\n+ RISK-001: 수수료율 변경\n2) SUCCESS-001: 문의 감소\n"
        result, report = self.run_tool(self.write("numbered.md", numbered + "\nNFR-001 RISK-001 SUCCESS-001\n"))
        self.assertEqual(result.returncode, 0, result.stdout)
        _, report = self.run_tool(self.write("duplicate.md", VALID + "\n1. OPEN-001: 중복\n"))
        self.assertEqual(self.codes(report), ["duplicate-id"])

    def test_indented_non_list_child_fills_field(self):
        text = VALID.replace("  - 토글을 켜면 완료 항목이 사라진다.",
                             "  Given 완료 항목이 있다 When 토글을 켠다 Then 사라진다.")
        text = text.replace("- 관련 품질 기대:", "- 화면 상태:\n\n  | 상태 | 표시 |\n  | --- | --- |\n"
                            "  | 켬 | 숨김 |\n- 관련 품질 기대:")
        result, report = self.run_tool(self.write("prd.md", text))
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_links_and_fragments(self):
        self.write("other.md", "# 다른 문서\n\n## 범위 정의\n")
        text = VALID + "\n[ok](other.md#범위-정의) [bad](other.md#없음) [gone](missing.md) [self](#없는-제목)\n"
        text += "[web](https://example.com/x#y)\n"
        _, report = self.run_tool(self.write("prd.md", text))
        messages = {(item["code"], item["message"]) for item in report["files"][0]["findings"]}
        self.assertEqual(messages, {
            ("broken-fragment", "제목 없음: other.md#없음"),
            ("broken-link", "대상 없음: missing.md"),
            ("broken-fragment", "제목 없음: #없는-제목"),
        })

    def test_allowed_root_resolves_symlink(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "prd.md").write_text(VALID, encoding="utf-8")
        link = self.docs / "linked.md"
        os.symlink(outside / "prd.md", link)
        result, report = self.run_tool(link, "--allowed-root", self.docs)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.codes(report), ["outside-allowed-path"])
        _, unchecked = self.run_tool(link)
        self.assertEqual(unchecked["checks"]["allowed_paths"], "not-checked")

    def test_document_id_collides_with_existing(self):
        self.write("old/existing.md", VALID.replace("완료 항목 숨기기", "기존 문서"))
        path = self.write("new.md", VALID)
        result, report = self.run_tool(path, "--existing", self.docs)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.codes(report), ["duplicate-document-id"])
        self.assertEqual(report["checks"]["document_ids"], "checked")

    def test_unreadable_input_exits_2(self):
        result, report = self.run_tool(self.docs / "nope.md")
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(report)
        self.assertTrue(result.stderr.startswith("cannot read:"))


if __name__ == "__main__":
    unittest.main()
