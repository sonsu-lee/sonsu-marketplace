# Claude 파일·정량 윤문

[스킬 절차](../SKILL.md#절차)의 파일·정량 경로에서 읽는다. 표현·의미 보존은 [공통 규칙](quick-rules.md#공통-보존-규칙), 등급은 [룰북](quick-rules.md#등급-기준-자가-채점)이 담당한다.

## 입력과 경로

스크립트는 설치 루트의 절대 경로로, `_workspace/` 데이터는 사용자 cwd 기준으로 지정한다. `<skill-dir>`는 [스킬 절차](../SKILL.md#절차) 4에 적힌 이 스킬 디렉터리의 절대 경로다. 이 문서는 호스트가 경로를 치환하지 않으므로 명령의 `<skill-dir>`를 그 값으로 바꿔 실행한다. omp에서는 스킬 호출 메시지의 `Skill directory` 또는 `realpath skill://fluent-korean` 결과를 이 값으로 쓰고, `Agent` 도구 대신 같은 이름의 agent를 `task` 도구로 호출한다. 물리적 경로에서 `.claude-plugin/`까지 올라가 설치 루트를 찾는다.

```bash
SKILL_ROOT="$(d="$(cd -P '<skill-dir>' 2>/dev/null && pwd)"; \
  while [ -n "$d" ] && [ "$d" != / ] && [ ! -d "$d/.claude-plugin" ]; do d="$(dirname "$d")"; done; \
  [ -n "$d" ] && [ -d "$d/.claude-plugin" ] && echo "$d")"
```

`${SKILL_ROOT}/scripts/prepare_monolith_input.py`의 존재를 확인한다. `SKILL_ROOT`가 비었거나 파일을 찾지 못하면 shim·게이트 미확인 상태를 사용자에게 알리고, 정량 검증 통과 대신 확인할 수 있는 윤문 결과와 한계만 보고한다.

1. 입력을 읽고 본문 바깥의 챗봇 인사·면책·꼬리 문장만 분리한다. 본문 안에 자연스럽게 녹아 있는 표현은 유지한다.
2. 첫 300자로 장르를 추정하되 사용자 지정을 우선한다. `--genre`는 칼럼 `column`, 리포트 `report`, 블로그 `blog`, 공적·기타 `essay`, 초록 `abstract`다.
3. 새 작업은 cwd에서 아래 명령으로 run 디렉터리를 원자적으로 할당한다. `mkdir`는 이미 있는 이름이면 실패하므로 다른 세션과 같은 디렉터리를 나눠 쓰지 않는다. TAG는 한 번 생성해 같은 run에서 재사용한다. `run_id`가 비어 있으면 할당 실패를 보고하고 멈춘다.

   ```bash
   TAG=$(python3 -c "import secrets;print(secrets.token_hex(2))")
   DAY=$(date +%F); mkdir -p _workspace; run_id=
   for n in $(seq -f %03g 1 999); do
     mkdir "_workspace/$DAY-$n-$TAG" 2>/dev/null && { run_id="$DAY-$n-$TAG"; break; }
   done
   echo "run_id=$run_id"
   ```

4. 1에서 정리한 입력을 파일 쓰기 도구로 `_workspace/${run_id}/01_input.txt`에 그대로 저장한다. 원문은 셸 인자·변수를 거치지 않고 파일로만 전달해 백틱·`$`까지 비교 기준에 그대로 남긴다. 그다음 같은 run 디렉터리로 shim을 실행한다.

   ```bash
   python3 "${SKILL_ROOT}/scripts/prepare_monolith_input.py" --run-dir "_workspace/${run_id}" --genre "$genre"
   ```

   3에서 만든 `run_id`를 이후 모든 명령의 run 디렉터리 이름으로 쓴다. shim은 `run_dir=` 줄로 실제 경로를 출력한다. `01_input.txt`는 정규화된 비교 기준 원문, `00_metrics.json`은 점수·`route_hint`, `01_input_with_metrics.txt`는 모델 입력이다. `sanitize_text.py`가 제로폭·bidi·특수공백·한글 NFD를 정규화하고 변경 시 `00_sanitize.json`을 남긴다. `--no-sanitize`는 이 처리를 끈다. 정규화는 문자 기준을 맞추는 작업이며 AI 워터마크 제거를 의미하지 않는다.
5. metrics 실패 시 `00_metrics.error`와 점수 없는 입력을 사용하고 `standard`로 진행한다. `--run-dir`과 `--diagnosis` 상대 경로는 cwd 기준이다. `--baseline`은 기준선 파일을 명시적으로 바꿀 때만 쓴다.

## 경로 선택

| 입력 | 경로 |
|---|---|
| `--strict`, 정밀 모드·정밀하게·제대로 | heavy |
| 가볍게·빠르게만 | light |
| 명시 없음 | `route_hint` |
| 힌트 없음·점수 계산 실패 | standard |

입력 길이만으로 경로를 바꾸는 대신 위 규칙을 따른다. light·standard가 C/D이면 heavy 재실행을 권하고 사용자의 선택을 기다린다. shim 직후 다음 상태 줄을 출력한다.

```text
fluent-korean — 경로: {light|standard|heavy} ({route_hint|사용자 지정}) / run_id: {YYYY-MM-DD-NNN-TAG}
```

## 역할별 입력과 결과

플러그인의 `agents/`가 제공하는 세 역할을 `Agent` 도구로 호출한다. 모델 선택은 해당 agent 정의와 호스트 설정을 따른다.

| 역할 | 입력 | 결과 |
|---|---|---|
| `humanize-diagnostician` | `input_path=01_input_with_metrics.txt`, `taxonomy_path=<skill-dir>/references/diagnosis-rules.md` | `02_diagnosis.md`: 지배 패턴 3~6개(ID·근거·처방), 장르·격식·보존 지침 |
| `humanize-monolith` | `input_path`, `quick_rules_path=<skill-dir>/references/quick-rules.md`, `genre_hint`, 강도 | `final.md`: 본문과 `HUMANIZE-SUMMARY` 주석 |
| `humanize-finalizer` | `original_path=01_input.txt`, `rewritten_path=final.md`, 있으면 `diagnosis_path=02_diagnosis.md` | `final_pre_finalize.md` 백업, 국소 보정한 `final.md`, `09_finalize.json` |

위 파일명은 현재 run 디렉터리 아래의 실제 경로로 전달한다. 진단은 span 개수보다 글을 지배하는 표현을 판단한다. finalizer는 원문·윤문본을 직접 대조해 의미 보존 15항과 잔존·과윤문을 검사하고 문제 구간만 고친다.

## 윤문 경로

- **light**: 진단 없이 monolith를 보수 강도로 한 번 호출한다. 청킹 없이 내용 앵커와 확신 없는 구간을 유지한다. 공통 후처리·게이트 뒤 탐지가 거의 없고 변경률이 5% 미만이면 “이미 좋은 글입니다 — 손댄 곳은 N곳(요지)”으로 보고한다.
- **standard**: diagnostician → 아래 명령으로 진단 결합 → monolith 한 번 → 공통 후처리·게이트 순서다. 장문도 기본은 단일 윤문 호출이다. finalize는 승급 조건으로 결정한다.
- **heavy**: 같은 진단·결합 후 윤문하고 공통 후처리·게이트와 finalize를 모두 거친다. 필요하면 결합 명령에 `--chunk`를 붙인다.

```bash
python3 "${SKILL_ROOT}/scripts/prepare_monolith_input.py" \
  --run-dir "_workspace/${run_id}" --genre "$genre" \
  --diagnosis "_workspace/${run_id}/02_diagnosis.md"
```

결합 입력은 진단 → 정량 블록 → 원문 순서다.

### Heavy 청크 처리

`--chunk`가 만든 `chunk_manifest.json`에서 passthrough를 제외한 body 청크가 2개 이상일 때만 병렬로 윤문한다. 하나면 단일 monolith를 호출하며 manifest가 있으면 그 청크의 `input_file`, 없으면 `01_input_with_metrics.txt`를 쓴다.

- 분할 경계는 도구가 결정한다. 각 body 청크의 `input_file`·`rewritten_file` 값을 그대로 쓰고 최대 4개를 병렬 호출한다.
- 모든 호출은 같은 룰북 경로와 `02_diagnosis.md`를 참조한다. 룰북·진단 전문은 파일로 공유한다.
- 아래 명령의 `03_reassembled.md`를 `final.md`로 삼는다. 원문 해시·연결·문자수를 확인하고 각주 passthrough를 보존한다. 재조립 실패는 입력과 manifest를 바로잡은 뒤 재시도한다.

  ```bash
  python3 "${SKILL_ROOT}/scripts/reassemble_chunks.py" --run-dir "_workspace/${run_id}"
  ```

- 경계의 문체 이음매는 전후 두 문단만 국소 보정한다.
- 청킹 후 입력을 바꾸면 재청킹한다. 재청킹은 경계와 맞지 않는 기존 청크 윤문본을 `stale_removed`로 제거하므로 새 manifest로 다시 윤문한다.

## 공통 후처리와 게이트

게이트 직전에 서법을 복원하고 새로 윤문한 문장의 연결어미 쉼표를 정리한다.

```bash
python3 "${SKILL_ROOT}/scripts/restore_modality.py" \
  --before "_workspace/${run_id}/01_input.txt" --after "_workspace/${run_id}/final.md" \
  --out "_workspace/${run_id}/final.md"
python3 "${SKILL_ROOT}/scripts/strip_injected_commas.py" \
  --before "_workspace/${run_id}/01_input.txt" --after "_workspace/${run_id}/final.md" \
  --out "_workspace/${run_id}/final.md"
python3 "${SKILL_ROOT}/scripts/verify_gates.py" \
  --before "_workspace/${run_id}/01_input.txt" --after "_workspace/${run_id}/final.md" --genre "$genre"
```

- 복원기는 유보·요구가 사라진 짝 문장만 원문으로 복원한다. 낮은 유사도·불명확한 대상·병합 의심은 보류하고 P5 판정에 맡긴다. 복원으로 표현 문제가 돌아와도 의미 보존을 우선하며 복원·보류 건수를 summary에 적는다.
- 쉼표 도구는 기본적으로 새로 쓴 문장만 처리한다. standard·heavy의 진단이 C-11을 지목한 경우에만 `--all`을 붙여 인용 밖 모든 문장을 처리한다. 밀도나 light 경로만으로 이 옵션을 선택하지 않는다.
- 게이트는 `HUMANIZE-SUMMARY` 주석을 제외한다. stdout의 실제 수치를 상태 줄과 summary에 쓴다.

| exit | 의미 | 행동 |
|---|---|---|
| 0 | 변경률·목표 달성·구조·보존 축 통과 | 결과 전달 |
| 1 | 문자율 경고 또는 목표·대구·보존·서법 문제 | 해당 축을 알리고 finalize 승급 |
| 2 | 변경률 중단 기준 도달 | 후보 채택을 중단하고 보수적으로 한 번 재실행. 다시 2면 `hold_and_report` |
| 3 또는 실행 불가 | 판정 미확인 | 입력·실행 경로를 확인해 재시도하고 해결 전에는 완료 대신 미확인 상태 보고 |

헤딩·불릿 변화가 수치를 부풀렸다면 `--ignore-markup`으로 교차 측정한다. 판정을 바꿀 근거로 사용할 때는 두 수치를 모두 사용자에게 알린다.

## Finalize와 결과

heavy, 게이트 exit 1, 자체검증 6항 중 2항 이상 위반, 사용자 검증·증적 요청이면 finalizer를 실행한다. 그 외 light·standard는 게이트로 검증한다. light에는 진단 파일이 없으므로 `diagnosis_path` 없이 호출한다.

`verdict=hold_and_report`면 사람 검토를 안내한다. 그 외에는 finalize 뒤 게이트를 다시 실행해 최종 값을 확정한다. 파일·정량 결과에는 다음을 담는다.

1. 상태: 완료 가능한 경우 `완료. 경로 {light|standard|heavy} / 변경률 X% / 등급 Y / 자체검증 N/6 통과`. 경고·보류·미확인은 해당 상태를 명시한다.
2. 윤문본 본문. light 조기 종료는 “이미 좋습니다”와 수정 요약으로 대신할 수 있다.
3. `final.md` 끝 summary의 메트릭·카테고리 탐지·자체검증 표와 복원·보류 건수.
4. 등급 B 이하는 heavy(`--strict`) 재실행 안내. 자동 승급 대신 사용자 선택으로 진행한다.

## 후속 요청

| 신호 | 처리 |
|---|---|
| 특정 카테고리만 다시 | 기존 run_id(TAG 포함)를 재사용하고 진단의 지배 패턴을 해당 카테고리로 한정해 heavy 진단부터 실행 |
| 이 문단만 | 해당 문단을 입력으로 새 run을 만드는 heavy 경로 |
| 2차 윤문·`/humanize-redo` | 기존 run_id(TAG 포함)의 `final.md`를 새 입력으로 heavy 진단부터 실행 |
| 윤문 강도 조정 | heavy 진단의 지배 패턴 수를 조절해 실행 |
| 장르 바꿔서 | genre를 바꿔 입력 준비부터 실행하고 route_hint 재판정 |

옵션은 `장르: 칼럼|리포트|블로그|공적`, `강도: 보수|기본|적극`(기본은 기본, light는 보수)과 경로 선택 표의 명시 요청을 사용한다. 옵션은 현재 요청에서 읽으며 프로젝트 `CLAUDE.md` 같은 다른 파일을 자동으로 파싱해 추론하지 않는다.
