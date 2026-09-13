# Marketplace v2 native behavior evaluation

이 평가는 marketplace v2의 실제 native Codex routing과 작업 절차를 두 개의 작은 fixture로
확인한다. 이전 26회 suite를 재현하지 않고, 승인된 기본 동작과 비교에 필요한 대표 경계만 다룬다.

- `review-service`: 일반 리뷰 team, 집중 lens, 외부 trust boundary, 내부 typed flow, provider
  cleanup, immutable docs snapshot을 같은 artifact에서 확인한다.
- `workflow-pack`: 결정론적 기계 작업과 동작 변경 구현의 gate 차이를 확인한다.

`review-service`의 webhook boundary와 provider cleanup 결함은 reviewer 검출력을 측정하기 위해
의도적으로 심은 oracle seed다. 이 fixture는 배포 제품 코드가 아니며, seed 수정은 평가 후보의
응답으로 판정할 대상이지 fixture baseline에 반영할 제품 수정이 아니다. 이 설명과 oracle은
per-run model workspace에 복사하지 않는다.

`cases.json`의 `expected`와 `evaluation_control`은 hidden evaluator data이며 model prompt와 fixture
workspace에 넣지 않는다. runner는 두 필드를 제거한 `.eval-input.json`, fixture 파일, 후보 plugin의 `.codex-plugin`·`hooks`·`skills`·`references`·`scripts`
사본만 각 workspace에 둔다. 사용자 `HOME`, plugin cache와 config는 사용하지 않는다. 인증은 임시
`CODEX_HOME/auth.json` symlink로만 참조하고 raw trace·출력·변경 workspace는 저장소 밖 새
`0700` 디렉터리에 보존한다.

## 평가 행렬

대표 `review-benchmark`는 artifact, 기준, 도구 조건을 유지하고 아래 네 cohort를 각각 3회 실행한다.
모델 품질 비교에서는 controller 변경을 confound로 만들지 않도록 `controlled_benchmark.py`가 각
reviewer를 delegated role로 직접 실행하고, 고정 `gpt-6-astra/high` adjudicator가 결과를 검증·통합한다.

| cohort | 요청 model / effort | fresh reviewer 수 |
| --- | --- | ---: |
| `luna-xhigh-1` | `gpt-5.6-luna` / `xhigh` | 1 |
| `luna-xhigh-5` | `gpt-5.6-luna` / `xhigh` | 5 |
| `sol-xhigh-1` | `gpt-5.6-sol` / `xhigh` | 1 |
| `sol-max-1` | `gpt-5.6-sol` / `max` | 1 |

그 밖의 routing·workflow 사례는 한 번씩 실행한다. 일반 리뷰는
`engineering:review-quality`와 기본 5개 fresh Luna `xhigh`, 한 lens만 지정한 리뷰는 단일 집중
reviewer를 Luna `xhigh`로 fresh delegation, 작은 기계 작업은 불필요한 전체 DAG 없이 결정론적 검사, 동작 구현은 필요한 구현·검증·
리뷰 gate를 기대한다. provider cleanup은 failure-mode review로 보내고, 현재 코드가 historical
snapshot을 자동으로 무효화하지 않는지도 확인한다.

명시적 `provider-explicit-scope`가 현재 provider 범위 검증을 담당한다. 기존
`provider-cleanup-routing`은 provider에 한정되지 않는 언어 해석도 가능해 필수 matrix에서 제외했다.
이전 실패·입력·판정은 [oracle 기록](ORACLE-CORRECTIONS.md)에 연결해 보존하며, 통과로 다시
분류하지 않는다. 현재 7-case matrix와 과거 7/8-case artifact의 source binding을 구분한다.

## 실행

최종 후보가 고정된 뒤 아래 순서로 실행한다. `prepare` output은 반드시 존재하지 않는 저장소 밖
경로여야 한다. 재실행은 기존 결과를 덮어쓰지 않으므로 새 output을 사용한다. Review comparison과
native workflow smoke는 필요하면 서로 다른 artifact로 준비해 source digest와 적용 범위를 분리한다.
Staging·manifest·discovery 코드가 바뀌면 독립 리뷰용 source를 고정하기 전에 실제 `prepare`와
model-free `preflight`를 먼저 실행해 native loader 계약을 확인한다. 비용이 드는 semantic model
호출은 그 결과까지 포함해 독립 리뷰를 통과한 고정 코드와 새 artifact에서만 실행한다.

