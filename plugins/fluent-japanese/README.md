# Fluent Japanese

일본어 업무 문서·일상 메시지·기술 설명을 독자와 목적에 맞게 작성·윤문하고, 기존 문서의 AI 문체를 점수와 근거로 진단합니다.

## 설치

```bash
codex plugin add fluent-japanese@sonsu-marketplace
claude plugin install fluent-japanese@sonsu-marketplace
omp plugin install fluent-japanese@sonsu-marketplace
```

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| [`fluent-japanese`](skills/fluent-japanese/SKILL.md) | 일본어 문서를 작성·윤문하거나 자연도를 진단할 때, 자기 문체를 프로파일로 만들 때 | 완성문과 판단 근거, 진단 점수·구간·이유, 또는 `style-profile.md` |

## 사용 예시

요청: `/fluent-japanese score quick report.md`

`lint.py --json` 결과와 원문을 [`score.py`](skills/fluent-japanese/scripts/score.py)에 넘겨 기계 점수를 계산하고, 문서 맥락에 맞춘 이유 3–5개와 우선 수정 항목을 반환합니다. 원문은 고치지 않습니다. 100자 미만 문서는 점수 없이 `too-short`로 답합니다. 계산 규칙과 출력 필드는 [진단 절차](skills/fluent-japanese/references/diagnose.md)에 있습니다.

## 구성

- `lint.py`·`outline.py`·`terms.py`는 `uv run`으로 실행하며 형태소 분석 의존성을 설치합니다.
- `semantic.py`는 full에서 환경이 허락할 때만 쓰는 opt-in 검출기이며 첫 실행에 약 1GB 모델을 내려받습니다.
- 원본과 로컬 변경은 [UPSTREAM.md](UPSTREAM.md), 라이선스는 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 있습니다.

## 검증

```bash
python3 -B -m unittest discover -s plugins/fluent-japanese/tests -p 'test_*.py'
uv run plugins/fluent-japanese/skills/fluent-japanese/scripts/lint.py --json plugins/fluent-japanese/skills/fluent-japanese/scripts/fixtures/natural.md
```
