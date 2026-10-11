# 근본 원인 역추적

잘못된 경로의 파일 생성·Git 초기화처럼 오류가 깊은 호출에서 드러날 때, 오류 지점에서
호출자와 입력을 거슬러 올라가 최초 조건을 찾는다. 증상이 발생한 위치와 원인을 수정할
책임 경계가 같은지 확인한다.

## 추적 순서

1. 증상과 오류가 발생한 직접 호출을 확인한다.
2. 호출자와 전달값을 확인하고, 값이 처음 잘못된 지점까지 반복한다.
3. 정상 경로와 입력·순서·환경의 차이를 비교한다.
4. 원인 가설을 작은 재현으로 검증한 뒤 소유 지점을 수정한다.
5. 같은 결함을 우회해서 만들 수 있는 경계가 있으면 [defense-in-depth.md](defense-in-depth.md)에
   따라 필요한 보호를 추가하고 검증한다.

추적할 근거가 부족하면 필요한 호출 정보만 수집한다. 원인을 확정하지 못한 완화 조치는
원인 수정과 구분해 보고한다.

## 예시: 빈 projectDir

빈 `projectDir`이 전달되는 호출 관계를 예로 든다.

```text
Error: git init failed in ~/project/packages/core
```

```typescript
await execFileAsync('git', ['init'], { cwd: projectDir });
```

```text
WorktreeManager.createSessionWorktree(projectDir, sessionId)
  → called by Session.initializeWorkspace()
  → called by Session.create()
  → called by test at Project.create()
```

`projectDir = ''`이 전달되면 Git이 `process.cwd()`에서 실행될 수 있다. 다음 코드에서는
`beforeEach`보다 먼저 `context.tempDir`에 접근하는 테스트 초기화가 빈 값의 시작점이다.

```typescript
const context = setupCoreTest(); // Returns { tempDir: '' }
Project.create('name', context.tempDir); // Accessed before beforeEach!
```

## 호출 정보 수집

수동으로 추적하기 어렵다면 문제 동작 직전에 필요한 경로·현재 디렉터리·스택을 기록한다.
테스트 로그가 숨겨지는 환경에서는 실제 출력에 나타나는 수단을 선택한다.

```typescript
// Before the problematic operation
async function gitInit(directory: string) {
  const stack = new Error().stack;
  console.error('DEBUG git init:', {
    directory,
    cwd: process.cwd(),
    nodeEnv: process.env.NODE_ENV,
    stack,
  });

  await execFileAsync('git', ['init'], { cwd: directory });
}
```

출력 필터 예시는 다음과 같다.

```bash
npm test 2>&1 | grep 'DEBUG git init'
```

스택에서 테스트 파일·줄·반복 입력을 찾는다. 필터 출력은 원인을 좁히는 자료이며 전체 테스트
통과를 입증하지 않는다. 종료 코드와 전체 결과는 별도 보존한다. 민감한 환경 변수나 요청
내용 전체를 로그에 넣지 않는다.

## 오염을 만드는 테스트 찾기

어떤 테스트가 파일을 만드는지 모르면 [find-polluter.sh](find-polluter.sh)의 사용법과 실제
실행 방식을 읽은 뒤 적절한 테스트 환경에서 사용한다.

```bash
./find-polluter.sh '.git' 'src/**/*.test.ts'
```

스크립트는 테스트를 하나씩 실행하고 첫 오염을 찾으면 멈춘다. 테스트 순서·병렬 실행에만
의존하는 문제는 이 방식의 검출 범위 밖일 수 있다.
