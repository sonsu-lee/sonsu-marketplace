# Marketplace v2 구현·검토 기록

Date: 2026-09-13

이 기록은 저장소 변경에 대한 검증이다. 실제 모델 호출과 의미 판정은 [REPORT.md](REPORT.md)에
별도로 기록한다. 원본 실패 리뷰를 수정 후 통과로 바꾸지 않고, 후속 수정·집중 리뷰를 연결한다.
설치된 플러그인 캐시, 사용자 설정과 원격 저장소는 이 작업에서 변경하지 않았다.

## 구현 범위

- Codex 전용 배포로 정리하고 Quality Engineering의 8개 스킬을 Engineering 2.0.0에 통합했다.
  일반 리뷰 진입점은 `engineering:review-quality`다. 역사적 연구·ADR·라이선스는 보존한다.
- 모델·추론·인원 기본값은 `shared/agent-policy/profiles.json`에서 생성한다. 일반 리뷰는
  같은 산출물과 기준으로 fresh Luna `xhigh` 5개, 집중 리뷰는 1개, 고위험 red-team은 별도
  Astra `high`다. 사용자 지정은 우선하고 root 설정을 바꾸지 않는다.
- 직접/위임 실행의 생명주기를 통합했다. Codex의 실행·세션·위임 기능을 사용하고, 관리형
  CLI가 등록된 작업의 DAG·검사·snapshot·review receipt·라운드 예산을 검증한다.
- 확정 도메인 규칙을 타입·상태에 표현하고 실제 외부 경계에서 검증한다. 내부의 도달 불가능한
  경로를 위한 방어 코드나 확인되지 않은 확장성 조건은 추가하지 않는다.
- Operations UI의 적용 가능한 상태·미해결 계약, Research의 독립 작업 지속, Prompting과
  Workflow의 공유 정책 참조, 8개 플러그인의 continuity를 같은 경계에 맞췄다.

결정과 원칙은 [ADR 0014](../../docs/decisions/0014-use-codex-managed-engineering.md)에 있다.

## 독립 검토와 수정

리뷰어 모델/effort는 호출 시 요청값이다. 도구가 underlying model/effort를 노출하지 않으므로
실제 내부 설정을 관측했다고 주장하지 않는다. 원지적은 root가 발생 조건과 근거로 판정했다.
동일 원인의 중복은 합치되 다수결로 유효성을 결정하지 않았다.

| 검토 | 고정 산출물 SHA-256 | 결과와 적용 범위 |
| --- | --- | --- |
| 최초 전체 리뷰, Luna xhigh 5개 | `f154ae31a10413eb118e1c4213f3615ff460ffd6df3b9ad74b13cf9e7647b953` | 원본 5개 모두 `failed`; 관리형 게이트·평가 실행기·일부 경로 문구의 실제 결함을 수정 대상으로 채택 |
| 게이트·정책 수정 집중 리뷰, Luna xhigh 1개 | `b32fa43cdac24316a7eeb93f077a2111974de35cc0d249093f75c07ed121f850` | `passed`; G1–G6 및 D1–D5 해결, 새 blocking finding 없음. 평가 실행기는 이 집중 범위에서 제외 |
| 평가 실행기 전체 리뷰, Luna xhigh 5개 | `b32fa43cdac24316a7eeb93f077a2111974de35cc0d249093f75c07ed121f850` | 원본 5개 모두 `failed`; 정상 합성 경로·숨겨진 평가 조건 노출·완료 판정·원자료 결합·보고 집계를 수정 대상으로 채택 |
| 평가 실행기 수정 집중 리뷰, Luna xhigh 1개 | `4cfc342a995ea4c2972dbe0a8d925f64bc7b2e789fab184d6ae2073ea43979d1` | `passed`; E1–E5 및 E8–E21 해결, 새 finding 없음 |
| 실제 native 실행에서 발견한 추가 반례 | `exact-final-20260913T014730-65080`의 원출력·trace | 판정자 정책 파일 누락, 생성 시도/성공 ID 집계, 역할·권한·capacity 조건, Node 실행 환경의 반례를 보존하고 후속 수정으로 연결 |
| Native 수정 집중 리뷰, Luna xhigh 1개 | `d2648f6186e1a3be3305654622b556e28b5af7c40abdc4121737cbd8db91c10a` | `passed`; 정책 입력·성공 ID와 원결과·역할·capacity·Node/npm 격리·공통 실행 계약을 검증. 새 native 의미 검증은 별도 실행 |
| Native staging/제외 설정 집중 리뷰, Luna xhigh 1개 | `89dce3f8c4398e93957c30826bc6b5e2d681a4dcdd0f538c780771705e4d0747` | `passed`; N9/N10 해결. 테스트 수치 문구의 비차단 P2는 현재 기록에 반영. 이후 namespace 사전 검사 보정은 별도 추가 검토 |
| Namespace 사전 검사 추가 집중 리뷰 | `c7bffa54e00033f237f43ff84af6f6c11781ea9d0781b5c5765ac9c901d65b44` | `passed`; 실제 namespaced discovery와 0회 모델 호출 preflight를 대조 |
| 집중 리뷰 수집·범위 문구 리뷰 | `b157f30e7072c50abb8ac9f0972ff359797cc0f065f1603d509c118c1fe146c9` | 정적 delta `passed`; 실제 동작에서는 docs 3/3 통과, provider 범위 보존 3/3 실패로 별도 기록 |
| 집중 리뷰 범위 선별·평가 절차 보완 | `8d0574844a552600164c3e3d321a1303cc7589f010093bf560657f049d5b757f` | 정적 `passed`, 전체 `inconclusive`; 실제 native 동작 근거는 후속 평가에 반환 |
| 평가 입력층 정리 집중 검토 | `8b651695c9cd6f22bdb16db6d10de22f13757a8adad7c65712e24afd1dcd6af1` | `passed`; 모호한 필수 oracle 제외, 동일 명시 사례의 근거 부분 재사용과 과거 실패 보존을 검증 |
| 최종 별도 red-team, Astra high 요청 | bundle `b834ef0e7bf26bdbf27c77fbe8f8e841c91c5c70eefb1e5d3eae45e08007a46d` | `survives_challenge`; 현재 목표의 반례·필수 근거 공백 없음. [원본 보고서](FINAL-REDTEAM.md) |

