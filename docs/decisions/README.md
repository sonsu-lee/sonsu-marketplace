# 결정 기록

이 디렉터리는 아키텍처뿐 아니라 저장소와 Codex 작업 방식에 장기간 영향을 주는 결정을
보관합니다.

## 기록 기준

다음 중 하나에 해당하면 결정 기록을 고려합니다.

- 되돌리기 어렵거나 변경 비용이 큽니다.
- 실제 대안 사이에 중요한 trade-off가 있습니다.
- 여러 후속 작업이 이 결정을 전제로 합니다.
- 나중에 선택 이유를 복원하기 어렵습니다.
- Codex가 반복해서 따라야 하는 저장소 정책입니다.

작고 쉽게 되돌릴 수 있는 변경, 일회성 실험, 아직 결론이 나지 않은 아이디어와 다른 문서에
이미 명확히 기록된 내용은 결정 기록을 만들지 않습니다.

## 형식과 상태

파일 이름은 `NNNN-<decision>.md` 형식입니다. 문서는 Context, Decision, Alternatives
Considered, Consequences와 Revisit When을 포함합니다.

상태는 `Proposed`, `Accepted`, `Rejected`, `Superseded` 중 하나를 사용합니다. 결정을
대체할 때에는 이전 파일을 덮어쓰지 않고 이전 문서와 새 문서에 서로의 번호를 기록합니다.

## 현재 결정

- [0001 Use Local Marketplace](0001-use-local-marketplace.md)
- [0002 Separate Document and Commit Approval](0002-separate-doc-and-commit-approval.md)
- [0003 Keep Marketplace Plugins Independent](0003-keep-plugins-independent.md)
- [0004 Keep Research Independent](0004-keep-research-independent.md)
- [0006 Keep Prompting as an Independent Plugin](0006-keep-prompting-independent.md)
- [0007 Use Stage-Owned Quality Gates with Bounded Backtracking](0007-use-stage-owned-quality-gates.md)
- [0008 Add an Independent Product Plugin](0008-add-product-plugin.md)
