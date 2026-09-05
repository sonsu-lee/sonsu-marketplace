# 0012 Use Role Routing and Execution Evidence

- Status: Accepted
- Date: 2026-09-05
- Supersedes: None; refines the model routing and context policy in 0011
- Superseded by: None
- Approval: 사용자가 연구·실험 결론과 Sol 배치에 대한 재조사를 검토한 뒤 현재 대화에서 “그러면 이대로 수정 진행해서 반영해줘봐”라고 승인했습니다.

## Context

Engineering은 이미 stage-owned gate, task별 제한된 수정, fresh reviewer와 plan 기반 red-team을
사용합니다. 다만 구체적인 모델 표는 Sol 중심이었고, 실제 모델 적용·실행 환경·미완료와 검증기
오류를 구분하는 공통 기록이 부족했습니다. 세션 분리만으로 파일이나 검토의 독립성이 생기는 것도
아닙니다. 기존 원 구현자 1–3회/fresh 4–5회는 운영 경험과 선행 workflow에서 가져온 값입니다.

공식 자료와 로컬 실험을 함께 검토했습니다. [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)는
역할별 모델과 effort 선택을, [최신 모델 가이드](https://developers.openai.com/api/docs/guides/latest-model)는
Astra 사용을 설명합니다. [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)와
[Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)은
별도 context에서 탐색하고 필요한 결과를 조정자에 돌려주는 구조를 다룹니다. 서로 다른 제품의
같은 effort 문자열이 같은 계산량이라는 근거로 사용하지 않습니다.

2026-09-05 추가 실험은 Codex CLI 0.153.3의 tool-enabled worker/reviewer를 사용했습니다.
최대 24회 예산에서 20회 invocation 중 17회 완료, 3회 약 360–362초 deadline 미완료였고 최대
동시는 3개였습니다. invocation은 여러 model/tool 왕복을 포함하며 API 요청 수나 비용 단위가 아닙니다.
구성은 pilot 1, 계획 구현 8, 환경 복구 교체 1, 독립 리뷰 6, 수정 3, 환경 확인 control 1회입니다.

| 범위 | 관찰 | 제한 |
| --- | --- | --- |
| Requests의 공개 redirect-auth 버그 | Luna/Terra medium의 완료 후보는 실행한 외부 검사 통과 | 전체 계약을 공개한 adapted task; 환경 영향 첫 Terra 호출은 깨끗한 비교에서 제외하고 교체. 공개 오래된 사례라 학습 노출 가능성 있음 |
| Engineering의 실제 review-artifact CLI 변경 | Luna medium 2회와 Terra medium 2회 모두 실제 경계 결함 잔존 | Terra high 구현은 이번 추가 실험에서 비교하지 않음 |
| 동일 Engineering artifact 독립 리뷰 | Terra medium 2개, Astra medium/high 각각 같은 3개 결함 확인 | 고유 결함은 3개; 중복 지적을 독립 발견 수로 세지 않음. Requests Astra 리뷰 2개는 미완료 |
| 이력 유지 수정 | native fork가 처음 두 반례를 해결하고 이후 resume이 새 net-diff 반례 해결 | fresh 비교 실행은 미완료; 두 방식의 우열·3+2 최적성 비교 불가 |

Requests는 [psf/requests#4718](https://github.com/psf/requests/pull/4718)의 base
`dd754d13de250a6af8a68a6a83a8b4419fd429c6`에서 시작했습니다. 후보별 실행한 125개 검사는
F2P 4개, P2P 117개, rebuild_auth 연결 4개이며 원격 연결 timeout 4개는 candidate sandbox에서
`not_run`입니다. Engineering은 이 저장소의 `2961836`→`471add3` 변경 계약을 사용했습니다.
검증기가 Python CLI를 Bash로 실행하거나 계약에 없는 출력 literal을 강제한 오류는 수정하고,
공유 helper가 빠진 fixture는 invalid, candidate 경로에 도달하지 못한 fault 주입은 inconclusive로
분리했습니다. 마지막 수정도 기본 검사 15 passed / 0 확인된 코드 실패 / 5 inconclusive /
1 invalid와 사후 net-diff 4 passed이므로 전체 gate 통과는 아닙니다.

이것은 모델 순위를 확정하는 benchmark가 아닙니다. 두 사례, 적은 반복, 사후 반례, 환경 복구와
미완료가 있으며 전체 Engineering workflow와 Claude native 실행은 시험하지 않았습니다.
원 실행·평가 자료는 로컬 실험 기록으로 보존하고 이 저장소에는 판단 근거만 요약합니다.

### 모델 선택 근거의 구분

[현재 공식 모델 안내](https://learn.chatgpt.com/docs/models)는 Astra 출시 뒤에도 Sol을 복잡하고
모호한 코드 변경·조사·판단의 주요 선택지로 유지합니다. Terra는 일상적인 작업, Luna는 좁고
반복 가능한 작업, Astra는 여러 단계·도구를 아우르는 가장 어려운 작업에 대응합니다. 이는 벤더의
역할 안내이며 이 저장소에서의 독립적인 성능 비교 결과는 아닙니다.

앞선 tool-free 리뷰에는 Sol high도 포함됐습니다. 사전 결함 9개를 두 번씩 본 결과는 여섯 설정
모두 18/18이어서 모델을 구분하지 못했습니다. 사후 확인한 추가 결함 2개를 두 번씩 본 결과는
Terra high 1/4, Sol high 2/4, Astra high 4/4였습니다. 그 표본에서 Astra는 Sol보다 응답이 빠르고
출력 token도 적었지만, 사후 평가와 적은 반복을 복잡한 자율 구현 전반으로 일반화할 수 없습니다.
위 tool-enabled 추가 실험에는 Sol 비교가 없습니다. Sol medium과 Terra high의 구현 비교도
없으므로 Sol을 기본 후보에서 제외할 근거가 되지 않습니다. Astra medium/high가 동일 artifact에서
같은 결함을 찾은 결과는 모든 리뷰에 high가 필수라는 근거도 아닙니다.

2026-09-05 확인한 [Codex 가격표](https://learn.chatgpt.com/docs/pricing)의 표준 속도 100만 token당
입력/캐시 입력/출력 크레딧은 Terra 50/5/300, Sol 100/10/500, Astra 250/25/1,250입니다.
동일한 token 양이면 Astra는 Sol의 2.5배이며 Sol 프로모션은 최소 2026-11-21까지 안내돼 있습니다.
이는 당시 단가 비교입니다. 실제 token 양·추론·캐시·속도 설정·재작업이 달라 총 완료 비용이 같은
비율이라는 뜻은 아닙니다. [공식 배포 가이드](https://developers.openai.com/api/docs/guides/deployment-checklist#choose-a-gpt-56-model)처럼
대표 작업의 성공, 지연, token 사용과 성공한 작업당 비용을 함께 비교해야 합니다.

따라서 아래 배치는 공식 안내를 반영한 **잠정 운영값**입니다. Sol medium/high의 역할별 배치와
Astra로 전환할 정확한 경계는 아직 직접 비교하지 않았습니다. 정적 검사, 지침을 읽고 답하는
decision probe와 독립 문서 리뷰는 지침의 일관성을 확인할 수 있지만 모델 선택의 우월성을 입증하지 않습니다.

## Decision

1. 역할·복잡도에 맞는 잠정 기본값을 사용합니다. 결정론적 처리는 controller 도구, 좁고 명확한
   구현은 Luna medium, 보조 조사·일반 task review는 Terra medium, 계약·해법이 분명한 복잡한
   구현은 Terra high입니다. 모호한 구현과 일반 전체 리뷰는 Sol medium, 복잡한 논리·가정·경계
   검토와 영향 큰 설계·fresh red-team은 Sol high로 시작합니다. 여러 시스템·도구·단계를 아우르는
   가장 어려운 작업은 Astra medium을 직접 선택하고 깊은 분석·경계 검증이 필요하면 high를 씁니다.
   Sol을 정상 후보로 두되 어떤 모델도 필수 중간 승격 단계로 만들지 않습니다. 모델과 추론도는
   별도로 선택하며 사용자 지정과 실제 allowlist를 우선합니다. 단가만으로 최저비용을 주장하지 않습니다.
2. [공통 실행 계약](../../plugins/engineering/skills/using-engineering-skills/references/agent-execution.md)을
   기존 brief/ledger/report에 연결합니다. requested/observed model·effort, task/gate ID, 정확한
   revision, session lineage, 환경·scratch와 소비·남은 예산을 구분합니다. 관측 불가와 fallback을
   적용 성공으로 바꾸지 않으며 사용자 설정을 자동으로 덮어쓰지 않습니다.
3. 스킬은 절차와 예산을 소유하고 별도 agent는 집중된 실행·독립 검토를 맡습니다. 최초 reviewer는
   구현자 transcript나 자체 판정 대신 고정 계약·artifact·검증 사실을 받습니다. 병렬 구현은 독립된
   쓰기 소유권이나 별도 worktree와 단일 통합 소유자를 요구합니다. 동시수는 controller가 제한하며
   전문 리뷰를 전체 리뷰의 대체물이나 다수결로 사용하지 않습니다.
4. 같은 task 수정의 3+2/max5를 운영값으로 유지합니다. 새 반례에도 같은 가정을 반복하고 진전이
   없으면 조기 fresh 전환을 허용합니다. session/model/owner가 바뀌어도 예산은 유지합니다.
   무관한 세 작업을 완료했다는 이유로 전체 session을 폐기하지 않습니다. 기존 Fast Path의 더
   낮은 예산과 일반 최종 리뷰 뒤 red-team 순서는 유지합니다.
5. 실행 미완료, runtime 실패, 잘못된 oracle와 코드 결함을 구분합니다. 원 결과를 보존하고
   검사 유효성을 바로잡은 뒤 재검증합니다. 필수 미검증을 pass로 승격하지 않습니다.

기존 [0007](0007-use-stage-owned-quality-gates.md)과 [0011](0011-use-fast-path-and-plan-red-team-gates.md)의
stage ownership, revision, 권한 경계와 completion gate는 유지합니다. 새 router나 daemon,
작업마다 다른 agent 설정 파일을 추가하지 않습니다.

## Alternatives Considered

- 모든 구현을 Luna 또는 Terra medium으로 통일: 복잡한 통합 경계에 충분하다는 근거가 없습니다.
- 모든 단계에 Astra high와 병렬 reviewer 적용: 좁은 작업에도 비용을 추가하며 실제 이득이 입증되지 않았습니다.
- Sol을 사용자 지정·가용성 대안으로만 제한: tool-enabled 비교의 부재는 Sol 불필요의 근거가 아닙니다.
- Luna→Terra→Sol→Astra 순차 승격: 작업에 적합한 모델을 직접 선택할 수 있고 회차만으로 판단력 부족을 알 수 없습니다.
- 3회 이후 항상 fresh 또는 같은 session 무제한 반복: task 난이도·피드백·진전과 공유 예산을 반영하지 못합니다.

## Consequences

기존 역할과 gate를 유지하며 실행과 검증을 더 정확히 보고할 수 있습니다. 모델 표는 되돌릴 수
있는 기본값이며 실제 실패 비용과 완료 비용에 따라 조정합니다. 현재 자료의 입력·출력 token이나
wall time만으로 총 금액을 계산하지 않습니다.

[LLMs Get Lost (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/file/59f6421e64707225fdf5b28840679a07-Paper-Conference.pdf),
[Scaling Agent Systems v3](https://arxiv.org/html/2512.08296v3),
[Is Three the Magic Number? (preprint)](https://arxiv.org/html/2607.05197v1)는 context·분해·반복의
문제를 검토하는 참고 자료입니다. 이 Engineering의 3+2 전환점이나 고정 fan-out 최적성을 증명하지 않습니다.
정적 검사와 native loading도 실제 모델 준수나 전체 workflow의 품질·비용 향상을 증명하지 않습니다.

## Revisit When

명확한 작업에서도 Luna 재작업이 늘거나, 복잡한 구현·리뷰에서 Terra high↔Sol medium과
Sol high↔Astra medium/high의 동일 작업 비교 근거가 쌓이면 재검토합니다. 비교에는 완료 품질,
유효한 추가 발견, 재작업까지 포함한 시간·비용과 미완료를 구분해 기록합니다. Sol 프로모션을 포함한
가격·속도 조건이 바뀌거나 모델별 재작업·완료 비용이 선택을 뒷받침하지 못할 때도 재검토합니다. 모델 allowlist와
platform의 model/effort·session·권한 도구가 바뀌면 해당 platform reference와 관측 경로를 갱신합니다.