게이트 수정은 중단된 검사 복구, 검사 삭제를 통한 실패 우회 방지, 모든 후속 집중 리뷰의
미해결 blocking finding 누적, 정책 변경 시 근거 무효화, 외부 JSON 진단과 lease 정리를 다룬다.
검사 명령의 정당한 수정은 출처가 있는 revision으로 허용하되 이전 근거를 무효화한다.

평가 실행기 수정은 정상 worker→합성→판정→보고 전체 경로, 부분 생성 입력의 원자적 게시,
완료 trace와 final 출력 검증, 관측된 모든 collaboration event의 통제 조건 검사, 실행 코드의
digest 고정, 입력·출력 provenance, 별도 hidden-oracle 판정과 metric 집계를 다룬다.

의도적으로 심은 fixture 결함을 제품 버그로 고치라는 지적, 내부 상태 파일을 적대적으로
통째로 위조하는 상황을 위한 중복 검증 요구, canonical cohort 설정을 Python에 다시 하드코딩하라는
지적은 적용 계약에 맞지 않아 기각했다. 이러한 기각은 실제 외부 입력 검증을 생략하는 근거가 아니다.

실제 실행에서는 24개 리뷰와 12개 통합 호출이 완료됐으며 root가 12개 통합 원출력을 모두 읽고
두 seed의 근거를 전체 코드 품질 원칙과 대조했다. 통합 workspace의 `code-quality.md` 누락은
별도 결함으로 남긴다. 기존 비교는 두 seed와 당시 공통 도구 조건의 관측이며, 수정 후 전체 정책
패키지로 실행한 결과라고 바꾸지 않는다. 오탐·중복 지표는 통합 후 결과다. 통합에서 기각된
추가 제안이 있으므로 원리뷰의 오탐이 0이었다는 의미가 아니다.

기존 동작 smoke는 일반 리뷰 5명 완료와 기계적 변경을 확인했다. 집중 리뷰의 무위임·미완료,
모호한 문서 관점 요청에서의 잘못된 생성 집계, Node shim 부재로 차단된 동작 검증도 보존한다.
마지막 사례가 테스트를 실행하지 못한 채 완료 게이트를 통과시키지 않은 것은 올바른 차단이다.
외부 연락 금지와 내부 위임 권한을 구분하고 root 역할을 명시하되, 평가 정답인 인원·모델·경로를
prompt에 넣지 않는다. 고정 runtime capacity와 명시적인 Node 실행 환경으로 영향을 받는 사례를
다시 검증한다.

