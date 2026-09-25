# 새 브랜치 이름

새 로컬·원격 브랜치 이름을 제안하거나 정할 때 적용한다. 기존 브랜치를 사용하는 push·PR·복구에서는 이름을 유지하고 자동으로 rename하지 않는다.

이름은 다음 순서로 결정한다.

1. 사용자가 지정한 정확한 이름
2. repository 문서·도구 설정에서 확인한 규칙
3. 실행 환경이 필수로 요구하는 prefix 규칙
4. 별도 규칙이 없을 때 `<type>/<short-kebab-description>`

Codex에서 실행 중이라는 사실이나 기존 branch 이름만으로 `codex/` 또는 `codex-` 접두사를 붙이지 않는다. 실행 환경이 prefix를 필수로 요구하면 그 요구사항을 확인하고 적용한다. `type`은 실제 변경 목적에 맞는 `feat`, `fix`, `docs`, `refactor`, `test`, `chore` 중 하나를 우선하며, repository가 다른 taxonomy를 요구하면 그 규칙을 따른다.

이름은 현재 작업 범위만 표현한다. 존재하지 않는 티켓 ID, team key, 사용자명이나 변경 범위를 만들어 넣지 않는다.
