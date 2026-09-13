# 최종 독립 red-team 검토

Verdict: survives_challenge

Review performed: yes

Bundle: `/tmp/sonsu-v2-final-audit-complete-redteam.md`

SHA-256: `b834ef0e7bf26bdbf27c77fbe8f8e841c91c5c70eefb1e5d3eae45e08007a46d`

반환 대상: root 조정자. 현재 필수 수정이나 재승인으로 반환할 반례는 없다.

## 판정 근거

원래 목표인 Codex 전용 Engineering 통합, 위험에 따른 검증, root 소유 위임, 관리형 근거 게이트와 실제 native 평가가 현재 해법에 연결되어 있다. 목표 달성을 무효화하거나 실질적으로 훼손하는 현재 반례는 확인하지 못했다. 과거 실패를 통과로 다시 분류하지 않고, 구현 수정·입력 오류 수정·후속 검증의 범위를 구분한 상태에서 판정한다. 이 판정은 모든 모델 실행의 성공이나 보편적 모델 우열을 뜻하지 않는다.

일곱 구성요소는 모두 존재하고 비어 있지 않다. 묶음 전체 digest를 직접 대조했고, whole-change에 있는 현재 소스 431개를 각 `Bytes` 경계로 읽어 내장 SHA-256과 대조한 결과 모두 일치했다. 이는 소스의 완전한 내장·무결성 검사이며 431개 파일의 모든 행을 의미적으로 전수 검토했다는 주장은 아니다.

## 목표·현재 해법·검증의 대응

- **통합·권한·실행 책임:** `original-goal`과 ADR 0014, `using-engineering-skills/SKILL.md`, `executing-plans/SKILL.md`, `subagent-driven-development/SKILL.md`, `shared/agent-policy`를 대조했다. 일반 리뷰와 focused 리뷰는 Engineering에 있고, 직접 실행과 위임 실행은 같은 생명주기를 사용한다. root가 할당하고 worker가 재위임하지 않으며, 별도 scheduler나 전체 도구 인터셉터를 만들지 않는 경계가 유지된다. 현재 skill·hook·script의 Claude 참조는 역사적 비교를 실행 설정으로 옮기지 말라는 문구였다. commit·push·PR·설치 캐시 변경을 구현 승인에 포함시키는 현재 계약은 확인되지 않았다.
- **관리형 게이트:** `plugins/engineering/scripts/evidence_gates_v2.py`의 `validate_revision`, `binding`, `review_current`, `evidence`, `complete`, `recover_pending_checks`, `prepare`, `adjudicate`를 읽었다. 계약·정책·선행 receipt·소스 변경을 현재 근거에 연결하고, source snapshot과 설치된 실행 환경 이미지를 구분한다. 필수 check ID 삭제와 review 정책 하향을 거부하고, 같은 gate의 round history를 보존한다. 집중 리뷰는 선택한 전체 라운드 이후의 blocking 지적을 누적하며 해결 근거 누락을 거부한다. 미완료 reviewer는 adjudication을 통과하지 못하고, accepted risk는 별도 completion 상태와 downstream 이력으로 남는다. 초기 G1–G6의 반례와 현재 수정 구조를 대조했으며 과거 실패의 단순 삭제로 통과시키는 경로는 확인하지 못했다.
- **native 실행 근거:** 내장된 complete-package behavior trace에서 잘못된 cwd·누락된 `--mode write` 시도의 실패와 후속 정상 실행이 함께 보존돼 있다. 이후 `close`의 실제 출력은 `ready: true`, 필수 검사 4개 `passed`, reviewer invocation 5개, final review `passed`, completion receipt와 `closed: complete`를 보여준다. 따라서 부모의 완료 서술만으로 성공을 추정한 사례가 아니다. 이 trace는 당시 고정 package의 관측이며 최신 matrix 전체의 새 실행으로 확대하지 않는다.
- **평가 실행기:** `runner.py`의 manifest/result 검증과 `_validated_adjudication`, `controlled_benchmark.py`의 plan·workspace·criteria binding을 대조했다. 실행 없는 row는 semantic/routing pass로 승격할 수 없고, reviewer routing pass에는 성공한 고유 ID와 같은 ID의 비어 있지 않은 완료 결과가 필요하다. raw execution 상태와 이후 의미 판정은 분리돼 있다. controlled 비교는 controller-varying 진단과 분리된 4개 cohort × 3회이며, 원래 24개 worker를 재사용한 policy-complete synthesis 12개를 새로운 worker 실행으로 표시하지 않는다. 작은 두-seed fixture의 ceiling과 `jobs=4` queue 영향도 명시돼 있어, 현재 자료로 Luna5의 일반적 품질·속도 우월성을 주장하지 않는다.