이 관찰을 Engineering 공통 실행 계약에도 반영했다. 판정자에게 참조된 품질 원칙까지 전달하고,
생성 횟수와 성공한 ID를 구분하며, 후속 wait/resume와 완료 결과를 같은 ID에 연결한다.
host가 지원하면 도구 결과 참조·Code Mode로 이 연결을 전달하고 관측되지 않은 상태를 추정하지 않는다.
집중 리뷰 진입점에서도 이 공통 계약을 읽도록 연결했다. 평가기의 routing 통과는 실제 성공 ID와
같은 ID의 비어 있지 않은 완료 결과를 요구한다. Parent turn 완료와 리뷰 게이트 통과는 구분한다.
Node/npm 버전 확인과 실행은 격리된 HOME·설정·cache 경로에서 수행하고 전역 설정을 변경하지 않는다.
정책 보완 후 종합 판단 12회가 모두 완료됐다. root가 원출력을 모두 읽었고 각 결과는 두 seed를
보존하며 근거 없는 추가 요구를 제외했다. 이는 기존 24개 worker를 재사용한 새로운 종합 판단이다.

수정 환경의 자연어 smoke 6개는 모두 필요한 인원과 같은 ID의 원결과 회수를 확인했다.
5개는 의미 판정도 통과했고, 동작 변경은 RED→GREEN 4개 테스트와 독립 리뷰 5개가 통과했지만
관리형 게이트가 환경 문제로 차단됐다. 평가 복사본에 `.codex-plugin/plugin.json`이 빠졌고,
Git 제외 규칙이 이미 있어도 helper가 쓰기를 요청했다. 이 둘은 N9/N10으로 별도 수정한다.
패키지 메타데이터를 제공하고 평가 환경에서 정확한 제외 규칙을 준비한다. helper는 기존 규칙을
읽어 확인한 경우 쓰기를 생략하며, 필요한 규칙을 추가할 수 없을 때의 차단은 유지한다.
root의 읽기 전용 파일 재현은 수정 전 두 helper 모두 실패, 수정 후 모두 성공·기존 바이트 보존을
확인했다. 후속 집중 리뷰는 통과했다. 메타데이터가 바꾼 namespaced discovery의 영향을 확인하기 위해
완전한 패키지로 자연어 6개 사례를 다시 실행했다. 동작 변경은 continuity 기록, RED→GREEN
4개 테스트, 5개 독립 리뷰 원결과, 관리형 검사·판정·complete-unit과 종료까지 실제 통과했다.
일반 리뷰·집중 실패 모드·기계적 변경도 통과했다. 문서 리뷰의 결과 미수집과 provider 리뷰의
요청 범위 이탈은 N11로 남겼다.

N11에서는 기존 수집 절차와 집중 리뷰 진입점 4곳만 보완했다. 정적 집중 리뷰 후 사전 등록한
문서·provider 각 3회의 새 실행을 모두 완료했으며, 모든 실행이 같은 ID의 완료 원결과를 수집했다.
문서 사례는 3/3 의미 판정도 통과했으나 provider는 부모 최종 답변이 무관한 webhook 결함을
추가하여 3/3 실패했다. 하위 결과만 읽고 trial 1을 통과로 보고한 평가자 오류는 root가 부모
최종 답변을 직접 읽어 정정했다. 생성·하위 완료·최종 답변의 범위 준수는 별개로 판정한다.
후속 수정은 공통 기준의 최종 후보 선별, 일반/집중 리뷰 템플릿과 스킬 평가 절차에 모았다.
요청 대상과 실제 계약·호출·데이터·자원 관계가 없는 지적은 root 자체 후보에도 제외 기준을
적용한다. 별도 정적 집중 검토에서 관련 caller·boundary 지적을 여전히 허용함을 확인했다.
이전 실패는 보존하며 동일 provider 원문 3회와 문서·집중 실패 모드·일반 리뷰 각 1회의
사전 등록 검증을 수행한다. 원문의 “오류 경로”에는 넓은 해석 가능성도 있어, provider-only
판정은 이 평가의 사전 정의 범위에 따른 관측으로 한정한다. 해당 6회는 모두 routing을
통과했으며 provider-only 기준 충족은 1/3, 문서·집중 실패 모드·일반 리뷰는 각각 1/1이다.
이 수치만으로 스킬의 scope 결함을 확정하지 않는다. 결과 전에 별도 사전 등록한 파일·함수
명시 사례는 동일 candidate profile에서 1/1 routing·semantic 통과했다. parent와 child 모두
provider cleanup만 보고했으며 기존 표를 대체하거나 합산하지 않는다. 모호한 원문의
의도에 대한 원인 판정은 `inconclusive`로 남긴다. 템플릿은 세 실패 trace에서
직접 읽히지 않았으므로 템플릿 정리를 이번 실패의 입증된 원인 수정이라고 단정하지 않는다.

