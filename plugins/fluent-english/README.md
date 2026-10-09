# Fluent English

영어 메시지와 기술 문서를 독자·목적에 맞게 작성·윤문·검토하고, 필자의 목소리와 보호할 문자열을 확인합니다.

## 설치

```bash
codex plugin add fluent-english@sonsu-marketplace
claude plugin install fluent-english@sonsu-marketplace
omp plugin install fluent-english@sonsu-marketplace
```

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| [`fluent-english`](skills/fluent-english/SKILL.md) | 영어 초안 작성, 가벼운 교정, 문체 검토나 AI 투 문장 정리가 필요할 때 | 요청에 맞는 영어 결과물, 구체적 검토 결과, 필요한 경우 짧은 변경 메모 |

## 사용 예시

요청: “Light-edit this note to a neighbour. Keep the tone: I think your parcel are on my porch. I'll leave it there until you get home.”

결과: “I think your parcel is on my porch. I'll leave it there until you get home.” 수일치 오류만 고치고 hedge와 축약형은 유지합니다.

## 도구

스킬 디렉터리에서 실행하는 읽기 전용 도구입니다. 출력은 편집 판단의 입력이며 자동 수정 명령이 아닙니다.

| 도구 | 확인하는 것 | 종료 코드 |
| --- | --- | --- |
| [`scripts/voice_profile.py`](scripts/voice_profile.py) | 원문·샘플·윤문본의 문장 길이, 축약형·인칭·유보 표현·문장부호 빈도와 전후 차이 | `0` 측정, `2` 입력 오류 |
| [`scripts/validate_preservation.py`](scripts/validate_preservation.py) | 코드, 인용, 링크 대상, frontmatter의 전후 문자열 | `0` 일치, `1` 차이 있음, `2` 입력 오류 |

출처와 로컬 변경 범위는 [UPSTREAM.md](UPSTREAM.md), 라이선스는 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 있습니다.

## 검증

```bash
python3 -B -m unittest discover -s plugins/fluent-english/tests -p 'test_*.py' -v
python3 -m json.tool evals/fluent-english/cases.json >/dev/null
```
