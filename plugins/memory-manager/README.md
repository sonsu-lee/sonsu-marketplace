# Memory Manager

필요할 때 명시적으로 호출해 Codex와 Claude Code의 저장된 메모리를 점검하고 정리하는
플러그인입니다. 하나의 `memory-manager` 스킬을 제공합니다.

## 사용

이 플러그인이 포함된 marketplace snapshot을 등록한 뒤 설치합니다.

```sh
# Codex
codex plugin add memory-manager@sonsu-marketplace

# Claude Code
claude plugin install memory-manager@sonsu-marketplace
```

Codex에서는 `$memory-manager`, Claude Code에서는 `/memory-manager:memory-manager`로 명시적으로
호출합니다.

```text
$memory-manager 현재 프로젝트의 Codex 메모리를 점검해 줘. 파일은 바꾸지 마.
$memory-manager 현재 프로젝트의 Codex 메모리에서 확인된 중복과 오래된 명령을 정리해 줘.
$memory-manager 이 경로의 Claude Code 메모리를 정리해 줘: /absolute/path/to/memory
```

인자 없이 호출하면 현재 프로젝트의 메모리를 점검합니다. 대상이 여러 개면 대상만 확인합니다.
점검은 읽기 전용이며, 정리를 요청한 범위에서는 확인된 변경을 진행합니다. 이미 승인한 범위의
수정을 다시 승인받는 고정 단계는 없습니다.

`agents/openai.yaml`의 `policy.allow_implicit_invocation: false`로 Codex의 암묵적 호출을
비활성화하고, `SKILL.md`의 `disable-model-invocation: true`로 Claude Code의 자동 호출도
비활성화합니다. 자동 수집, 세션 종료 hook, 예약 실행과 외부 메모리 서비스는 포함하지 않습니다.
다른 플러그인이나 MCP 연결 없이 동작하며 별도 helper runtime도 필요하지 않습니다.

## 정리 범위

- 같은 범위의 중복 기억을 병합하고 고유한 조건·예외·출처를 보존합니다.
- 현재 근거로 달라졌음이 확인된 사실을 갱신합니다. 오래됐다는 이유만으로 지우지 않습니다.
- 전역 선호와 프로젝트 규칙, 장기 지식과 일시적인 작업 상태를 구분합니다.
- 인덱스의 링크와 주제 파일을 확인하고 불확실한 항목은 보류합니다.

저장소 지시·문서·설정·스킬로의 이동은 제안으로 남깁니다. 파일 전체 삭제, raw transcript·DB
재작성이나 Git 작업은 포함하지 않습니다. 에이전트별 차이는 [Codex 참고 파일](skills/memory-manager/references/codex.md)과
[Claude Code 참고 파일](skills/memory-manager/references/claude-code.md)에서 다룹니다.

## Codex의 수정 노트 방식

현재 호스트가 원본 수정 대신 별도 update note를 요구하면 그 방식으로만 기록합니다.
예를 들어 `memories/extensions/ad_hoc/notes/`가 지정된 환경에서는 허용된 노트를 생성하고
`수정 노트 기록됨 · 원본 반영 미확인`으로 보고합니다. 해당 경로를 모든 Codex 설치에
가정하지 않으며, 원본 반영 여부는 별도 재조회로 확인합니다.

직접 편집이 허용된 환경에서는 변경 전 백업과 재확인, 변경 후 내용·참조 검증을 수행합니다.
백업은 메모리 로딩 경로와 Git 저장소 밖에 둡니다.

## 출처와 검증

[UPSTREAM.md](UPSTREAM.md)에 검토한 공개 스킬과 공식 문서를 기록합니다. 외부 파일을
복사하지 않고 이 저장소의 승인된 요구사항에 맞춰 작성했습니다. 현재 별도 라이선스를 선언하지
않았습니다. 검증 시나리오는 [평가 안내](../../evals/memory-manager/README.md)를 참고하세요.
