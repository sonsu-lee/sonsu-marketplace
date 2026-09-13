# Marketplace v2 native evaluation report

## 현재 판정

별도 최종 red-team은 `survives_challenge`로 판정했다. 현재 목표를 막는 반례나 필수 검증 공백은
확인되지 않았다. [전체 판정과 관찰 한계](FINAL-REDTEAM.md)를 함께 보존한다. 역사적
complete-package smoke와 N11 run의 실패 기록은 그대로 유지한다. 후속 scope 수정은 정적 focused review를 통과했고,
원래 provider 문구의 사전 provider-only 해석 기준은 1/3, 명시적인 file/flow 범위 case는 1/1을
충족했다. 원래 문구는 한국어상 더 넓게 읽을 수 있어 그 1/3만으로 제품 skill의 scope 결함을 확정하지
않으며, 원인 판정은 `inconclusive`다. Routing 성공과 semantic/oracle 판정을 계속 분리한다.

| Gate | 판정 | 근거 |
| --- | --- | --- |
| App CLI capability | `pass` | `codex-cli 0.154.0-alpha.6.2`; Luna `xhigh`, Sol `xhigh`, Sol `max` 요청이 `capability-ok` 반환 |
| Evaluator deterministic validation | `pass` | 20개 unit test (현행 7-case 상태에서 root 재검증 7.968초), case validation, diff/link check 통과 |
| Complete-package model-free preflight | `pass` | `.codex-plugin`·hooks 포함, 필수 namespaced skill 8개 발견, loader error 0, model calls 0 |
| Native package metadata read | `pass` | 격리 app-server에서 marketplace plugin 11개와 Engineering skill 23개·hook 2개 읽음 |
| Controlled reviewer comparison | `pass` | 24 worker + policy-complete synthesis 12개; 모든 cohort가 두 seed를 최종 보존 |
| Complete-package natural smoke | `failed` (historical) | 6개 중 4개 pass/pass, docs routing fail 1개, provider semantic fail 1개 |
| N11 focused closure validation | `failed` (narrow oracle) | docs 3/3 pass; provider routing 3/3 pass이나 provider-only 기준 0/3 |
| Scope repair selected matrix | `mixed` | routing 6/6; docs/focused/general pass; 원래 provider-only 기준 1/3, 원인 `inconclusive` |
| Explicit provider scope | `pass` | 명시적 `src/provider.ts/runWithProvider` 범위에서 routing/semantic 1/1 pass |
| Current oracle setup | `pass` | 모호한 필수 case 제외의 독립 검토 통과; 원본 failed/mixed 기록과 동일 명시 case 근거 재사용을 구분 |
| Final release red-team | `survives_challenge` | 고정된 전체 소스·목표·설계·검증·실패 이력을 독립 검토; 필수 수정 요구 없음 |

요청 model·effort는 CLI가 수락했지만 JSONL은 underlying model·effort를 노출하지 않았다. 따라서 아래
모든 표에서 observed model·effort는 `unknown/unknown`이며, 요청값과 관측값을 동일하다고 간주하지
않는다.

## Controlled reviewer 비교

`review-service`에는 두 개의 의도적 seed만 있다.

- `external-payload-cast`: webhook 외부 입력 trust boundary
- `provider-session-leak`: provider 실패 경로의 session cleanup

이 fixture는 배포 제품 코드가 아니다. 내부 typed dispatch guard, 현재 v3 문서 갱신, historical v2
snapshot 재작성은 seed가 아니며 근거 없이 요구하면 false positive 또는 unnecessary change로 판정했다.

원본 비교는 같은 artifact·criteria·도구 조건에서 cohort별 3회 실행했다. `controlled_benchmark.py`가
reviewer를 delegated no-interaction role로 직접 호출했으므로 controller 모델 변경이 reviewer 비교를
오염시키지 않는다. Worker와 synthesis 모두 `jobs=4`였다.

