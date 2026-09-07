# Sonsu Marketplace

[한국어](README.md) · [English](README.en.md) · [日本語](README.ja.md)

개발, 리서치, 제품 기획과 글쓰기에 사용하는 Codex 플러그인 모음입니다.
필요한 플러그인만 골라 설치하고, Codex에 평소처럼 작업을 요청하세요.

[설치](#설치) · [플러그인](#플러그인) · [사용 예시](#사용-예시) · [문서](docs/README.md)

## 설치

`codex plugin` 명령을 지원하는 Codex CLI에서 마켓플레이스를 등록합니다.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
```

필요한 플러그인을 설치합니다. 예를 들어 개발 작업에는 Engineering을 사용할 수 있습니다.

```sh
codex plugin add engineering@sonsu-marketplace
```

다른 플러그인은 아래 표의 설치 이름으로 바꿔 설치하세요. Workflow의 설치 예시는 다음과 같습니다.

```sh
codex plugin add workflow@sonsu-marketplace
```

설치 후에는 새 Codex 작업을 시작하세요. 등록된 플러그인 목록은 다음 명령으로 확인할 수 있습니다.

```sh
codex plugin list --marketplace sonsu-marketplace
```

## 플러그인

| 플러그인 | 용도 | 설치 이름 |
| --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | 소프트웨어 변경 설계, 구현, 디버깅과 검증 | `engineering` |
| [Quality Engineering](plugins/quality-engineering/README.md) | 코드 단순화와 유지보수성, 실패 경로, 운영 문제 검토 | `quality-engineering` |
| [Workflow](plugins/workflow/) | Git branch·commit·push, 티켓 작성·수정·상태 관리와 GitHub PR 작업 | `workflow` |
| [Fluent Languages](plugins/fluent-languages/) | 기술 내용을 보존하는 자연스러운 한국어·일본어·영어 작성 | `fluent-languages` |
| [Research](plugins/research/README.md) | 여러 출처 조사, 사실 검증과 근거를 갖춘 답변 작성 | `research` |
| [Prompting](plugins/prompting/README.md) | Codex·ChatGPT·OpenAI API용 프롬프트 작성과 개선 | `prompting` |
| [Product](plugins/product/README.md) | 제품 아이디어 탐색, 사용자 근거 정리, 가설 검증과 PRD 작성 | `product` |
| [Figma Workflow](plugins/figma-workflow/README.md) | Figma 제품 화면, 클릭 가능한 프로토타입과 디자인 품질 검토 | `figma-workflow` |
| [Memory Manager](plugins/memory-manager/README.md) | 명시적으로 호출하는 코딩 에이전트 메모리 점검과 정리 | `memory-manager` |

각 플러그인은 독립적으로 사용할 수 있습니다. 포함된 스킬과 상세 사용법은 위 링크에서 확인하세요.

## 사용 예시

관련 플러그인을 설치한 뒤 Codex에 다음과 같이 요청할 수 있습니다.

| 플러그인 | 요청 예시 |
| --- | --- |
| Engineering | “이 버그의 원인을 찾아 수정하고, 재현 조건으로 검증해 줘.” |
| Quality Engineering | “현재 diff에서 불필요한 추상화와 도달 가능한 실패 경로를 검토해 줘.” |
| Workflow | “현재 변경을 커밋하고 Draft PR을 만들어 줘.” |
| Fluent Languages | “이 일본어 기술 설명을 의미와 코드 식별자를 유지하면서 자연스럽게 다듬어 줘.” |
| Research | “이 두 서비스의 요금과 제한 사항을 공식 자료로 비교해 줘.” |
| Prompting | “이 프롬프트를 Codex에서 바로 쓸 수 있게 개선해 줘.” |
| Product | “이 인터뷰 메모에서 사용자 문제와 근거를 정리해 줘.” |
| Figma Workflow | “이 Figma 화면의 Auto Layout과 프로토타입 연결을 검토해 줘.” |
| Memory Manager | “$memory-manager 현재 프로젝트의 Codex 메모리를 점검해 줘.” |

Codex는 요청 내용과 설치된 스킬의 설명을 바탕으로 필요한 스킬을 선택합니다.
Memory Manager는 `$memory-manager`로 명시적으로 호출할 때만 작동합니다.
여러 플러그인을 함께 사용할 때의 역할은 [스킬 라우팅 문서](docs/architecture/skill-routing.md)에 정리되어 있습니다.

Research의 Exa·Perplexity 연동은 선택 사항이며, 사용 가능한 web·browser·connector와 로컬 자료로도 조사할 수 있습니다.
Figma Workflow의 캔버스 작업에는 공식 Figma MCP 연결과 해당 도구의 필수 스킬이 필요합니다.
설정과 도구 요구사항은 각 플러그인의 문서를 참고하세요.

## 업데이트

등록된 Git 마켓플레이스의 최신 snapshot을 가져옵니다.

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

플러그인을 설치하거나 업데이트한 뒤에는 새 Codex 작업을 시작해 최신 스킬 목록을 불러오세요.

<details>
<summary>이전에 같은 스킬을 설치했다면</summary>

다른 마켓플레이스의 `fluent-languages`나 standalone `prompt-builder`, `product-discovery`, `to-prd`를
설치했다면 같은 이름의 스킬이 중복되지 않도록 기존 복사본을 먼저 제거하세요.

</details>

## 개발 및 기여

플러그인을 수정하거나 추가하려면 저장소를 clone하고 로컬 마켓플레이스로 등록합니다.

```sh
git clone https://github.com/sonsu-lee/sonsu-marketplace.git
cd sonsu-marketplace
codex plugin marketplace add .
codex plugin list --marketplace sonsu-marketplace
```

GitHub 소스와 로컬 경로는 같은 `sonsu-marketplace` 식별자를 사용하므로 한 환경에서는 한 가지 방식으로 등록합니다.

- [플러그인 추가 가이드](docs/guides/adding-a-plugin.md) — 디렉터리 구성과 manifest 등록
- [문서 안내](docs/README.md) — 아키텍처, 설계 결정과 플러그인 계약
- [업스트림 업데이트 런북](docs/runbooks/updating-upstream-plugin.md) — 원본과 로컬 변경을 구분해 갱신하는 절차
- [평가 도구](evals/) — 언어 출력, 스킬 라우팅과 플러그인 품질 검증
- [GitHub Issues](https://github.com/sonsu-lee/sonsu-marketplace/issues) — 버그 보고와 개선 제안

<details>
<summary>저장소 구조와 검증 명령</summary>

### 저장소 구조

```text
sonsu-marketplace/
├── .agents/plugins/marketplace.json  # 플러그인 목록
├── plugins/
│   └── <plugin>/
│       ├── .codex-plugin/plugin.json # 플러그인 정보
│       └── skills/                  # 스킬과 참고 자료
├── docs/                            # 유지보수 문서
└── evals/                           # 평가 fixture와 검증 도구
```

### 검증

저장소 루트에서 다음 정적 검사를 실행합니다.

```sh
find .agents plugins evals -name '*.json' -print0 \
  | xargs -0 -n1 python3 -m json.tool >/dev/null
python3 plugins/fluent-languages/scripts/render-skills.py --check
python3 evals/language-style/eval.py validate
python3 -m unittest -v evals/language-style/test_eval.py
git diff --check
```

이 명령은 JSON 구문, 생성된 스킬의 정본 일치 여부와 평가 fixture·runner의 구조를 확인합니다.
실제 모델의 스킬 선택이나 출력 품질은 별도 검증이 필요합니다. 플러그인 구조를 변경했다면
격리된 Codex 환경에서 마켓플레이스 등록, 플러그인 설치와 스킬 노출도 확인하세요.

마켓플레이스 형식은 [OpenAI 공식 플러그인 패키징 문서](https://developers.openai.com/plugins/build/plugins)를 따릅니다.

</details>

## 라이선스와 출처

저장소 전체에 공통으로 적용되는 root-level 라이선스는 현재 선언하지 않았습니다. 각
플러그인의 범위는 다음과 같이 구분합니다.

- Engineering에는 [MIT 라이선스](plugins/engineering/LICENSE)가 적용됩니다.
- Quality Engineering은 여러 고정 upstream을 기반으로 하며 [Apache-2.0 라이선스](plugins/quality-engineering/LICENSE), [NOTICE](plugins/quality-engineering/NOTICE), [출처 mapping](plugins/quality-engineering/UPSTREAM.md)과 [MIT 원문 고지](plugins/quality-engineering/THIRD_PARTY_NOTICES.md)를 유지합니다.
- Workflow에는 현재 별도의 라이선스를 선언하지 않았습니다.
- Prompting에는 현재 별도의 라이선스를 선언하지 않았습니다.
- Product에는 현재 별도의 라이선스를 선언하지 않았습니다.
- Memory Manager는 독자 작성 플러그인이며 현재 별도의 라이선스를 선언하지 않았습니다. 설계 참고 출처는 [UPSTREAM.md](plugins/memory-manager/UPSTREAM.md)에 기록합니다.
- Figma Workflow는 외부 파일을 복사하지 않은 독자 작성 플러그인이며 현재 별도의 라이선스를 선언하지 않았습니다. 검토한 출처와 비복사 원칙은 [UPSTREAM.md](plugins/figma-workflow/UPSTREAM.md)에 기록합니다.
- Fluent Languages의 라이선스와 원본별 출처는 [LICENSE](plugins/fluent-languages/LICENSE), [UPSTREAM.md](plugins/fluent-languages/UPSTREAM.md)와 [THIRD_PARTY_NOTICES.md](plugins/fluent-languages/THIRD_PARTY_NOTICES.md)에 기록합니다.
- Research는 기준 원본에서 라이선스 파일을 확인하지 못했으며 사용 허가를 추정하지 않습니다. 기준 commit과 포함 범위는 [UPSTREAM.md](plugins/research/UPSTREAM.md)에 기록합니다.