```bash
python3 -B evals/marketplace-v2/runner.py validate

ARTIFACT_DIR=/tmp/sonsu-v2-native-eval/final-$(date +%Y%m%dT%H%M%S)
python3 -B evals/marketplace-v2/runner.py prepare \
  --output "$ARTIFACT_DIR" \
  --codex-binary /Applications/ChatGPT.app/Contents/Resources/codex

python3 -B evals/marketplace-v2/runner.py preflight \
  --output "$ARTIFACT_DIR"

# native controller routing/workflow 사례
python3 -B evals/marketplace-v2/runner.py run \
  --output "$ARTIFACT_DIR" \
  --timeout 900

# reviewer 모델·인원 통제 비교
python3 -B evals/marketplace-v2/controlled_benchmark.py prepare --output "$ARTIFACT_DIR"
python3 -B evals/marketplace-v2/controlled_benchmark.py workers \
  --output "$ARTIFACT_DIR" --jobs 4 --timeout 900
python3 -B evals/marketplace-v2/controlled_benchmark.py adjudicators \
  --output "$ARTIFACT_DIR" --jobs 4 --timeout 900
python3 -B evals/marketplace-v2/controlled_benchmark.py adjudication-template \
  --output "$ARTIFACT_DIR" --destination "$ARTIFACT_DIR/controlled/adjudication.json"
# 원출력과 hidden oracle을 대조해 adjudication.json을 작성한 뒤:
python3 -B evals/marketplace-v2/controlled_benchmark.py report \
  --output "$ARTIFACT_DIR" --adjudication "$ARTIFACT_DIR/controlled/adjudication.json"

python3 -B evals/marketplace-v2/runner.py adjudication-template \
  --output "$ARTIFACT_DIR" \
  --destination "$ARTIFACT_DIR/adjudication.json"
```

`adjudication.json`은
[`testing-skills-with-subagents.md`](../../plugins/engineering/skills/writing-skills/testing-skills-with-subagents.md)의
정본 절차에 따라 각 run의 `final.md`, delegated child 원결과와 `trace.jsonl`을 각각 읽고 채운다.
Child 결과만으로 parent의 최종 의미 판정을 대신하지 않고, 생성·수집·통합 단계를 별도로 판정한다.
`validated_defects`, `critical_misses`,
`false_positives`, `duplicate_findings`, `unnecessary_changes`는 oracle id 또는 구체적인 한 줄 설명을
사용한다. 완료된 turn도 의미 판정 전에는 `inconclusive`이며 자동 키워드 판정으로 승격하지 않는다.

```bash
python3 -B evals/marketplace-v2/runner.py report \
  --output "$ARTIFACT_DIR" \
  --adjudication "$ARTIFACT_DIR/adjudication.json"
```

한 run만 진단할 때는 `--run-id`, 사례 전체는 `--case-id`, benchmark cohort는 `--cohort-id`를 쓴다.
runner는 자동 retry를 하지 않는다. 실행 오류는 코드 판단 오답으로 세지 않고 `not_run`, 완료 없는
timeout·불완전 trace는 `inconclusive`로 유지한다.

Native run과 controlled worker·adjudicator는 같은 수집기로 stdout을 최대 32 MiB,
stderr를 최대 8 MiB까지 저장한다. 어느 byte 한도든 도달하면 프로세스 그룹을 종료하고 저장한
앞부분만 증거로 남긴다. 정확히 한도와 같은 크기도 보수적으로 불완전 출력으로 판정한다.
Trace 파서는 최대 32 MiB, 100,000행(빈 행 포함), 한 행당 4 MiB만 처리하며 행 한도를 넘으면
남은 내용을 읽지 않는다. 한도에 걸린 실행은 `turn.completed`가 남아 있어도 `inconclusive`이고,
report와 template의 재검증도 파일 크기와 파싱 한도에서 같은 제한 상태를 재계산한다.
이 한도는 stdout·stderr 수집과 trace 파싱에 적용하며 Codex가 직접 쓰는 `final.md`나 workspace
전체에 대한 디스크 quota는 아니다. Timeout과 byte 한도 종료 시 POSIX 프로세스 그룹을 정리하고
상속된 pipe의 EOF를 무한히 기다리지 않는다.

