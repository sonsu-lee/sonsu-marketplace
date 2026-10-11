# 경계에 따른 추가 검증

잘못된 입력의 근본 원인을 고친 뒤, 다른 유효한 진입 경로나 신뢰 경계가 같은 결함을 다시
만들 수 있는지 확인한다. 각 검사의 소유 책임과 우회 경로를 기준으로 필요한 보호를 선택한다.
동일한 데이터를 지나는 모든 계층에 같은 검증을 반복할 필요는 없다.

## 보호를 선택하는 순서

1. 잘못된 값의 발생 지점과 소비 경로를 추적한다.
2. 입력의 신뢰 수준이나 책임이 바뀌는 경계와 이미 있는 보호를 확인한다.
3. 확인된 누락·우회 경로를 막는 최소 검사를 소유 경계에 추가한다.
4. 각 추가 검사가 포착해야 하는 입력이나 우회 경로를 재현해 효과를 검증한다.

| 경계 | 맡을 책임 |
| --- | --- |
| 외부 진입점 | 요청 형식과 기본 입력 조건을 검증한다 |
| 업무 동작 | 그 동작에 필요한 불변식을 유지한다 |
| 실행 환경 | 테스트·운영 등 환경별 허용 자원과 작업 범위를 확인한다 |
| 진단 | 실패를 구분할 상태와 호출 정보를 수집한다. 로그는 입력 검증을 대신하지 않는다 |

## 예시

```typescript
function createProject(name: string, workingDirectory: string) {
  if (!workingDirectory || workingDirectory.trim() === '') {
    throw new Error('workingDirectory cannot be empty');
  }
  if (!existsSync(workingDirectory)) {
    throw new Error(`workingDirectory does not exist: ${workingDirectory}`);
  }
  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`workingDirectory is not a directory: ${workingDirectory}`);
  }
  // ... proceed
}
```

이 검사는 입력이 비어 있거나 존재하지 않는 디렉터리인 경우를 다룬다. 이후 작업이 다른
진입점에서 직접 호출된다면 그 경계의 불변식을 별도로 확인한다. 파일시스템 권한·심볼릭
링크·작업 승인 등 다른 계약까지 위 검사 하나로 충족했다고 판단하지 않는다.

테스트에서 Git 작업을 임시 디렉터리로 제한해야 하면 해당 프로젝트의 검증된 경로 경계를
사용한다. 경로 문자열 접두어만 같다는 이유로 허용된 하위 경로라고 판단하지 않는다.
진단 로그는 필요한 디렉터리·현재 위치·호출 스택을 수집하되 민감한 값은 제외한다.

## 과거 사례 기록

원 자료에는 빈 `projectDir` 때문에 소스 디렉터리에서 `git init`이 실행된 사례가 있다.

1. 테스트 준비가 빈 문자열을 만든다.
2. `Project.create(name, '')`가 호출된다.
3. `WorkspaceManager.createWorkspace('')`로 전달된다.
4. `git init`이 `process.cwd()`에서 실행된다.

당시에는 `Project.create()`의 디렉터리 검증, `WorkspaceManager`의 빈 값 검증, 테스트의
임시 경로 제한, 실행 전 스택 기록을 추가했다. 원 결과는 “All 1847 tests passed, bug impossible
to reproduce”였다. 서로 다른 경로·대역·환경에서 각 보호가 문제를 잡았다는 원 기록이며,
현재 모든 변경에 네 계층 검사를 요구하거나 결함이 불가능함을 증명하는 근거는 아니다.