| Cohort | 요청 | fresh reviewer | 반복 pass | 검출 seed/run | misses | 최종 FP | 최종 duplicate | worker call median | team span median |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `luna-xhigh-1` | `gpt-5.6-luna/xhigh` | 1 | 3/3 | 2 | 0 | 0 | 0 | 173.796s | 173.796s |
| `luna-xhigh-5` | `gpt-5.6-luna/xhigh` | 5 | 3/3 | 2 | 0 | 0 | 0 | 151.254s | 331.610s |
| `sol-xhigh-1` | `gpt-5.6-sol/xhigh` | 1 | 3/3 | 2 | 0 | 0 | 0 | 233.133s | 233.133s |
| `sol-max-1` | `gpt-5.6-sol/max` | 1 | 3/3 | 2 | 0 | 0 | 0 | 274.629s | 274.629s |

각 3회 team span은 다음과 같다.

- `luna-xhigh-1`: 173.796s, 175.708s, 112.073s
- `luna-xhigh-5`: 331.610s, 407.476s, 297.355s
- `sol-xhigh-1`: 233.133s, 152.890s, 297.611s
- `sol-max-1`: 274.629s, 330.204s, 245.162s

5인 team은 `jobs=4` 때문에 다섯 worker가 항상 동시에 시작하지 않았다. Team span에는 scheduler queue가
포함되므로 production 5-parallel latency나 모델 속도 순위로 해석할 수 없다. Worker call median과 team
span을 별도로 기록한 이유도 이 때문이다.

최초 12개 Astra/high synthesis는 모두 두 seed를 보존했지만, evaluator가 `review-criteria.md`에서
참조한 `code-quality.md`를 adjudicator workspace에 복사하지 않은 packaging 결함이 있었다. 이 결과는
원본 그대로 보존했고 fixed-code 실행으로 다시 이름 붙이지 않았다. Root가 전체 정책으로 12개 final을
외부 교차 확인해 동일한 두 seed와 불필요한 확장 배제를 확인했다.

정책 packaging을 고친 뒤 원래 24개 worker의 call identity, command/stdin, trace/final, workspace와
입력 digest를 frozen 원본 validator로 재검증하고 worker 호출 없이 synthesis 12개만 새로 실행했다.
새 synthesis는 완전한 원본 정책 파일을 명시적으로 읽었다.

| Cohort | replay synthesis 완료 | 두 seed 보존 | misses | post-synthesis FP | post-synthesis duplicate | median synthesis latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `luna-xhigh-1` | 3/3 | 3/3 | 0 | 0 | 0 | 76.495s |
| `luna-xhigh-5` | 3/3 | 3/3 | 0 | 0 | 0 | 94.767s |
| `sol-xhigh-1` | 3/3 | 3/3 | 0 | 0 | 0 | 54.915s |
| `sol-max-1` | 3/3 | 3/3 | 0 | 0 | 0 | 42.027s |

Root가 replay final 12개를 모두 다시 읽어 `external-payload-cast`와 `provider-session-leak`만 남고,
현재 v3 docs·내부 dispatch guard·history rewrite 요구가 배제됐음을 확인했다. FP·duplicate·unnecessary
change 0은 최종 synthesis 출력에 대한 값이다. 일부 raw worker는 추가 v3 문서·테스트 요구를 제안했고
synthesis가 이를 명시적으로 거절했다. 따라서 이 수치는 개별 raw reviewer 품질이 아니라 reviewer team과
고정 synthesis를 합친 end-to-end 결과다.

두 seed가 전부인 작은 fixture에서 네 cohort 모두 ceiling에 도달했다. 이 표는 보편적인 모델 품질이나
속도 우위를 입증하지 않는다. `luna-xhigh-5`는 이 benchmark 순위와 무관하게 사용자가 승인한 기본값이다.

## Complete-package natural smoke

최종 staging evaluator는 candidate의 `.codex-plugin`, `hooks`, `skills`, `references`, `scripts`를 함께
복사하고, `/.engineering/gates/`와 `/.sonsu/continuity/`를 fixture Git exclude에 미리 설정했다. 격리한
bundled Node `v24.20.0`과 npm `11.19.0`을 path·digest·version으로 binding했다. Model-free preflight는
필수 namespaced skill 8개, missing 0, loader error 0, model calls 0으로 통과했다.