manifest ID는 ID 자체를 제외한 canonical content hash이며 현재 runner·Codex binary digest,
candidate revision, snapshot과 run path를 다시 확인한다. 각 실행은 atomic reservation을 먼저 만들고
중단된 reservation도 자동 재시도하지 않는다. report와 adjudication template은 result identity,
command·stdin, trace·final·stderr digest와 trace에서 재계산한 완료 상태가 일치하는 결과만 관측으로
센다. 불일치 파일은 `inconclusive` 또는 `not_run`으로 남긴다. 이는 우발적 혼합·변조를 검출하는
일관성 검증이며, artifact directory에 쓰기 권한이 있는 공격자에 대한 tamper-proof 보장은 아니다.
Controlled plan도 `controlled_benchmark.py` 자체 digest를 canonical plan ID에 포함하고 매 load에서
재검증한다. 따라서 scheduler·worker·adjudicator 구현이 달라진 plan은 새로 준비해야 한다.

각 fixture workspace는 user/global Git config와 hook을 읽지 않는 로컬 Git baseline을 갖는다.
`.sonsu/`, `.engineering/`, `node_modules/` 같은 generated infrastructure는 제품 diff에서 분리하지만
전체 변경 목록과 final workspace digest에는 남긴다. `.agents/`와 `.eval-input.json`은 고정 입력이며,
실행 뒤 candidate/public-input digest가 바뀌면 해당 실행은 `inconclusive`다. 제품 `src/`, contract,
tests와 docs는 제품 diff에 그대로 포함한다. 파일 digest에는 내용·크기와 실행 권한 비트
(`stat.S_IMODE(mode) & 0o111`)를 포함하므로 내용이 같아도 `chmod 644 → 755`는 candidate·workspace
변경으로 검출한다. 디렉터리 권한과 파일의 읽기·쓰기 권한 비트는 이 digest에 포함하지 않는다.

`preflight`는 같은 격리 workspace를 native `skills/list`로 읽어 필수 skill 이름과 loader error를
검사한다. 모델을 호출하지 않으며, discovery 통과를 실제 skill 선택이나 행동 통과로 간주하지 않는다.

`runner.py`의 cohort 실행은 model이 controller와 reviewer를 모두 맡는 native workflow 관찰이다.
controller가 실제 reviewer를 만들었는지와 그 증거를 평가하지만, controller까지 달라지므로 모델
품질 순위를 계산하는 자료로 쓰지 않는다. `controlled_benchmark.py`는 cohort당 1개 또는 5개의
no-delegation worker를 직접 호출하고 3회 반복한 뒤 동일한 Astra adjudicator를 사용한다. worker와
adjudicator의 원출력·trace는 분리 보존하며, 이 trace도 underlying model·effort는 노출하지 않는다.
Native smoke의 `evaluation_control`은 manifest metadata에만 있고 model stdin에는 넣지 않는다.
Controlled report만 cohort 품질 지표를 집계하며 native 표는 controller-confounded workflow 관찰로
표시한다.
Controlled adjudicator의 실행 규칙 위반 `fail`은 원 실행 결과와 summary에 보존한다.
의미 판정용 template에서는 해당 실행을 `execution_available=false`, `verdict=inconclusive`로
작성하며, 실행하지 않은 `not_run`은 그대로 유지한다.

## 관측 한계

JSONL은 요청 flag를 받은 endpoint의 완료, visible tool event, token usage와 시간을 기록한다.
현재 JSONL에는 underlying model과 effort가 없어 두 값은 `unknown`으로 보고한다. subagent 생성 수와
skill read는 visible event에서만 계산하며, host가 child detail을 노출하지 않으면 adjudication에서
`inconclusive`로 둔다. 소수 합성 fixture 결과를 보편적인 모델 우월성으로 일반화하지 않는다.
`luna-xhigh-5`는 이 benchmark 결과와 무관하게 사용자가 승인한 기본값이다.

## Capability probe

2026-09-13 앱 번들 `codex-cli 0.154.0-alpha.6.2`에서 임시 `HOME`·`CODEX_HOME`, `--ephemeral`,
`--ignore-user-config`, read-only 빈 workspace로 다음 요청이 각각 종료 코드 0과 정확한
`capability-ok`를 반환했다.

- `gpt-5.6-luna / xhigh`
- `gpt-5.6-sol / xhigh`
- `gpt-5.6-sol / max`
- runner smoke용 `gpt-5.6-luna / medium`

원자료는 `/tmp/sonsu-v2-native-eval/probe-20260913T000748-49803`에 있다. 이는 호출 지원
확인으로만 사용하며 marketplace 최종 후보 평가나 실제 모델·effort 관측을 대신하지 않는다.
