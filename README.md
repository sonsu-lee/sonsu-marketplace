# Sonsu Marketplace

개인적으로 사용하는 Codex 플러그인을 한곳에서 배포하고 관리하는 마켓플레이스입니다.
개발 방법론, 제품 탐색, Git 산출물, 출력 언어, 리서치와 프롬프트 작성을 서로 독립적인 플러그인으로
나누어 필요한 기능만 설치할 수 있습니다.

## 플러그인

| 플러그인 | 버전 | 역할 | 주요 스킬 |
| --- | --- | --- | --- |
| [Engineering](plugins/engineering/README.md) | `1.0.0` | 의사코드 우선 계획과 단계별 quality gate를 둔 구현, 디버깅, 검토와 검증 | `brainstorming`, `writing-plans`, `using-git-worktrees`, `test-driven-development` 등 14개 |
| [Quality Engineering](plugins/quality-engineering/README.md) | `0.1.0` | 도메인 형태의 구현과 단순성·유지보수성·실패 모드·운용 가능성 검토 | `domain-shaped-code`, `simplify-code`, `review-quality` 등 8개 |
| [Workflow](plugins/workflow/) | `0.7.0` | branch·commit, ticket 생성·lifecycle과 GitHub pull request 작업 | `git-workflow`, `to-ticket`, `ticket-lifecycle`, `to-pr` |
| [Fluent Languages](plugins/fluent-languages/) | `0.1.0-beta.4` | 기술 내용을 보존하는 한국어, 일본어와 영어 출력 지침 | `fluent-korean`, `fluent-japanese`, `fluent-english` |
| [Research](plugins/research/README.md) | `0.7.0-sonsu.2` | 여러 출처의 탐색, 원문 교차 검증과 인용 감사 | `research` |
| [Prompting](plugins/prompting/README.md) | `0.1.0` | Codex, ChatGPT와 OpenAI API용 프롬프트 작성·재작성·최적화 | `prompt-builder` |
| [Product](plugins/product/README.md) | `0.1.0` | 제품 기회 탐색, 근거 종합, 도메인 발견, 검증과 PRD 변환 | `product-brainstorming`, `product-discovery`, `synthesize-product-evidence`, `product-domain-discovery`, `design-product-test`, `assess-product-test`, `to-prd` |

각 플러그인은 다른 플러그인을 설치하거나 먼저 실행했다고 가정하지 않습니다. 여러 영역을
포함한 요청에서는 Codex가 설치된 스킬의 설명과 요청 목적을 바탕으로 필요한 플러그인을 함께
사용합니다. 자세한 책임과 조합 기준은 [스킬 라우팅 문서](docs/architecture/skill-routing.md)에
정리되어 있습니다.

## 설치

### GitHub에서 등록

일반적인 사용 환경에서는 GitHub 저장소를 마켓플레이스 소스로 등록합니다.

```sh
codex plugin marketplace add sonsu-lee/sonsu-marketplace --ref main
codex plugin list --marketplace sonsu-marketplace
```

필요한 플러그인만 선택해 설치합니다.

```sh
codex plugin add engineering@sonsu-marketplace
codex plugin add quality-engineering@sonsu-marketplace
codex plugin add workflow@sonsu-marketplace
codex plugin add fluent-languages@sonsu-marketplace
codex plugin add research@sonsu-marketplace
codex plugin add prompting@sonsu-marketplace
codex plugin add product@sonsu-marketplace
```

등록된 Git 마켓플레이스의 최신 snapshot을 가져오려면 다음 명령을 실행합니다.

```sh
codex plugin marketplace upgrade sonsu-marketplace
```

플러그인을 설치하거나 업데이트한 뒤에는 새 Codex 작업을 시작해 최신 스킬 목록을 불러옵니다.
이전에 다른 마켓플레이스의 `fluent-languages` 또는 standalone
`prompt-builder`, `product-discovery` 또는 `to-prd`를 설치했다면 같은 이름의 스킬이 중복되지
않도록 기존 복사본을 먼저
제거합니다.

### 로컬 저장소에서 등록

플러그인을 수정하거나 검증할 때는 clone한 저장소 루트를 로컬 소스로 등록할 수 있습니다.

```sh
git clone https://github.com/sonsu-lee/sonsu-marketplace.git
cd sonsu-marketplace
codex plugin marketplace add .
codex plugin list --marketplace sonsu-marketplace
```

GitHub 소스와 로컬 경로는 같은 `sonsu-marketplace` 식별자를 사용하므로 한 환경에서는 목적에
맞는 한 가지 방식으로 등록합니다. 저장소 파일을 수정하거나 커밋하는 작업과 Codex에
마켓플레이스·플러그인을 등록하는 작업은 서로 별개입니다.