이 complete-package artifact에서 natural controller 6개를 최대 동시성 2로 실행했다. Cohort 비교가
아니라 native routing/workflow 관찰이며, 각 controller가 최대 5개 reviewer를 만들 수 있으므로 자원
간섭을 제한했다.

| Case | Execution | Semantic | Routing | Seconds | agent attempts / unique receiver IDs / nonempty completed IDs |
| --- | --- | --- | --- | ---: | --- |
| `general-review-default` | complete | pass | pass | 277.584 | 5 / 5 / 5 |
| `focused-failure-lens` | complete | pass | pass | 227.775 | 1 / 1 / 1 |
| `mechanical-deterministic` | complete | pass | pass | 32.122 | 0 / 0 / 0 |
| `behavior-change-gates` | complete | pass | pass | 595.295 | 5 / 5 / 5 |
| `docs-snapshot-boundary` | complete | pass | fail | 119.032 | 1 / 1 / 0 |
| `provider-cleanup-routing` | complete | fail | pass | 299.517 | 2 / 1 / 1 |

`behavior-change-gates`는 continuity 기록, RED 2 failures, 구현, Node/npm GREEN 4/4, source/test syntax와
diff check, gate init/enter, 5개 고유 reviewer 결과, prepare-review, 5개 record-review, adjudication pass,
complete-unit receipt, gate close와 continuity close까지 관측했다. 실행 중 잘못 시도한 helper/CLI 명령은
후속 성공으로 교정됐으며 그 실패 자체를 pass 근거로 사용하지 않았다.

Docs 실행은 child를 만들었지만 `pending_init` 뒤 기다리지 않고 parent가 자체 분석과 final을 내서 routing
fail이다. Provider 실행은 child 결과를 수집했지만 parent final이 집중 범위 밖 webhook seed를 추가해
semantic fail이다. Native parent turn 완료는 routing gate 통과를 뜻하지 않는다. Routing pass에는
manifest가 요구한 수와 같은 고유 receiver ID, 같은 ID의 nonempty 완료 결과가 필요하다.

## N11 focused closure 검증

집중 리뷰의 root branch가 delegate 이후 same-ID nonempty result를 기다리고 adjudicate/report하도록
N11 문구를 보완한 뒤, 동일한 docs와 provider 원문을 각각 3개 fresh artifact에서 사전등록했다. 6개
호출을 최대 동시성 2로 모두 실행했고 첫 성공에서 멈추지 않았다.

| Case | Complete | Routing pass | Semantic pass | Semantic fail | Median seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| `docs-snapshot-boundary` | 3/3 | 3/3 | 3/3 | 0/3 | 195.265s |
| `provider-cleanup-routing` | 3/3 | 3/3 | 0/3 | 3/3 | 211.231s |

Docs는 3회 모두 reviewer 1개의 same-ID nonempty 결과를 기다린 뒤 immutable v2 snapshot을 수정하지
않았다. 이전 collection 실패는 재발하지 않았다. Provider는 3회 모두 결과 수집과 routing은 통과했지만
parent final이 webhook까지 포함했다. Trial 1·3은 child raw result가 provider-only였는데 parent가
webhook을 추가했고, trial 2는 delegated prompt부터 전체 change와 webhook 계약을 함께 전달해 child와
parent 모두 webhook을 포함했다. 따라서 N11은 collection closure를 고쳤지만, 사전정한 provider-only
해석 oracle 충족률은 0/3이었다. 이 수치는 아래 입력 모호성 진단과 분리하며 skill 결함의 원인 판정으로
사용하지 않는다.

이 검증 중 evaluator 운영 실수도 있었다. Trial 1 provider의 child wait 결과만 읽고 parent final을
확인하지 않은 채 semantic pass라고 중간 보고했다. Root가 실제 parent `final.md`에서 provider와 webhook
두 findings를 확인해 이를 바로 `fail`로 정정했다. Raw output은 수정하지 않았다. 이 사례 때문에 최종
adjudication은 각 run의 parent `final.md`, child 원결과와 `trace.jsonl`을 따로 읽고 생성·수집·통합
단계를 각각 판정해야 한다. 정본 절차와 사전등록 전체 실행·원본 실패 보존 규칙은
`plugins/engineering/skills/writing-skills/testing-skills-with-subagents.md`에 있으며 evaluator README는
native artifact 경로를 구체화한다.

