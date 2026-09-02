# 한국어 문체 후보 평가

이 디렉터리는 한국어 기술 설명문에 적용할 문체 후보를 비교하기 위한 고정 평가 자료다. 평가가 끝나기 전에는 언어 스타일 plugin의 구조나 최종 후보를 확정하지 않는다. 이 자료 자체도 ADR이나 승인된 제품 결정이 아니다.

## 비교 조건

- `C`: 공통 기술 정보 보존 계약만 적용하는 기준선
- `A`: `im-not-ai`에서 생성 단계에 안전한 규칙만 선별한 `im-only`
- `B`: `A` 전체에 문장 성분, 조사·어미, 완결 문장 규칙 세 개만 더한 최소 `hybrid`

세 조건은 [공통 보존 계약](candidates/common.md)을 공유한다. 후보별 고정 지침은 [candidates](candidates)에, 원본 commit과 라이선스 고지는 [SOURCES.md](SOURCES.md)에 있다.

## 평가 구성

Screen은 12개 과제에 `C/A/B`를 각 두 번 실행해 성공한 모델 호출 72개를 만든다. Confirm은 나머지 18개 과제에 `A/B`를 각 두 번 실행해 72개를 만든다. 과제 30개는 다음 여섯 유형에 다섯 개씩 배분한다.

1. 구현 완료와 변경 결과 보고
2. 코드 리뷰와 위험 설명
3. 디버깅·원인 분석과 불확실성 보고
4. 아키텍처 대안과 결정 자료
5. API·CLI·runbook과 번호 절차
6. 기존 기술 문서의 제한적 다듬기

모델은 `gpt-5.6-sol`, reasoning `xhigh`, service tier `priority`로 고정한다. 각 호출은 임시 `HOME`과 `CODEX_HOME`, 읽기 전용 sandbox, 빈 대화 이력을 사용한다. 사용자 auth 파일은 내용을 복사하지 않고 임시 `CODEX_HOME`에서 symlink로만 참조한다. preflight는 설치된 언어·문체 skill, plugin cache와 `~/.agents/skills`가 model-visible prompt에 섞이지 않았는지 확인한다.

## 정적 검증

Python 3.9 표준 라이브러리만 필요하다.

```sh
python3 evals/language-style/eval.py validate
python3 -m unittest -v evals/language-style/test_eval.py
python3 -m py_compile evals/language-style/eval.py evals/language-style/test_eval.py
git diff --check
```

## 실행 순서

manifest와 모든 실행 결과는 기본적으로 repository 밖인 `~/.codex/evals/sonsu-marketplace/language-style/`에 생성된다. `plan`이 출력한 절대 경로를 다음 명령의 `<...>` 자리에 사용한다.

```sh
python3 evals/language-style/eval.py plan --stage screen
python3 evals/language-style/eval.py run --manifest <screen-manifest.json> --workers 4 --retries 1 --timeout 600
python3 evals/language-style/eval.py check --manifest <screen-manifest.json>
```

Screen의 자동 보존 검사에서 기준선 안전 중단 조건이 발생하지 않았을 때만 같은 입력으로 Confirm manifest를 만든다. Confirm은 고정한 Screen manifest의 ID와 candidate, fixture, runner hash가 일치해야 한다.

```sh
python3 evals/language-style/eval.py plan --stage confirm --screen-manifest <screen-manifest.json>
python3 evals/language-style/eval.py run --manifest <confirm-manifest.json> --workers 4 --retries 1 --timeout 600
python3 evals/language-style/eval.py check --manifest <confirm-manifest.json>
```

`pass`와 `fail`은 모델이 정상적으로 응답한 호출이다. `fail`은 자동 보존 검사에서 품질 위반이 발견됐다는 뜻이다. timeout, 인증·실행 오류와 빈 출력은 `not_run`, 잘린 trace나 외부 skill 오염은 `inconclusive`로 분리한다. 후자의 호출은 144개 성공 호출에 포함하지 않으며 원인과 재시도 횟수를 따로 기록한다.

후보 지침, fixture 또는 runner가 Screen 이후 바뀌면 기존 Screen 결과와 새 Confirm 결과를 합치지 않는다. manifest와 raw artifact를 직접 고친 경우에도 hash 검증이 실패한다.

## 블라인드 평가

두 단계가 모두 완결되면 `A/B` 출력 30쌍을 담은 정적 HTML과 별도의 비공개 key를 만든다. 같은 과제의 반복 두 개를 함께 읽고 과제당 한 번 평가한다.

```sh
python3 evals/language-style/eval.py review \
  --manifest <screen-manifest.json> \
  --manifest <confirm-manifest.json>
```

HTML은 후보 이름을 포함하지 않는다. 브라우저에 평가를 저장한 뒤 `JSON 다운로드`로 ratings 파일을 내보낸다. 평가는 기술적 정확성과 완전성, 명료성, 자연스러운 한국어, 간결성, 구조와 어조 적합성을 각각 1~5점으로 기록하고 전체 선호를 왼쪽·동률·오른쪽 중 하나로 고른다.

```sh
python3 evals/language-style/eval.py analyze \
  --manifest <screen-manifest.json> \
  --manifest <confirm-manifest.json> \
  --ratings <ratings.json> \
  --key <private/review-key.json>
```

ratings가 없으면 분석은 `awaiting_human_review`이며 후보를 추천하지 않는다. `B`는 보존 실패가 `A`보다 많지 않고, 비동률 과제 중 3분의 2 이상에서 이기며, 단측 exact sign test가 `p < 0.05`이고, 명료성과 자연스러움이 각각 `+0.25` 이상 개선되는 등 등록된 조건을 모두 만족할 때만 추천한다. 완전한 평가에서 차이가 실질적 동등 구간에 있거나 채택 조건을 만족하지 못하면 더 단순한 `A`를 추천한다. 분석 결과는 추천 자료이며 사용자가 후보를 선택하기 전까지 승인된 결정이 아니다.

## 해석 범위

자동 검사는 literal, 사실 조건, 금지 주장, 숫자, heading 계층, 표·절차 순서와 fenced code를 확인한다. 의미 보존 전체나 자연스러움을 증명하지는 않는다. 이 실험은 개인용 plugin의 선호를 판단하며 한국어 사용자 전체로 일반화하지 않는다. 모델, upstream 규칙 또는 주요 사용 장르가 바뀌면 같은 fixture로 다시 평가한다.
