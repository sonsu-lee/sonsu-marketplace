# omp 직접 설치 Engineering 실행 참고

기본 5개 omp 배포에는 Engineering이 포함되지 않는다. 개발 실행·task·todo·session·review는
omp 순정 기능이 맡는다. 아래 내용은 Engineering을 직접 설치한 선택·legacy 호출자만 적용한다.

현재 omp 세션의 도구 schema와 권한을 확인하고 [실행 계약](agent-execution.md)을
적용한다. 플러그인은 작업·품질 계약을 소유하며 세션·권한·에이전트 실행기를 재구현하지 않는다.

- 설치된 스킬은 `/skill:<name>`으로 호출하며 플러그인 이름 접두어를 붙이지 않는다. 참고 자료의
  `engineering:<skill>`처럼 접두어가 붙은 스킬 표기도 omp에서는 `<skill>`이다. 파일과 Git
  작업에는 현재 노출된 native 도구를 사용한다. `${CLAUDE_PLUGIN_ROOT}`와 `${CLAUDE_SKILL_DIR}`는
  없으므로 플러그인 루트는 bash에서 `realpath skill://<현재 스킬>` 결과의 두 단계 위 디렉터리로 구한다.
- 독립 검토와 역할별 작업은 `task` 도구에 `agent: "<role>"`(예: `general_review`)을 지정해
  실행한다. `engineering:<role>` 형식은 쓰지 않는다. 모델은 사용자 설정
  `task.agentModelOverrides` → 역할 agent frontmatter 순서로 정해지며 호출마다 지정할 수 없다.
  기본값은 [omp 모델 프로필](omp-model-profiles.md)에 있다.
- `Unknown agent`가 반환되면 이 플러그인의 `agents/<role>.md`를 읽어 역할 지침을 brief에 넣고
  기본 `task` agent로 실행한다. 이때 native 역할이 선택됐다고 주장하지 않는다.
- 요청 모델과 관측 모델을 구분해 기록한다. 관리형 gate는 `@smol` 같은 별칭을 사용자 설정으로 해석한
  실제 모델 ID를 요청값으로 저장하므로 관측 모델도 실제 ID로 적는다. 관측하지 못한 모델을 요청값으로
  채우지 않고, 필수 검토의 관측 모델이 요청과 다르면 `blocked`/`not_run`으로 둔다.
- 기본 구성은 native todo·session으로 작업을 이어간다. 이 저장소는 세션 ID 주입 extension이나
  Stop hook을 배포하지 않는다. 직접 설치한 Engineering 호출자가 기존 관리형 gate를 선택하면
  현재 native session-ID를 실제로 관측한 증거가 있을 때만 `--session-id`를 명시하고
  `init --host omp`로 등록한다. 증거가 없으면 gate 실행을 `blocked`/`not_run`으로 기록한다.
  다른 세션, 환경 변수의 추정값이나 최신 디렉터리에서 ID를 추정하지 않는다.
- `todo`, `ask` 등 보조 도구는 현재 세션에 노출된 것만 사용한다.

공식 참고: `omp://task-agent-discovery.md`, `omp://extensions.md`, `omp://skills.md`.