## Scope repair와 명시적 입력 검증

후속 scope 문구를 적용한 frozen 7-case profile에서 원래 provider prompt 3회와 docs, focused failure,
general 각 1회를 결과 확인 전에 사전등록하고, 최대 동시성 2·`stop_early=false`로 모두 실행했다.
정적 focused review도 별도로 pass했다.

| Case | Complete | Routing | Semantic/oracle | Seconds | attempts / unique IDs / same-ID nonempty results |
| --- | --- | --- | --- | ---: | --- |
| `provider-cleanup-routing` trial 1 | complete | pass | fail | 264.105 | 1 / 1 / 1 |
| `provider-cleanup-routing` trial 2 | complete | pass | pass | 253.423 | 1 / 1 / 1 |
| `provider-cleanup-routing` trial 3 | complete | pass | fail | 258.892 | 1 / 1 / 1 |
| `docs-snapshot-boundary` | complete | pass | pass | 222.343 | 1 / 1 / 1 |
| `focused-failure-lens` | complete | pass | pass | 245.467 | 1 / 1 / 1 |
| `general-review-default` | complete | pass | pass | 249.228 | 5 / 5 / 5 |

Provider trial 1·3은 child가 provider-only 결과를 냈지만 parent가 webhook을 추가했다. Trial 2는 child와
parent 모두 provider-only였다. 따라서 **사전정한 provider-only 해석 oracle 충족률은 1/3**이고 raw
실패는 그대로 보존한다. 다만 `provider session cleanup과 오류 경로`는 한국어 문법상 fixture 전체의
오류 경로로 넓게 읽힐 수도 있다. 이 결과만으로 확정적인 skill scope 결함이나 유일한 언어 해석을
입증하지 못하므로 원인 판정은 `inconclusive`다.

이 모호성을 확인한 뒤, 명시적 대상에 대한 후속 사례 `provider-explicit-scope`를 실행 전에
별도 사전등록했다. 이 후속 사례는 기존 사례와 입력이 다른 진단이다. Prompt는 `src/provider.ts`의 `runWithProvider`와 그
provider 호출 오류 경로를 명시하며, 기존 case와 합산·대체·재판정하지 않는다. 새 8-case source와
artifact에서 한 번 fresh 실행했다.

| Case | Execution | Routing | Semantic | Seconds | attempts / unique IDs / same-ID nonempty results |
| --- | --- | --- | --- | ---: | --- |
| `provider-explicit-scope` | complete | pass | pass | 188.718 | 1 / 1 / 1 |

Parent final과 child 원결과 모두 `provider-session-leak`만 보고했고 webhook finding은 없었다. 이는
명시적인 file/flow 범위에서 현재 focused route가 범위를 지킨 1회 관측이다. 단일 실행이 모든 자연어
focused prompt의 일반 동작을 보장하지는 않는다. 7-case artifact는 원래 runner/cases digest에, 이
explicit case는 새 8-case digest에 각각 묶였으며 서로의 validator 실행으로 다시 표시하지 않는다.

## 현행 필수 matrix의 oracle 정리

원인 귀속이 모호한 `provider-cleanup-routing`은 `invalid_oracle_setup`으로 현행 필수 matrix에서
제외하고, 명시적인 `provider-explicit-scope`를 유지했다. 이전 narrow-oracle 실패 수치·raw output·
리뷰 판정은 그대로 보존한다. 스킬을 더 수정하거나 모델을 승격해 같은 입력이 통과할 때까지
반복하지 않았다.

