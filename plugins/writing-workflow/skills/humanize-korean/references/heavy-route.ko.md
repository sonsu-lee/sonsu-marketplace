# Heavy 경로

> 영문 정본: [heavy-route.md](heavy-route.md) (`fcbe81d` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

선택한 경로가 heavy일 때 읽는다. 엄격 또는 정밀 요청, 두 번째 패스, 선택한
범주, 요청받은 문단, 강도 변경, 새 장르, 또는 이 경로를 권하는 `route_hint`(긴
텍스트)가 해당한다. 메인 스킬의 `SKILL_ROOT`, `RUN_DIR`, `GENRE`를 그대로 쓴다.
청크 분할과 재조립의 세부 동작은
[런타임 상세](runtime.md#chunking-and-reassembly)에 있다.

후속 패스는 선택한 최신 텍스트를 `01_input.txt`로 하는 새 실행을 시작하며 이
경로를 쓴다. 이전 실행을 절대 덮어쓰지 않는다. 자동 편집 라운드는 세 번으로
제한하고, 그 뒤에는 검토를 권한다.

1. standard 경로와 똑같이 진단해 `02_diagnosis.md`를 만든 뒤, 결정론적
   청커를 요청한다.

   ```bash
   python3 "$SKILL_ROOT/scripts/prepare_monolith_input.py" \
     --run-dir "$RUN_DIR" --genre "$GENRE" --no-sanitize \
     --diagnosis "$RUN_DIR/02_diagnosis.md" --chunk
   ```

2. `chunk_manifest.json`을 읽는다. 본문 항목마다 정확한 `input_file`과
   `rewritten_file`을 쓰고, 패스스루 항목은 건너뛴다. 본문 청크는
   [편집 역할](roles/monolith.md)로 편집하며, 요약이나 지어낸 도입부·결론을
   넣지 않는다. 청크 경계가 펜스 블록을 가르더라도 코드는 바꾸지 않는다. 보호
   구간은 원문 전체를 살펴 확인한다. 본문 청크가 하나여도 이 절차를 따른다.
3. 모든 본문 출력이 만들어지면, 청크가 하나여도 항상 재조립한다.

   ```bash
   python3 "$SKILL_ROOT/scripts/reassemble_chunks.py" \
     --run-dir "$RUN_DIR" --strict
   ```

4. 재조립에 성공하면 `03_reassembled.md`를 `final.md`로 복사한다. 경고는 보고한다.
   재조립은 패스스루 텍스트를 복원하고 글자 수 회계를 검사한다. 의미나 코드
   보존을 보장하지는 않는다.
5. 공통 게이트를 실행한 다음, 원문, 후보, 진단을 [마무리 역할](roles/finalizer.md)
   로 직접 비교하며 항상 마무리한다. 청크 출력에는 요약이 없으므로 마무리
   역할이 요약 블록을 정확히 하나 추가한다. 이후 게이트를 다시 실행한다.
   `hold_and_report`는 검토가 필요하다.
