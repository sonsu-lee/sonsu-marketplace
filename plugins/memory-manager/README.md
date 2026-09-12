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

Codex 실행 예시:

```text
$memory-manager 현재 프로젝트의 Codex 메모리를 점검해 줘. 파일은 바꾸지 마.
$memory-manager 현재 프로젝트의 Codex 메모리에서 확인된 중복과 오래된 명령을 정리해 줘.
$memory-manager 이 경로의 Claude Code 메모리를 정리해 줘: /absolute/path/to/memory
```

Claude Code 실행 예시:

```text
/memory-manager:memory-manager 현재 프로젝트의 Claude Code 메모리를 점검해 줘. 파일은 바꾸지 마.
/memory-manager:memory-manager 이 경로의 Claude Code 메모리를 정리해 줘: /absolute/path/to/memory
```

인자 없이 호출하면 현재 프로젝트의 메모리를 점검합니다. 대상이 여러 개면 대상만 확인합니다.
점검은 읽기 전용이며, 정리를 요청하면 확인된 변경을 반영한 별도 MD 완성본을 만듭니다.
원본 직접 편집은 명시적으로 요청했고 호스트도 허용할 때만 수행합니다. 이미 승인한 범위를
다시 승인받는 고정 단계는 없습니다.

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

## 정리 방법과 결과물

1. 대상 메모리와 실제 로컬 경로를 확인하고, 이번 작업의 정리 방법과 보존 기준을 정리합니다.
2. 근거를 점검해 유지·병합·갱신·제거·보류할 내용을 정리안으로 작성합니다.
3. 정리안의 변경을 반영한 **원본 파일 전체 교체용 `.md`**를 별도로 만듭니다.
4. 완성본을 검증한 뒤 **파일 링크와 원본 메모리의 실제 로컬 절대 경로**를 함께 제공합니다.

완성본 파일에는 메모리 본문만 들어 있습니다. 정리안, 사용 설명과 바깥 코드 블록을 제거하거나
섹션별로 조립할 필요 없이, 파일 내용 전체를 복사해 원본 파일에 전체 선택·붙여넣기·저장하면
됩니다. 한 파일 안에서 특정 프로젝트만 정리했어도 다른 프로젝트의 내용은 원문 그대로 포함해
전체 교체 때 빠지지 않도록 합니다. 여러 파일이면 완성본과 원본 경로를 일대일로 제공합니다.

기존 정리안이 있으면 현재 원본과 대조해 재사용합니다. 원본이 읽기 전용이어도 별도 결과물
쓰기가 허용된 위치에 완성본을 만들 수 있습니다. 기본 상태는
`전체 교체용 MD 제공됨 · 원본 미반영`이며, 파일 생성 자체가 금지된 경우에는 제한과
`완성본 파일 미생성`을 알립니다.

호스트가 수정 노트를 요구하면 지정된 경로·형식을 따르며 기존 요청을 중복 기록하지 않습니다.
수정 노트는 원본의 변경 요청이고, 사용자가 복사할 별도 MD 파일은 수동 교체용 산출물입니다.
원본 직접 편집이 명시적으로 요청되고 허용된 경우에는 백업과 재확인, 반영 후 검증을 수행합니다.

## 출처와 검증

[UPSTREAM.md](UPSTREAM.md)에 검토한 공개 스킬과 공식 문서를 기록합니다. 외부 파일을
복사하지 않고 이 저장소의 승인된 요구사항에 맞춰 작성했습니다. 현재 별도 라이선스를 선언하지
않았습니다. 검증 시나리오는 [평가 안내](../../evals/memory-manager/README.md)를 참고하세요.