## 결정론적 검증

| 검증 | 관측 결과 |
| --- | --- |
| Engineering v1/v2 gate suite | 77개 통과. 읽기 전용 제외 설정 수정 후 root 실행 77.387초 |
| 게이트 집중 리뷰의 v2 suite | 독립 검토자가 31개 통과, 86.174초 |
| Operations UI 계약 validator | 50개 통과 |
| Continuity runtime | 19개 통과; 이미 설정된 읽기 전용 제외 파일에서도 checkpoint 저장 확인 |
| Codex packaging | 2개 통과 |
| Design Patterns | 38개 통과; 원본 catalog 553개/12 families 검증 |
| Review/red-team/SDD package와 identity | 관련 shell suite 5개 통과 |
| 공유 생성물 | `render-agent-policy.py --check`, `render-continuity.py --check` 통과 |
| 변경 문서의 상대 링크 | 검사한 변경·신규 Markdown에서 깨진 상대 링크 0개 |
| Native evaluator | Native 수정 집중 리뷰의 18개 통과 이후 staging/namespace 회귀를 추가해 owner 20개 통과; 현행 7개 source case 검증 통과; 모호한 case 제외 후 root 20개 재검증 7.968초; 과거 7/8-case 실행은 각 frozen source에 연결 |

한 번의 v1 검사 timeout은 다른 장기 작업과 동시 실행 중 발생했다. 동일 검사 재실행은
3.6초에 통과했고, timeout 값을 늘리지 않은 당시 수정본 전체 76개 실행도 통과했다. 이후 제외 설정 수정본은 77개가 통과했다.

실제 앱 번들 `codex-cli 0.154.0-alpha.6.2`의 `plugin/list`가 11개 로컬 패키지를 load error 없이
읽었고, `plugin/read`도 11개 모두 성공했다. 총 57개 스킬, Engineering 23개 스킬과 2개 hook
entry를 확인했다. 이는 모델 호출 0회의 메타데이터 검증이며 hook 실행·라우팅의 의미 검증은 아니다.

## 보장 범위

관리형 CLI는 등록된 unit의 진입·완료와 근거 일관성을 검증한다. 임의 도구 호출을 가로막거나
AI 판정의 진실성, 인간 승인, 적대적 파일 변조 방어를 증명하지 않는다. 소스 snapshot은 전체
소스·설정·의존성 manifest를 포함하며 설치된 dependency/cache 환경의 실행 이미지는 아니다.
실제 모델 비교는 작은 합성 fixture의 관측으로 제한하며 보편적인 모델 우열로 일반화하지 않는다.

## 원자료 위치

원자료는 이 작업 환경의 임시 디렉터리에 보존되어 있다. 다른 환경에서는 해당 경로가 없을 수
있으며, 저장소의 요약 표만으로 원리뷰나 실제 모델 실행을 재현했다고 간주하지 않는다.

- 전체 원리뷰: `/tmp/sonsu-v2-review-{1..5}.md`
- Root 판정: `/tmp/sonsu-v2-adjudication.json`
- 게이트 집중 리뷰: `/tmp/sonsu-v2-focused-review.md`
- 평가 실행기 전체 원리뷰: `/tmp/sonsu-v2-eval-review-{1..5}.md`
- 평가 실행기 root 판정: `/tmp/sonsu-v2-eval-adjudication.json`
- 평가 실행기 집중 리뷰: `/tmp/sonsu-v2-evaluator-focused-review.md`
- 실제 패키지 목록: `/private/tmp/sonsu-v2-native-packaging-p9_v4n6z/plugin-list.json`
- 실제 패키지 상세: `/private/tmp/sonsu-v2-native-package-details-ruv19vy8/`

- Native 반례 판정: `/tmp/sonsu-v2-native-adjudication.json`
- Native 수정 집중 리뷰: `/tmp/sonsu-v2-native-repair-review.md`

- Native staging/제외 설정 집중 리뷰: `/tmp/sonsu-v2-sandbox-repair-review.md`

- Namespace 추가 집중 리뷰: `/tmp/sonsu-v2-sandbox-preflight-review.md`
- N11 정적 집중 리뷰: `/tmp/sonsu-v2-review-closure-review.md`
- N11 반복 실행: `/tmp/sonsu-v2-native-eval/n11-focused-validation-20260913T035015-30160/report.md`

