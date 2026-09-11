# Memory Manager 평가

[cases.json](cases.json)은 실제 사용자 메모리 없이 실행할 수 있는 다섯 가지 동작 시나리오입니다.
스킬의 문구 일치가 아니라 파일 변경과 결과 보고를 확인합니다.

## 실행 방법

1. 각 case의 `files`를 서로 다른 임시 디렉터리 아래에 생성합니다. 상대 경로는 모두 해당
   디렉터리 안에서 해석하고 실제 Codex home·Claude memory를 사용하지 않습니다.
2. 실행 전 파일 목록과 bytes 또는 SHA-256을 보관합니다.
3. 평가 agent에는 [스킬](../../plugins/memory-manager/skills/memory-manager/SKILL.md)과 참고 자료의 고정 사본, 해당 case의
   `request`, fixture root만 제공합니다. `expected`나 앞선 평가 결과는 전달하지 않습니다.
   대상 fixture 밖의 쓰기·개인 메모리 접근·네트워크·Git 작업과 재위임을 허용하지 않습니다.
4. 실행 후 원본 및 새 파일을 재조회하고 `expected`의 의미와 실제 변경을 대조합니다.
   최종 답변만으로 통과시키지 않습니다. 백업이 필요한 case에서는 원본 사본의 bytes와
   실행 기록의 백업→편집 순서도 확인합니다.
   붙여넣기 사례에서는 결과물의 코드 블록을 추출해 평가자 소유 사본의 지정 구간에 그대로
   적용합니다. 유지 항목·원래 출처·중첩 코드 fence와 범위 밖 프로젝트를 보존하며, 정리안의
   변경이 모두 반영됐는지 확인합니다. 개별 교체 문구나 자리표시자만 있으면 실패입니다.
5. 요청한 model/effort와 관측 가능한 실제 설정, 명령·파일 차이·출력, 실행 완료 여부 및 한계를
   임시 평가 기록에 남깁니다. 실제 모델 설정을 확인할 수 없으면 `unknown`으로 둡니다.

## 판정 범위

- `codex-note-only`: 원본 보호, 한 개의 노트에 정리안과 섹션 완성본, 복사할 범위·본문, 반영 미확인 표시.
- `claude-direct`: 실제 중복 병합·명령 갱신, 출처·예외 보존, 변경 전 복원 사본.
- `review-untrusted-memory`: 읽기 전용, 저장된 명령의 비신뢰 처리, 불확실한 참조와 오래된 선호 보존.
- `codex-copy-only`: 파일 쓰기가 불가능해도 대화에 완전한 교체 본문 제공, 원본·다른 프로젝트 보존.
- `codex-existing-proposal`: 기존 정리안을 재사용하고 누락된 완성본을 대화로 제공, 중복 노트 방지.

정적 frontmatter·manifest 검사와 native plugin/skill loading은 별도로 확인합니다.
`allow_implicit_invocation: false`를 loader에서 읽었다는 사실은 실제 모델의 선택 행동을
측정한 것과 다릅니다. 이 fixture 평가도 실제 Codex의 비동기 노트 반영이나 Claude Code
native 실행을 검증하지 않습니다. 스킬 없는 대조군 없이 성능 개선을 주장하지 않습니다.