## Scope 실패와 oracle 정리의 독립 판단

`provider-cleanup-routing` 원문의 “provider session cleanup과 오류 경로”는 provider 흐름만을 뜻할 수도 있고 전체 오류 경로로 읽힐 수도 있다. 그 입력에서 webhook 지적을 했다는 사실은 사전 narrow oracle의 실패 근거지만, 그 자체로 현재 skill이 명시된 사용자 범위를 위반했다는 충분한 증거가 되지는 않는다. 기존 0/3·1/3 결과와 원인 귀속 `inconclusive`는 그대로 보존해야 한다.

현재 `cases.json`에는 `src/provider.ts`의 `runWithProvider`와 “그 provider 호출의 오류 경로만”을 지정한 별도 사례가 남아 있다. 내장된 explicit 사례의 parent final은 provider session cleanup만 보고했고, `result.json`에는 생성 ID 1개와 동일 ID의 nonempty completed result가 있다. 이전 scope matrix의 general parent final은 두 seed를 유지했고 docs/focused 결과의 범위도 별도로 기록돼 있다. 이 근거는 단순히 이전 reviewer의 `passed`라는 결론을 인용한 것이 아니라 실제 최종 출력과 실행 관측을 대조한 것이다.

내장된 oracle retirement 전후 자료와 검증 기록상 마지막 수정은 ambiguous case 하나의 제거이며 explicit case·Engineering 파일·fixture·runner·cohort는 유지된다. 따라서 입력층의 `invalid_oracle_setup` 정리와 동일 사례 근거의 부분 재사용은 현재 요구에 맞는 최소 수정이다. 실패한 필수 제품 동작을 숨기기 위해 계약을 낮춘 반례로 판정할 근거는 없다. 사용하지 않는 모호한 사례를 제거했다는 이유만으로 새 전체 native 실행을 임의의 차단 조건으로 만들지 않는다. 과거 scope review의 `inconclusive`를 `passed`로 다시 기록할 필요도 없다.

## 조치할 반례와 필수 확인 사항

조치할 반례: 없음. 현재 근거에서 확인한 필수 검증 공백: 없음.

다음은 관찰 한계이며 현재 승인을 막는 확인된 결함은 아니다.

1. 현행 7-case matrix 전체를 마지막 입력층 수정 후 새로 native 실행한 결과는 없다. 기존 변경 없는 사례의 연결된 근거를 부분 재사용한 판정이다.
2. 관련 caller/boundary finding을 반드시 포함해야 하는 별도 native 사례는 없다. 현재 정적 기준은 실제 대상 계약·호출·데이터·자원 흐름에 영향을 주는 주변 지적을 허용하지만, 그 분기의 runtime 성공률을 이번 자료로 수치화할 수 없다.
3. underlying model·effort는 host에서 관측되지 않았다. 요청값 수락과 실제 내부 설정은 다르며 `unknown`을 유지한다. Native package read 성공은 hook 실행이나 모든 skill의 의미적 성공을 증명하지 않는다.
4. 관리형 CLI는 등록된 unit과 근거의 일관성을 검증한다. 임의 도구 호출의 차단, 적대적인 state 전체 위조 방어, AI 판정의 의미적 진실성까지 보증하지 않는다. 이들은 현재 승인된 해법의 명시적 경계다.
5. 본 검토에서는 추가 모델 호출·외부 조회·전체 테스트 재실행을 하지 않았다. 테스트 수치와 이전 실행은 묶음에 고정된 관측 근거이며, 본 검토자가 새로 실행한 검사는 묶음과 현재 431개 내장 소스의 digest 대조다.

원래 목표 변경, 추가 설계 승인, 임의의 새 검토 횟수 또는 새 산출물은 요구하지 않는다. 보고서 외 소스·Git·설치 환경을 변경하지 않았다.