## 플러그인 경계

| 작업 | 담당 플러그인 |
| --- | --- |
| 소프트웨어 변경의 설계, 구현, 디버깅과 검증 | Engineering |
| 코드의 shape, 단순성, 유지보수성, 실패 모드와 운용 가능성 | Quality Engineering |
| Git branch·commit·push, ticket와 pull request 산출물 | Workflow |
| 한국어·일본어·영어 설명문의 자연스러움과 기술 내용 보존 | Fluent Languages |
| 여러 외부 출처가 필요한 조사와 사실 검증 | Research |
| Codex·ChatGPT·OpenAI API용 프롬프트 산출물 | Prompting |
| 제품 기회, 문제, 근거, 도메인 규칙, 검증과 PRD | Product |

Research의 Exa와 Perplexity 연동은 선택 사항입니다. 사용할 수 있는 전문 provider가 없으면
Codex가 이미 제공하는 web, browser, connector와 로컬 자료로 가능한 범위에서 조사하며,
provider를 자동으로 설치하거나 인증하지 않습니다.

## 저장소 구조

```text
sonsu-marketplace/
├── .agents/plugins/marketplace.json
├── plugins/
│   └── <plugin>/
│       ├── .codex-plugin/plugin.json
│       └── skills/
├── docs/
├── evals/
└── README.md
```

- [마켓플레이스 문서](docs/README.md): 아키텍처, 결정 기록, 제품 요구사항, 가이드, 참조와 런북
- [플러그인 추가 가이드](docs/guides/adding-a-plugin.md): 새 플러그인의 디렉터리와 manifest 등록 절차
- [업스트림 업데이트 런북](docs/runbooks/updating-upstream-plugin.md): 원본 기준선과 로컬 변경을 분리해 갱신하는 절차
- [`evals/`](evals/): 언어 출력과 스킬 라우팅의 fixture 및 정적 평가 도구

마켓플레이스 식별자는 `sonsu-marketplace`, 표시 이름은 `Sonsu Marketplace`입니다. Codex는
저장소 루트의 [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json)에서 각
플러그인의 로컬 경로를 찾습니다.

## 검증

저장소 루트에서 다음 정적 검사를 실행합니다.

```sh
find .agents plugins evals -name '*.json' -print0 \
  | xargs -0 -n1 python3 -m json.tool >/dev/null
python3 plugins/fluent-languages/scripts/render-skills.py --check
python3 evals/language-style/eval.py validate
python3 -m unittest -v evals/language-style/test_eval.py
git diff --check
```

JSON parsing, 생성된 Fluent Languages 스킬의 정본 일치 여부와 평가 fixture·runner의 구조를
확인하는 명령입니다. 정적 검사는 실제 모델의 스킬 선택이나 출력 품질을 증명하지 않습니다.
플러그인 구조를 변경한 뒤에는 격리된 Codex 환경에서 마켓플레이스 등록, 플러그인 설치와
스킬 노출까지 별도로 확인합니다.

마켓플레이스 경로, CLI 등록과 source 형식은 [OpenAI 공식 플러그인 패키징 문서](https://developers.openai.com/plugins/build/plugins)를 따릅니다.

## 라이선스와 출처

저장소 전체에 공통으로 적용되는 root-level 라이선스는 현재 선언하지 않았습니다. 각
플러그인의 범위는 다음과 같이 구분합니다.

- Engineering에는 [MIT 라이선스](plugins/engineering/LICENSE)가 적용됩니다.
- Quality Engineering은 여러 고정 upstream을 기반으로 하며 [Apache-2.0 라이선스](plugins/quality-engineering/LICENSE), [NOTICE](plugins/quality-engineering/NOTICE), [출처 mapping](plugins/quality-engineering/UPSTREAM.md)과 [MIT 원문 고지](plugins/quality-engineering/THIRD_PARTY_NOTICES.md)를 유지합니다.
- Workflow에는 현재 별도의 라이선스를 선언하지 않았습니다.
- Prompting에는 현재 별도의 라이선스를 선언하지 않았습니다.
- Product에는 현재 별도의 라이선스를 선언하지 않았습니다.
- Fluent Languages의 라이선스와 원본별 출처는 [LICENSE](plugins/fluent-languages/LICENSE), [UPSTREAM.md](plugins/fluent-languages/UPSTREAM.md)와 [THIRD_PARTY_NOTICES.md](plugins/fluent-languages/THIRD_PARTY_NOTICES.md)에 기록합니다.
- Research는 기준 원본에서 라이선스 파일을 확인하지 못했으며 사용 허가를 추정하지 않습니다. 기준 commit과 포함 범위는 [UPSTREAM.md](plugins/research/UPSTREAM.md)에 기록합니다.
