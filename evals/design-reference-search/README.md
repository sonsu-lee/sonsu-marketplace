# 디자인 레퍼런스 검색 평가

`design:find-references`와 설계 스킬 안의 [레퍼런스 검색 계약](../../plugins/design/references/reference-search.md)을
다섯 층으로 평가한다. 앞 층의 통과를 뒤 층의 근거로 쓰지 않는다. 각 층의 결과는
`pass / fail / not_run / inconclusive`와 근거로 기록한다.

| 층 | 확인하는 것 | 위치 | 현재 상태 |
| --- | --- | --- | --- |
| L0 결정적 검사 | reference set 형식, locator 출처 추적, 중복, primary·차용 상한, 스키마 일치, 사례 연결 | `test_*.py` | 자동 실행 |
| L1 선택·행동 | 자동 선택, 설계 스킬과의 경계, 공급자 자격·대체, 안전한 행동 | `cases.json`, `../skill-routing/cases.json` | `not_run` |
| L2 검색 품질 | 고정 후보 풀에서 쿼리·선별·결과 없음 판단 | `retrieval_metrics.py`와 정답 세트 | `not_run`: 정답 세트 없음 |
| L3 설계 효용 | 레퍼런스 유무에 따른 최종 디자인 차이 | 아래 절차 | `not_run` |
| L4 비용 | 검색 호출 수, 토큰, 지연 | 실행 trace | `not_run` |

```bash
python3 -B -m unittest discover -s evals/design-reference-search -p 'test_*.py' -v
```

## L0 결정적 검사

검증기(`validate_design_quality.py references`)와 계약 확장(`extensions.references`)이 형식,
locator 출처, 중복, primary·차용 상한과 `no_verified_match` 규칙을 지키는지 검사한다.
`--provenance`는 `agent_found` locator가 실제 도구 출력 기록에 있는지만 확인한다. 이 층의
통과는 레퍼런스가 요청에 맞는다는 뜻이 아니다.

## L1 선택과 행동

`../skill-routing/cases.json`의 `find-references` 사례는 자동 선택과 근접 오답을,
이 폴더의 `cases.json`은 선택 뒤의 행동을 다룬다. 실행 방법은
[skill-expansion](../skill-expansion/README.md)과 같다. 격리된 host에서 중립 ID, `prompt`,
`installed_plugins`의 스킬 카탈로그와 `fixture`만 제공하고 `expected`·`must_not`은 주지 않는다.

- `fixture.providers[].state`가 `qualified`인 공급자만 호출 가능한 도구로 노출한다.
  `unauthorized`·`unavailable`은 해당 오류를 반환하는 도구로 제공한다.
- `tool_returns`는 첫 검색의 도구 응답으로 반환한다. 모델이 결과를 상상해 채우지 않는다.
- 자동 선택은 prompt마다 3회 실행해 2회 이상 선택되면 선택으로 본다. 명시적 호출 성공을 자동
  선택 성공으로 보고하지 않는다.
- `split: held_out` 사례는 SKILL.md와 계약 문구를 고치는 데 쓰지 않고 마지막 회귀 검사에만 쓴다.

모의 도구 응답으로 확인한 선택은 실제 공급자 호출이나 네트워크 성공의 증거가 아니다.

## L2 검색 품질

Mobbin·Refero 같은 공급자의 색인은 이 저장소가 소유하지 않는다. 그래서 L2는 공급자 검색이 아니라
스킬의 쿼리 작성, 후보 선별, 결과 없음 판단을 고정된 후보 풀에서 측정한다.

1. 스타일·화면·흐름·컴포넌트·앱 지정·플랫폼·오타·범위 밖 쿼리를 40–60개 만들고
   `calibration`과 `held_out`으로 나눈다. `held_out`은 튜닝에 쓰지 않는다.
2. 쿼리마다 공급자 응답을 스냅샷으로 저장해 후보 풀로 쓴다. 라이브 결과는 계속 바뀌므로 채점 중에
   다시 검색하지 않는다. 이미지 원본은 저장소에 커밋하지 않고 locator와 공급자 링크만 둔다.
3. 평가자 2명 이상이 후보를 0/1/2로 채점하고 가중 κ를 보고한다. 디자인 판단은 평가자 간 일치가
   낮은 편이므로 κ가 0.4 미만이면 등급 정의와 예시를 먼저 보강한다. 반환됐지만 채점되지 않은
   후보는 0으로 계산한다. `unjudged_rate`가 높으면 후보 풀과 채점을 보강한다.
4. 스냅샷을 재생하는 모의 공급자에서 스킬을 실행해 run 파일을 만들고 채점한다.

```bash
python3 evals/design-reference-search/retrieval_metrics.py validate --gold <gold.json>
python3 evals/design-reference-search/retrieval_metrics.py score --gold <gold.json> --run <run.json> --split held_out
python3 evals/design-reference-search/retrieval_metrics.py score --gold <gold.json> --run <run.json> --floors <floors.json>
```

주 지표는 `ndcg_at_k`(k=5)다. `hit_at_k`, `precision_at_k`, `mrr`, 범위 밖 쿼리의 `abstention`,
상위 결과의 `distinct_app_ratio`를 함께 본다. run에 없는 사례는 결과 없음으로 채점하며 범위 밖
사례라도 abstention 통과로 세지 않는다. 큐레이션한 표본이므로 신뢰구간을 주장하지 않고 사례 수를 함께 보고한다.

첫 측정값은 목표가 아니라 `provisional-baseline-regression-gate` 상태의 최저선으로 floors 파일에 고정한다.
참고할 공개 수치로 GUing의 Hit@5 0.77, UI Remix의 Hit@5 0.88과 nDCG@5 0.77이 있다. 이 값은
데이터와 과업이 달라 합격 기준으로 옮기지 않는다. calibration과 held-out의 차이가 크면 쿼리 규칙이
calibration 사례에 과적합된 것으로 보고 다시 검토한다.

## L3 설계 효용

30개 이상의 설계 과업을 같은 모델·도구 조건에서 레퍼런스 검색 허용과 금지로 각각 실행하고
결과를 같은 viewport의 PNG로 렌더링한다. 평가자는 어느 쪽이 검색을 썼는지 모르는 상태에서
과업 적합성, 위계, 레퍼런스의 과한 복제 여부, 일반적 기본값과의 차이를 보고 고른다.

- 같은 쌍을 순서를 바꿔 두 번 판정하고 두 번 모두 같은 쪽을 고른 경우만 승리로 센다.
- 채택 규칙은 [language-style](../language-style/README.md)과 같다. 동률이 아닌 과업의 2/3 이상에서
  이기고 단측 부호검정 p<0.05를 만족해야 한다. 승률의 Wilson 95% 하한도 0.5를 넘어야 한다.
- 모델 평가자를 쓰면 판정의 20% 이상을 사람 평가자와 대조해 일치율을 보고한다.

## L4 비용

L1–L3 실행 trace에서 검색 호출 수, 이미지·상세 조회 수, 토큰, 지연을 사례별로 기록한다.
계약은 요청당 검색 호출을 보통 6회 이내로 둔다. 지연과 토큰의 상한은 기준 측정 전에 정하지 않고,
L3에서 개선이 확인된 경우에만 비용 증가를 받아들인다.
