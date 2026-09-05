# Research 원본 출처

`skills/research/`는 아래 원본 저장소의 한 skill subtree를 독립 Codex 플러그인으로 패키징한
것입니다.

- 원본 저장소: <https://github.com/sonsu-lee/skills>
- 기준 커밋: [`e8313cb43b8913a47b1d2f5997d1fdc877344660`](https://github.com/sonsu-lee/skills/commit/e8313cb43b8913a47b1d2f5997d1fdc877344660)
- 원본 플러그인 버전: `0.7.0`
- 원본 subtree: `skills/research/`
- 원본 Git tree: `d49869e56357e14c6ee2630c006d0ed09b086697`
- 가져온 날짜: `2026-09-02`
- 라이선스: 기준 커밋의 저장소 루트와 subtree에 `LICENSE` 또는 `COPYING` 파일이 없으므로
  별도 라이선스를 추정하지 않습니다.

## 기준선 포함 범위

다음 8개 파일은 기준 커밋의 `skills/research/`에서 내용과 실행 권한을 변경하지 않고
가져왔습니다.

- `SKILL.md`
- `agents/openai.yaml`
- `evals/cases.json`
- `evals/rubric.md`
- `references/code-research.md`
- `references/evidence-policy.md`
- `references/tool-routing.md`
- `references/workflow-integration.md`

`plugins/research/.codex-plugin/plugin.json`, 이 플러그인의 `README.md`, 이 파일과 marketplace
등록은 독립 배포를 위한 로컬 wrapper이며 원본 subtree의 일부가 아닙니다. 원본 저장소의
공통 평가 harness, 다른 skills와 플랫폼별 파일은 runtime에 필요하지 않아 포함하지 않았습니다.

## 기준선 검증

원본과 로컬 subtree의 상대 경로, regular file mode와 SHA-256을 비교합니다. 기준선 8개
파일을 POSIX 상대 경로로 정렬하고 각 행을 `0o644 <file SHA-256> <relative path>`로 만든 뒤,
UTF-8 LF로 연결하되 마지막 LF는 붙이지 않습니다. 이 바이트열의 SHA-256은 다음과 같습니다.

```text
23295810086d4bd2cc594472714c0d7af3a6564e6753738f7e20c87ed680306c
```

로컬 정책 변경은 이 기준선 commit 다음의 별도 commit에서 수행합니다.

- 기준선 commit: `8b77d22a8faebb331ed3bfdb9e2ee799e209e48f`

## 로컬 변경

`0.7.0-sonsu.1`에서는 원본의 조사·증거·보안 계약을 유지하면서 다음 정책을 적용합니다.

- Research를 다른 플러그인이나 standalone skill 없이도 실행할 수 있는 독립 플러그인으로 유지합니다.
- Exa와 Perplexity를 선택적 공급자로 취급하고, Codex가 관리하는 연결과 사용자가 직접
  구성한 API·CLI adapter의 자격 확인을 분리합니다.
- 공급자별 고정 순서 대신 조사 목적에 따라 기본 공급자를 고르고, 필요한 경우에만 두
  공급자를 교차 검증에 사용합니다.
- 외부 표현 스킬 이름을 호출하지 않고 Research 자체의 출력 계약으로 결과를 작성합니다.
- 관리형·직접 연결, 단독 설치와 근접 오호출 사례를 평가 fixture에 반영합니다.

`0.7.0-sonsu.2`에서는 외부 코드 패턴 검색과 반복 조사에 다음 로컬 정책을 추가합니다.

- 검색을 증거 역할별 query family로 분리하고 bounded brute force, provider cap·pagination과
  artifact 계보 중복을 명시적으로 다룹니다.
- popularity가 아니라 동일 commit의 production call path, 테스트, 실패 의미와 라이선스를 먼저
  확인하는 hard gate를 적용합니다.
- query fingerprint, immutable artifact ID, mutable fact 재검증과 rubric version에 따라 기존
  근거를 다시 내려받지 않고 재사용할 수 있게 합니다.
- 영속 저장은 기본 `off`로 유지하고, 승인된 절대 경로에서 metadata-only SQLite `cache`와
  명시적으로 승격한 `catalog`만 사용합니다.
- 코드 검색 및 cache 재사용·기본 read-only 경계를 평가 fixture에 추가합니다.

`0.7.0-sonsu.3`에서는 공급자 선택을 첫 검색 전에 수행하고 검색 목적이 바뀔 때 재판단합니다.

- 기술 주제 자체를 Exa 선택 근거에서 제외하고, 넓은 미지의 후보 발견과 정확한 사실·현재 비교를 구분합니다. 애매한 일반 검색은 Perplexity를 우선합니다.
- `lookup`도 공개 검색이 필요하면 같은 선택 기준을 적용하며 검색과 원문 읽기를 분리합니다.
- 관리형 공급자의 첫 필요한 읽기 호출로 인증·가용성을 확인하고, 일시 실패를 이후 작업에 고정하지 않습니다.
- 공급자 전용 스킬과의 선택 충돌을 줄이기 위한 사용자 소유 호스트 지침 예시와 단독·동시 설치 평가 사례를 제공합니다. 전역 파일이나 설치 캐시는 자동 수정하지 않습니다.

변경된 파일의 구체적인 차이는 기준선 commit과 현재 버전 사이의 Git diff로 추적합니다.
