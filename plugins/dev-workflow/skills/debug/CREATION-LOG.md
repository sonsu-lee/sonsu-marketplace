# 작성 이력: 체계적인 디버깅 스킬

이 문서는 2025-10-03 원 작성 기록을 한국어로 정리한 자료다. 당시의 설계 선택·평가 결과를
보존하며 현재 실행 지침이나 이번 리비전의 검증 보고로 사용하지 않는다. 현재 절차는
[SKILL.md](SKILL.md)에 있다. 인용문과 수치는 원 기록을 유지한다.

## 원 자료와 추출

`~/.claude/CLAUDE.md`에서 조사 → 정상 사례 분석 → 가설 → 구현의 네 단계 틀을 추출했다.
당시 핵심 문구는 “ALWAYS find root cause, NEVER fix symptoms”였으며 시간 압박과 근거 없는
수정 시도를 억제하려는 목적이었다.

포함한 내용은 네 단계의 규칙, 구체적 수행 순서와 “NEVER fix symptom”, “STOP and re-analyze”
같은 표현이었다. 프로젝트별 맥락, 동일 규칙의 변형과 서술형 설명은 제외하거나 원칙으로
압축했다고 기록했다.

당시 `skill-creation/SKILL.md` 구조에 따라 적용 증상, 절차형 스킬 분류, 검색어, 수정 실패
분기와 단계별 체크리스트를 구성했다. 검색어는 “root cause”, “symptom”, “workaround”,
“debugging”, “investigation”이었다.

## 당시 표현과 구조 선택

강조 표현에는 “ALWAYS”·“NEVER”, “even if faster”, “even if I seem in a hurry”,
“STOP and re-analyze”, “Don't skip past”가 있었다. 첫 조사 단계, 단일 가설, 첫 수정 실패
이후의 재분석과 잘못된 접근 목록을 구조적으로 배치했다.

원 기록은 원인 조사 규칙을 개요·적용 시점·첫 단계·구현 규칙에 반복했고,
“NEVER fix symptom”을 네 번 사용했다고 설명한다. 이것은 당시 선택의 기록이며 현재
문서에 동일한 반복이나 강한 표현을 유지하라는 요구는 아니다.

## 당시 평가 기록

원 기록은 `skills/meta/testing-skills-with-subagents`를 따라 네 검증을 만들었다고 서술한다.
아래 결과 문구는 직접 인용이며, 원 실행 로그나 현재 재실행 결과는 이 파일에 포함돼 있지 않다.

| 당시 사례 | 원 기록의 결과 |
| --- | --- |
| 압박 없는 단순 문제 | “Perfect compliance, complete investigation” |
| 시간 압박과 쉬워 보이는 증상 수정 | “Resisted shortcut, followed full process, found real root cause” |
| 여러 계층과 원인 불확실성 | “Systematic investigation, traced through all layers, found source” |
| 첫 가설·수정 실패 | “Stopped, re-analyzed, formed new hypothesis (no shotgun)” |

원 총평은 “All tests passed. No rationalizations found.”였다. 이는 당시 작성자의 보고이며,
현재 스킬의 모든 조건에서 동작을 보장하는 결과로 일반화하지 않는다.

## 변경과 당시 결론

초기판은 네 단계, 잘못된 접근 목록과 수정 실패 분기로 구성했다. 이후
`skills/testing/test-driven-development` 참조를 추가하고 TDD의 최소 구현과 디버깅의 원인
수정이 서로 다른 목적임을 설명했다고 기록했다.

원 결론은 원인 조사·구체적 순서·TDD 관계가 명확하고 압박 사례에서 검증됐다는 것이었다.
잘못된 접근을 정확히 나열하면 “I'll just add this one quick fix” 같은 선택에 제동이
걸린다는 해석도 담겼다. 이러한 효과의 해석과 위 관찰 보고는 구분한다.

당시 사용 예시는 스킬 로드 → 개요 확인 → 첫 단계 조사 → 잘못된 접근 확인 → 전체 단계
완료였다. 원 비용 추정은 “Time investment: 5-10 minutes”, “Time saved: Hours of
symptom-whack-a-mole”이었다. 비교 조건이나 측정 방법이 없어 현재 비용 절감의 증거로
사용하지 않는다.

---

*작성일: 2025-10-03*
*원 목적: 스킬 추출·구조화·규칙 강화의 참고 사례*
