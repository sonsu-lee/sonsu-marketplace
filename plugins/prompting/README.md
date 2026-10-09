# Prompting

Codex, ChatGPT, OpenAI API와 Claude Code·Anthropic API에서 바로 사용할 수 있는 간결한 프롬프트를 작성합니다.

## 설치

[마켓플레이스를 등록](../../README.md#설치)한 뒤 설치합니다.

```sh
codex plugin add prompting@sonsu-marketplace
claude plugin install prompting@sonsu-marketplace
omp plugin install prompting@sonsu-marketplace
```

omp에서는 기본 구성에 들지 않는 opt-in 패키지이므로 필요할 때 직접 설치합니다.

다른 플러그인 없이 단독으로 동작합니다.

## 스킬

| 스킬 | 사용할 때 | 결과 |
| --- | --- | --- |
| [`prompt-builder`](skills/prompt-builder/SKILL.md) | 특정 모델·제품에 넣을 프롬프트를 생성·재작성·최적화할 때 | 입력 칸별로 바로 복사할 수 있는 fenced block과 필요한 API 설정 |

prompt engineering 개념 설명처럼 프롬프트 산출물이 없는 요청은 일반 답변으로 처리합니다. 모델·제품별 차이는 [OpenAI 지침](skills/prompt-builder/references/openai-prompt-guidance.md)과 [Claude 지침](skills/prompt-builder/references/claude-prompt-guidance.md)에 있고, 출처 기준은 [UPSTREAM.md](UPSTREAM.md)에 있습니다.

## 사용 예시

요청: “Codex에 넘길 작업 프롬프트를 만들어 줘. `docs/setup.md`의 Python 최소 버전을 3.11로 맞추고 다른 파일은 바꾸지 않게 해 줘.”

결과:

```text
docs/setup.md의 Python 최소 버전 안내를 3.11로 수정한다. 다른 파일은 변경하지 않는다.
완료 조건: docs/setup.md에서 최소 버전이 3.11로 표시된다.
```

## 구성

[작업 연속성 참고 자료](references/continuity.md)는 여러 단계로 이어지는 작업의 계약·진행·근거 위치를 작업 폴더의 `.sonsu/continuity/`에 짧게 기록하고, 같은 session의 컴팩션·재개 후 실제 상태와 대조합니다. 짧은 단발 작업은 기록 없이 완성하며, 파일 쓰기 금지와 기존 승인 범위를 유지합니다.

포함된 `SessionStart` hook은 활성 기록이 있을 때 참고 자료·기록 경로만 전달합니다. 설치 후 CLI의 `/hooks`에서 현재 hook 정의를 검토하고 신뢰해야 실행됩니다. hook을 사용할 수 없으면 위 참고 자료를 읽고 수동으로 재개합니다. helper는 Python 3.9+와 POSIX(macOS/Linux) 환경을 사용합니다. [기록 형식·운영 계약](../../docs/reference/task-continuity.md)과 [검증 범위](../../evals/task-continuity/README.md)를 참고하세요.

## 검증

```sh
python3 scripts/validate_refactor_inventory.py check --plugin prompting
python3 scripts/render-continuity.py --check
python3 -B -m unittest discover -s evals/plugin-compat -p 'test_*.py'
```

모델 선택 사례는 [`evals/skill-routing/cases.json`](../../evals/skill-routing/cases.json)에 있습니다.
