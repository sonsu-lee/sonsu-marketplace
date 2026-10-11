# omp 모델·실행 차이

omp 기본 배포에는 Dev Workflow 역할·gate가 없으며 개발 실행·task·todo·session과 memory는 omp
순정 기능이 맡는다. 리뷰는 Review 플러그인의 스킬이 아래 PR 리뷰 기본값과 순정 `reviewer`·`task`로
실행한다. 이 자료와 `omp-profiles.json`의 역할 표는 Dev Workflow를 직접 설치한 호출자의 참고이며
기본 설치에 설정을 추가하는 절차가 아니다.

OMP PR 리뷰는 순정 `reviewer` 1명을 매 라운드 새로 요청한다. model·effort·memory·isolation·
동시성은 사용자의 기존 native 설정을 유지한다. `@slow` 등 별칭, 이미 등록한
`task.agentModelOverrides`, agent frontmatter와 provider 지원 범위를 읽어 실제 설정을 확인한다.
Codex의 Luna xhigh나 Claude의 Opus medium을 OMP에 자동으로 복사하지 않는다. 기존 설정을
덮는 override 또는 YAML overlay가 기본 실행에 필요하다고 안내하지 않는다.

각 라운드의 현재 요구사항·전체 diff·주변 소스만 새 reviewer 입력으로 전달하고 이전 대화·
finding·구현 서사를 제외한다. 별도 프로세스를 쓰면 resume 없이 새
`omp --no-session -p <brief>`에서 순정 reviewer 호출과 완료 결과 수집을 명시한다.
memory backend와 추가 context provider·hook·외부 memory tool의 실제 제어 상태도 확인하되
설정을 자동 변경하지 않는다. 새 입력과 memory 차단을 구분하고 충족하지 못한 격리는 한계로 남긴다.

`task`의 `isolated`는 파일 공간 격리이며 memory 차단 설정이 아니다. 현재 native 설정에서
지원하는 경로를 쓰고, isolation이 비활성화돼 있으면 이를 자동으로 켜지 않는다. 외부에서 만든
임시 워크트리는 조정자가 결과를 보존하고 검토자 종료·clean 상태를 확인한 뒤 제거한다.
순정 reviewer가 승인된 수정과 반복 종료를 자동으로 관리한다고 가정하지 않으며, 조정자가
지적 판정·승인된 수정·새 전체 리뷰·결과 보존·정리를 담당한다.

사용자가 다른 model·effort를 명시하거나 제한된 비교 실험을 요청한 경우에만 별도 실행에서
정확한 provider/model/effort를 지정한다. 그 실행을 기존 native 설정과 구분해 기록하며 실제
결함 탐지·오탐·완료 시간·사용량 근거 없이 새로운 운영 기본값으로 확정하지 않는다.
stock `reviewer`와 직접 설치한 Dev Workflow·Review의 `general_review`는 다른 agent다. 아래 legacy 별칭은
기존 호출자의 참고이고 stock reviewer의 설정으로 취급하지 않는다. 관측 model·effort·완료 상태와
실행 한계를 기록하며 없는 관측값은 `unknown`이다.