정리 직전 8-case source는 `/tmp/sonsu-v2-before-oracle-retirement-source`에 고정했다.
현재 7-case matrix는 모호한 항목 하나만 제거했으며, 명시 사례의 입력·expected, fixture,
candidate plugin profile, evaluator runtime과 모델 설정은 바뀌지 않았다. 따라서 명시 사례의
1회 관측은 원래 8-case artifact에 연결한 채 해당 사례의 근거로 재사용한다. 이를 현행 7-case
전체를 새로 실행한 결과라고 보고하지 않는다. 이 정리의 의미는 실패의 통과 전환이 아니라
입력에 근거가 부족한 필수 검사를 바로잡은 것이다.

## 이전 실행과 적용 범위

Complete-package 이전 bare-discovery smoke는 별도 역사적 증거로 보존한다. 당시 6개 중 general,
focused failure, mechanical, docs, provider는 pass/pass였고 behavior는 RED/GREEN과 reviewer 5개를
수행했지만 managed gate가 staging의 plugin metadata·Git exclude 누락으로 차단되어 semantic
`inconclusive`였다. 이와 별도로 root는
`/tmp/sonsu-v2-native-eval/exact-final-20260913T014730-65080`의 원본 behavior workspace에서 bundled
Node test 5/5가 52.213ms에 통과했음을 외부 확인했다. 이 확인은 어느 native gate 실패도 pass로
바꾸지 않는다.

이 다섯 pass는 `.agents/skills` bare discovery 환경 결과이며 complete `.codex-plugin`/hooks 환경의
실행으로 다시 이름 붙이지 않는다. 이후 complete-package 6개를 전부 다시 실행했기 때문에 현재 package
routing 주장은 그 새 batch에만 근거한다. 더 이른 controller-varying 12회는 controller와 reviewer
모델이 함께 바뀐 workflow diagnostic이며 reviewer 모델 비교 자료가 아니다. Plan/source binding 전
batch도 raw same-prompt 관찰로만 보존하고 repaired evaluator 실행으로 재분류하지 않는다.

## Native packaging 관측

격리한 native app-server `plugin/list`는 현재 local marketplace plugin 11개를 찾았고 load error는
없었다. `plugin/read`는 11개 모두 성공했으며 Engineering 2.0.0은 skill 23개와 hook entry 2개,
전체 marketplace는 skill 57개와 hook-bearing plugin 8개를 노출했다. 이는 실제 native catalog,
manifest, skill, hook **metadata reading**만 검증한다. Hook 실행, semantic behavior, model routing을
증명하지 않으며 설치·global config·cache 변경이나 model call은 없었다.

## 원자료와 provenance

- Capability probe: `/tmp/sonsu-v2-native-eval/probe-20260913T000748-49803`
- Controlled 원본: `/tmp/sonsu-v2-native-eval/exact-final-20260913T014730-65080`
  - manifest `353e7a173e394085f50c8962ea969db4ecc13df765d37da6b79635bbd31ffb0d`
  - controlled plan `40b0f9efeefb0a7a8f206e32bf75cab6b627d0ef7af3c9ea66764dc22f9461ca`
- Policy-complete replay: `/tmp/sonsu-v2-native-eval/policy-replay-prepared-20260913T024854-98203`
  - canonical plan `980a05057e496bc7cc070ab7c9f5bd195719e23e72b358c516dd6dd91f9262c2`
  - plan file SHA-256 `b91df87ca3f69ab66e7dbbfdce040ee43678717619fdf5c307e29df19c557a9d`
  - report SHA-256 `dc01b692b6f6a87e38f7aa269d2734d93854c1c9241db589820bdab621a93093`
- Historical bare-discovery smoke: `/tmp/sonsu-v2-native-eval/repaired-natural-20260913T025712-2882`
  - report SHA-256 `0c017479c97a74afbf77d7d1a0cb8478ba573db47c388dc5550b08cd4f5be414`
- Complete-package smoke: `/tmp/sonsu-v2-native-eval/behavior-staging-final-20260913T032803-23240`
  - manifest `1aa2be7ad9fa9e7892913ec45b67801e2091ddb39d3a4ab95242fe096792f9c9`
  - candidate profile SHA-256 `fe33cf5529c088dc93b9333e081c83617d11b7a4efaff8f74492262294549fd5`
  - report SHA-256 `22095a8e29524578dcac4fad6fac55d8f1bc3154b147242641695caa953acec9`
