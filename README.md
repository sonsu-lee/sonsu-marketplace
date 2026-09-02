# Sonsu Marketplace

개인적으로 사용하는 Codex 플러그인을 관리하는 마켓플레이스입니다. Superpowers 원본을
개인 정책에 맞게 조정하고, Git·ticket·PR 산출물을 담당하는 Workflow와 한국어·일본어·영어 출력
지침을 제공하는 Fluent Languages, 여러 출처를 검증하는 Research를 독립적으로 운영합니다.

## 등록된 플러그인

| 플러그인 | 버전 | 상태 |
| --- | --- | --- |
| [Superpowers](plugins/superpowers/README.md) | 6.3.0-sonsu.2 | 원본 v6.3.0 기반 개발 방법론 |
| [Workflow](plugins/workflow/.codex-plugin/plugin.json) | 0.4.0 | Git, ticket와 GitHub PR workflow |
| [Fluent Languages](plugins/fluent-languages/.codex-plugin/plugin.json) | 0.1.0-beta.4 | 공통 코어와 언어별 한국어·일본어·영어 출력 지침 |
| [Research](plugins/research/README.md) | 0.7.0-sonsu.0 | 여러 출처의 탐색, 원문 검증과 인용 감사 |

Superpowers의 원본 커밋과 포함 범위는 [UPSTREAM.md](plugins/superpowers/UPSTREAM.md)에 기록합니다.
worktree 감지·생성 흐름과 해당 스킬 파일은 원본을 유지합니다. 스킬 안의 commit 문구를
포함한 모든 Git 변경은 로컬 승인 게이트를 따르며, 문서 라우팅, 계획 저장과 TDD 적용
범위는 [저장소 문서](docs/README.md)에 정의한 개인 정책을 따릅니다. 각 플러그인은 다른
플러그인을 필수로 요구하지 않으며, 여러 영역의 요청은 Codex의 스킬 라우팅으로 조합합니다.

## 저장소 구조

```text
sonsu-marketplace/
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── plugins/
│   ├── superpowers/
│   │   ├── .codex-plugin/plugin.json
│   │   ├── assets/
│   │   ├── skills/
│   │   └── UPSTREAM.md
│   ├── workflow/
│   │   ├── .codex-plugin/plugin.json
│   │   └── skills/
│   ├── fluent-languages/
│   │   ├── .codex-plugin/plugin.json
│   │   ├── sources/
│   │   ├── scripts/
│   │   ├── skills/
│   │   └── UPSTREAM.md
│   └── research/
│       ├── .codex-plugin/plugin.json
│       ├── skills/
│       └── UPSTREAM.md
├── evals/
│   ├── fluent-japanese/
│   ├── fluent-english/
│   ├── language-style/
│   └── skill-routing/
├── docs/
│   ├── architecture/
│   ├── decisions/
│   ├── guides/
│   ├── product/
│   ├── reference/
│   ├── runbooks/
│   └── README.md
├── .gitignore
└── README.md
```

- `.agents/plugins/marketplace.json`에는 마켓플레이스 정보와 플러그인 목록을 정의합니다.
- `plugins/`에는 각 플러그인을 별도 폴더로 보관합니다.
- `docs/`에는 장기간 유지할 아키텍처, 결정, 요구사항, 가이드, 참조와 런북을 보관합니다.
- 마켓플레이스 식별자는 `sonsu-marketplace`, 표시 이름은 `Sonsu Marketplace`입니다.

## Codex에 등록하기

`codex plugin` 명령을 지원하는 Codex CLI에서 저장소 루트를 기준으로 실행합니다.

```sh
codex plugin marketplace add .
codex plugin marketplace list
codex plugin list --marketplace sonsu-marketplace
```

등록 명령에는 `marketplace.json` 파일 경로가 아닌 저장소 루트 경로를 전달합니다.
저장소를 만드는 것만으로 사용자의 Codex 설정에 마켓플레이스가 자동 등록되지는 않습니다.

등록한 마켓플레이스에서 필요한 플러그인을 각각 설치합니다.

```sh
codex plugin add superpowers@sonsu-marketplace
codex plugin add workflow@sonsu-marketplace
codex plugin add fluent-languages@sonsu-marketplace
codex plugin add research@sonsu-marketplace
```

이 저장소의 파일을 수정하거나 커밋하는 작업과, Codex에 플러그인을 설치하는 작업은 별개입니다.
각 플러그인은 하나만 설치해도 해당 기능이 독립적으로 동작합니다. 기존 원격
`fluent-languages@fluent-languages`를 사용 중이라면 같은 이름의 스킬이 중복되지 않도록
기존판을 제거한 뒤 로컬판을 설치합니다.

## 플러그인 추가하기

플러그인 디렉터리, 매니페스트와 마켓플레이스 등록 절차는
[플러그인 추가 가이드](docs/guides/adding-a-plugin.md)를 따릅니다.

## 형식 확인

저장소 루트에서 JSON 문법을 확인할 수 있습니다.

```sh
python3 -m json.tool .agents/plugins/marketplace.json
python3 -m json.tool evals/fluent-japanese/cases.json
python3 -m json.tool evals/fluent-english/cases.json
python3 -m json.tool plugins/research/skills/research/evals/cases.json
python3 plugins/fluent-languages/scripts/render-skills.py --check
```

앞의 네 명령은 JSON 문법만 확인합니다. 마지막 명령은 배포용 Fluent Languages 스킬이 공통
코어와 언어별 정본에서 생성된 내용과 일치하는지 확인합니다. 일본어·영어 case 파일의 parsing은
실제 모델 행동 평가가 아닙니다. 플러그인을 추가한 뒤에는 매니페스트와 참조 경로를 검토하고
Codex에서 설치 및 실행까지 확인합니다.

마켓플레이스 경로와 소스 형식은 [OpenAI 공식 문서](https://learn.chatgpt.com/docs/enterprise/plugin-management#supported-formats)를 따릅니다.

## 라이선스

Superpowers 원본의 저작권 고지와 [MIT 라이선스](plugins/superpowers/LICENSE)를 유지합니다.
Fluent Languages의 로컬 라이선스, 원본별 provenance와 제3자 라이선스 고지는 각각
[LICENSE](plugins/fluent-languages/LICENSE), [UPSTREAM.md](plugins/fluent-languages/UPSTREAM.md)와
[THIRD_PARTY_NOTICES.md](plugins/fluent-languages/THIRD_PARTY_NOTICES.md)에 기록합니다.
Research 원본의 기준 커밋, 포함 범위와 라이선스 확인 결과는
[UPSTREAM.md](plugins/research/UPSTREAM.md)에 기록합니다.
