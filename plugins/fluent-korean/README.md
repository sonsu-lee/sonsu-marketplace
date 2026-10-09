# Fluent Korean

[im-not-ai](https://github.com/epoko77-ai/im-not-ai/tree/92b2936956d65d62ff4b19b75cccad8e3429bf43)를 바탕으로 한국어 글을 새로 쓸 때 AI 티·번역투를 피하고, 기존 글을 의미와 말투를 보존하며 윤문·진단한다.

## 설치

```sh
codex plugin add fluent-korean@sonsu-marketplace
claude plugin install fluent-korean@sonsu-marketplace
omp plugin install fluent-korean@sonsu-marketplace
```

## 스킬

| 스킬 | 사용할 때 | 결과 |
|---|---|---|
| `fluent-korean` | 한국어 블로그·문서·메시지·티켓·PR을 새로 쓰거나 기존 글의 AI 티·번역투를 윤문·진단할 때 | 새 글, 국소 수정본, 진단 근거 또는 검증 상태가 붙은 파일 윤문본 |

일반 대화 답변·단순 맞춤법 교정·번역은 각 요청에 직접 답한다.

## 사용 예시

```text
fluent-korean으로 “설정이 변경되어진 후 재시작이 필요합니다.”만 다듬어 줘.
```

결과: “설정이 변경된 후 재시작이 필요합니다.” 짧은 국소 수정은 채팅으로 반환하고, 파일·정량 윤문은 `_workspace/{run_id}/final.md`와 변경률 검증 결과를 남긴다.

## 구성

| 호스트 | 진입점 | 파일·정량 검증 |
|---|---|---|
| Codex | [단일 호출 스킬](codex/skills/fluent-korean/SKILL.md) | 자체검증과 등급 |
| Claude Code | [다단계 스킬](skills/fluent-korean/SKILL.md) | light·standard·heavy 경로와 `verify_gates.py` |
| omp | 생성된 단일 호출 스킬(`/skill:fluent-korean`) | `verify_change_rate.py`. 30% 이상 경고, 50% 이상 미채택, 실행 오류는 미확인 |

공통 보존 규칙과 패턴의 정본은 `skills/fluent-korean/references/`다. Codex 사본은 같은 파일을 복사하고, omp 패키지는 `scripts/render-omp-compat.py`가 Codex 스킬에서 생성한다. [고정 원본과 포함 범위](UPSTREAM.md) · [라이선스](THIRD_PARTY_NOTICES.md)

## 검증

```sh
python3 plugins/fluent-korean/scripts/build_quick_rules.py --check
python3 plugins/fluent-korean/scripts/build_diagnosis_rules.py --check
diff -r -x file-workflow.md plugins/fluent-korean/skills/fluent-korean/references plugins/fluent-korean/codex/skills/fluent-korean/references
python3 scripts/render-omp-compat.py --check
```