- N11 focused validation: `/tmp/sonsu-v2-native-eval/n11-focused-validation-20260913T035015-30160`
  - plan SHA-256 `763b614a0bcf1b08fbebf35108e96054a829542bca130345431d331deeb64ba5`
  - candidate profile SHA-256 `c326e9ee9c4a5735af1c4d61b287826b75d610f990f43208400aff3525aa6c1b`
  - group report SHA-256 `c0fbadb2ef9cac1c7164932cf67a2e678f18acbe0c1ea3f9b17b1b056d9e0e34`
- Scope repair 7-case validation: `/tmp/sonsu-v2-native-eval/scope-repair-validation-20260913T040957`
  - runner SHA-256 `f5503f2bd6343557f8c9fe3c83f87b690a36b680196ea27c3aba600eb25c550d`
  - cases SHA-256 `eca4746e2037f216b77ad76784b692ce27d6c2d7964d84aab8c362e0ac0c6f14`
  - candidate profile SHA-256 `09665594e1738b75f92206f1e11341c709b05f13c7a9a923d00837d3e3310817`
  - pre-registration SHA-256 `403de3b91170d07ef9f081a258b4fdf156005015ed89f855e0c3d9617f5dd996`
  - group report SHA-256 `c1a0a885442c349db906ed3ddd1c035e3d15d03b563bbb729a01667e137950b6`
  - summary SHA-256 `9f70c0f97e0ddb3ba2c57bcdd06d743fe2c397445ffe40b1b307fa7bb91b563b`
- Explicit provider scope 8-case validation: `/tmp/sonsu-v2-native-eval/provider-explicit-scope-20260913T042723`
  - manifest `1926fdfda2387a8c0acbf60f32832dbdde0475525f9ed7ef938990187c18ae50`
  - cases SHA-256 `e14143c805ba03f31b3d1c3ef0b83123c80084cf06fa25507022cea2eda069a0`
  - pre-registration SHA-256 `07df7a2b0a773c75ed6a58e8ee204740854ed8474e8d55685a6e02eea425ab92`
  - artifact report SHA-256 `a9124fd66c0620207d17011301d7c313da28428710b048797386ddff1b3e78a5`
  - summary SHA-256 `7f673eb00ba52e0319277fcf63f06b32144f8a2105cc595e14b9eeb4b01558af`
- Scope repair static focused review: `/tmp/sonsu-v2-scope-repair-review.md`
- Native package metadata:
  - `/private/tmp/sonsu-v2-native-packaging-p9_v4n6z/plugin-list.json`
  - `/private/tmp/sonsu-v2-native-package-details-ruv19vy8`

Runner manifest는 canonical content, runner·binary digest, candidate revision, snapshot과 run path를 묶고,
result identity와 command/stdin, trace/final/stderr digest, fixed input의 실행 전후 digest를 검증한다.
Controlled plan은 evaluator source digest를 포함한다. Reservation은 중복 실행을 막고 중단 상태를 자동
재시도하지 않는다. 이 검증은 우발적 artifact 혼합과 불일치를 찾기 위한 consistency validation이며,
artifact directory 쓰기 권한을 가진 공격자에 대한 tamper-proof 보장은 하지 않는다.

## 최종 red-team 기준

- Review bundle SHA-256: `b834ef0e7bf26bdbf27c77fbe8f8e841c91c5c70eefb1e5d3eae45e08007a46d`
- Reviewed source archive SHA-256: `9187252c2dbff3d2576a2178cabedcfdc50954a4f543c20388dcfe1ae42e0dd3`
- Final review: [FINAL-REDTEAM.md](FINAL-REDTEAM.md)

검토 후에는 이 보고서와 구현 검토 기록의 최종 상태를 갱신하고 원본 red-team 보고서를 그대로
추가했다. 실행 코드·스킬·정책·case·fixture는 바꾸지 않았다. 이 판정은 설치·commit·push·게시
권한을 부여하지 않으며, 현행 matrix 전체를 마지막으로 다시 실행했다는 주장도 아니다.