- N11 범위 진단: `/tmp/sonsu-v2-n11-diagnosis.md`
- 범위 선별 보완 집중 리뷰: `/tmp/sonsu-v2-scope-repair-review.md`

모호한 provider 입력의 필수 narrow 기대는 `invalid_oracle_setup`으로 현행 matrix에서 제외했다.
명시적 provider 사례와 Engineering 전체 파일·fixture·runtime·cohort가 직전 8-case source와
같음을 코드로 대조했고, 현재 matrix가 해당 모호한 항목 하나만 제거함을 확인했다. 기존 raw
실패·정적 및 native addendum의 `inconclusive` 판정은 보존한다. 현행 검증은 입력층 정리이며
원래 실패를 성공으로 재분류한 것이 아니다.

입력층 정리의 독립 검토는 `passed`이며 새 필수 지적은 없었다. 원본 source/narrative 검토의
`inconclusive`는 그대로 보존하고, 현재 검증 범위의 연결과 마지막 전체 red-team을 구분한다.

- 입력층 정리 검토: `/tmp/sonsu-v2-oracle-retirement-review.md`

## 최종 완료 기록

별도 Astra high 요청의 최종 검토는 `survives_challenge`다. 검토한 전체 source archive는
`9187252c2dbff3d2576a2178cabedcfdc50954a4f543c20388dcfe1ae42e0dd3`이며, 431개 source의
무결성과 일곱 구성요소를 확인했다. 전체 행의 의미 전수 검토나 모든 자연어 요청의 성공을
뜻하지 않는다. 원본 실패·scope `inconclusive`와 입력층 수정의 근거는 그대로 보존한다.

최종 판정 뒤 변경은 `REPORT.md`, 이 기록과 원본 복사본 `FINAL-REDTEAM.md`의 완료 기록뿐이다.
실행 코드·스킬·모델 정책·fixture·case는 검토한 source와 동일하다. 저장소 소스 반영과 검증이
완료됐으며 설치 캐시·사용자 설정·원격 저장소는 이 작업에서 변경하지 않았다.


## PR 게시를 위한 main 통합

사용자의 PR 게시 요청 후 기존 검증 소스를 `7bff4b6e9935a0305a4cce260ef3b98f7ec2bbc1`에
보존하고, `main`의 문서 구성 개선 `908366872f66b8e60b292da93657859a02672084`를 통합했다.
README의 상세 내용을 담당 문서로 이동한 개선과 Writing·Fluent 지침을 보존하면서, Codex 전용
구조·Engineering 품질 통합·라이선스 경로를 유지했다. Fluent는 `0.1.0-beta.10`, Writing은
`0.2.0-beta.5`로 배포 버전을 올렸다.

통합 검토 입력은 tree `4dbe9f56f7a741404b9ec14e285683b706151064`, tar SHA-256
`9454d6451d4dc32bb4eb9223c02df657d44c406da367f3610bf5f706375d0c23`이다. 새 문맥의
Luna xhigh 검토는 v2 대비 통합 차이에 한정했다. Writing 책임을 예전 문구로 설명하는
Fluent README·Workflow README·Workflow 조합 참조의 불일치 1건을 `changes_requested`로
보고했고, 해당 세 파일의 각 한 줄을 수정했다. 같은 검토자의 제한된 후속 확인은 `passed`이며
새 전체 리뷰가 아니다. 최종 내용 tree는 `075b28b213f83c5665c86c4125bffab61e4f2e24`이고,
이후 변경은 이 검증 기록과 REPORT의 관측 범위 안내뿐이다.

- 원본 국소 리뷰: `/tmp/sonsu-v2-pr-integration-review.md`, SHA-256 `642bb65b25ec872b21ee29672d6814f37875d9f383fe2277c46cbb3e5f549784`.
- 수정 확인: `/tmp/sonsu-v2-pr-integration-closure.md`, SHA-256 `13b04595e9af271f1d408bdf17e58e7f0da96e6ef6cdc2c30427a7b642b86bda`.
- 통합 후 패키징 2개·언어 평가기 15개 테스트, 언어 사례 validation, 변경 JSON 34개 파싱,
  agent-policy·continuity·Fluent 생성 결과 검사, 상대 링크와 diff 검사가 통과했다.
- 관리형 게이트 실행 코드·모델 정책·marketplace-v2 사례 및 평가기 코드는 기존 v2 커밋과
  byte-identical이다. Native 전체 matrix와 red-team을 새로 실행하지 않았으며 기존 고정 근거와
  이번 국소 검증을 구분한다. `/tmp` 위치는 로컬 원본 식별자이고 원격 첨부가 아니다.
