# omp와 Codex의 실행 방식

> 영문 정본: [clients.md](clients.md) (`fe462ed` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

## 전용 home

각 클라이언트는 테스트 로그인만 담은 전용 home을 `HOME`으로 지정해 실행한다.
클라이언트마다 하나씩 만들고 한 번만 로그인한다.

```sh
H="$HOME/.cache/skill-evals/homes/omp"
mkdir -p "$H" && HOME="$H" omp login

H="$HOME/.cache/skill-evals/homes/codex"
mkdir -p "$H" && HOME="$H" CODEX_HOME="$H/.codex" codex login --device-auth
```

평가 대상 스킬이나 그 플러그인을 이 home에 설치하지 않는다. 설치된 사본은 기준선
실행에서도 로드될 수 있다. 스크립트는 클라이언트에 `HOME`, `PATH`, 로케일과 터미널
변수만 전달하므로 셸에 있는 토큰은 사용되지 않는다.

## 출력 실행

- **omp**는 `--approval-mode yolo`로 OS 샌드박스 없이 실행한다. 플러그인에 속한
  스킬은 그 플러그인의 사본(`--plugin-dir`) 안에서 실행되므로 플러그인의
  에이전트와 형제 스킬이 존재한다. 두 비교군은 평가 대상 스킬만 다르다. 플러그인
  밖의 스킬은 경로로 지정하고, 스킬이 없는 기준선은 `--no-skills`로 실행한다.
- **Codex**는 `--sandbox workspace-write`로 네트워크 접근 없이 실행하며, 플러그인
  없이 스킬의 경로만 받는다.

둘 다 평가의 입력 파일이 있는 빈 임시 git 디렉터리에서 시작하며, 스킬 사본에서는
`evals/`를 뺀다. Ctrl-C는 클라이언트 세션을 끝내고 진행 중인 실행을 측정되지 않은
것으로 기록한다.

## 트리거 실행

평가할 description을 가진 스킬을 새 프로젝트(`.omp/skills/<name>/` 또는
`.agents/skills/<name>/`)에 두고, 스크립트가 먼저 클라이언트가 이를 탐색하는지
확인한다. skill-creator와 마찬가지로 에이전트의 첫 도구 호출로 판정하며 omp의
`todo`는 무시한다. 스킬을 읽으면 트리거이고, 그 밖의 호출이거나 도구 호출이 없으면
트리거가 아니다. 따라서 비율은 같은 클라이언트와 모델 안에서만 비교할 수 있다.

## 채점과 재작성

같은 클라이언트와 모델에 도구 없이 호출해 수행한다. omp는 `--no-tools
--no-skills`, Codex는 `--ephemeral --sandbox read-only`를 쓴다.

## Python

스크립트에는 Python 3.11 이상이 필요하다. 더 오래된 `python3`에서는 동등한
`uv run --no-project --python 3.12 python ...` 명령을 출력하고 종료하므로, 그
명령을 대신 실행한다.
