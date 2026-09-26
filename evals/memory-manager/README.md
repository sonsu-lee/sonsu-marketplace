# Memory Manager 평가

`test_store.py`는 임시 저장 위치에서 저장·검색·옵트인 훅·프로젝트 격리·linked worktree·
명시적 삭제·색인 재생성·symlink 거부를 확인합니다. 실제 사용자 메모리는 fixture로
사용하지 않습니다.

```sh
python3 -m unittest discover -s evals/memory-manager -p 'test_*.py'
python3 scripts/render-claude-compat.py --check
python3 -m unittest discover -s evals/plugin-compat -p 'test_*.py'
claude plugin validate plugins/memory-manager-claude --strict
```

[cases.json](cases.json)은 실제 호스트의 스킬 선택·행동을 위한 별도 사례입니다. 각 사례에
새 `SONSU_MEMORY_HOME`과 fixture 프로젝트를 제공하고 요청·관련 스킬만 에이전트에
전달합니다. `files`를 먼저 만들고 `setup`으로 기억을 준비한 뒤 `{target_id}` 같은
자리표시자를 실제 ID로 치환합니다. `expected`는 평가자에게만 줍니다. 실행 전후 저장소와 fixture 파일을
재조회해 실제 호출·읽기·쓰기 여부를 기록합니다. 특히 관련 요청의 회상과 무관한
요청의 미회상을 각각 평가합니다. 정적 frontmatter 통과를 행동 통과로 간주하지 않습니다.

호스트가 실제 스킬을 발견하고 호출했는지, Codex 훅 정의가 신뢰되었는지, Claude Code
훅이 실행되었는지는 각 호스트에서 별도로 관찰합니다. 실행하지 못한 항목은 `not_run`,
원인을 특정할 수 없는 결과는 `inconclusive`로 보고합니다.
