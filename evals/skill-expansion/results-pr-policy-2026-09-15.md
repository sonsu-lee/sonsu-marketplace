# 2026-09-15 PR 리뷰 정책 후속 평가

## 변경 범위

Quality Engineering 0.5.1은 기본 독립 PR 리뷰를 Luna xhigh 5명 + Astra xhigh 1명으로 변경한다.
새 세션·고정 전체 diff·직접 생성·재위임 금지·슬롯 부족 시 분할 실행을 명시한다.
사용자 지정은 우선하며, 모델 미지원과 자동 메모리 격리 한계는 실제 관측대로 보고한다.
원인·발생 조건·필요한 수정이 같은 지적은 최종 결과에 한 번만 남긴다.
이 기록은 이전 3인 구성의 평가나 구현 검토를 새 정책의 실행 증거로 사용하지 않는다.

## 정적·호환 검사

- plugin-compat unittest 7개 통과.
- Claude/continuity renderer `--check`, `git diff --check` 통과.
- SKILL frontmatter 기본 구조·description 길이·상대 링크 검사 통과.
- 평가 JSON 파싱·case ID 중복 검사 통과. 기존 명시 3인 요청은 사용자 지정 우선 사례로 유지한다.

## 별도 문맥의 판단 평가

`pr_policy_eval`을 `fork_turns=none`으로 생성해 현재 스킬과 네 상황을 제공했다.
기대 판정은 제공하지 않았고 평가 모델은 별도 override 없이 상속했다. 실제 모델 식별값은
반환되지 않아 unknown이다. 원출력은 `/private/tmp/pr-policy-eval-20260915.json`에 보존했다.
단일 평가 세션이 네 상황을 처리했으며, 이는 6명의 실제 PR 리뷰 실행이나 자동 선택 평가가 아니다.

| 상황 | 관찰 | 판정 |
|---|---|---|
| 새 슬롯 2개, 자동 메모리 비활성화 불가 | 5 Luna + 1 Astra xhigh를 새 세션으로 분할 실행하고 자동 메모리 격리 한계를 보고 | pass |
| Astra 및 외부 실행 수단 미지원 | Luna 부분 결과와 Astra blocked/not_run을 구분하고 전체 완료·대체 모델을 주장하지 않음 | pass |
| Luna high 3명 명시 | 사용자 지정대로 3명·high를 선택하고 기본 Astra를 추가하지 않음 | pass |
| 같은 결함 4개와 별도 결함 1개 | 중복 제거 후 2건, 단독 발견 유지, 전체 리뷰 반복 없음. head 일치와 별도로 마지막 base 확인 필요를 식별 | pass |

## 로컬 설정 확인과 실행 한계

사용자가 승인한 로컬 Codex 설정에서 `max_threads`를 8에서 16으로 변경했고 `max_depth = 3`은 유지했다.
수정 전 백업을 만들었고 codex-cli 0.154.0의 `features list`가 설정을 오류 없이 읽었다.
설정 읽기 성공은 현재 대화의 실행 상한 변경이나 새 작업의 실제 16슬롯 검증을 의미하지 않는다.
실제 6인 PR 리뷰·원격 조회·모델 설정 readback·영구 메모리 격리·새 버전 설치 및 자동 선택은 not_run이다.

## 평가한 스킬

SHA-256: `7b08dab62dc934a1246e4dacbf011404a4b3b50dcc8e27df517bc44421736c54`
