# Codex 작성 시 고려사항

> 영문 정본: [codex.md](codex.md) (`57da0f4` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

작성하는 스킬이 Codex를 대상으로 할 때 읽는다. 프로젝트의 작업 흐름과 최신
[Build skills 가이드][skills]를 따른다.

1. **공통 형식 유지:** 지침으로 시작하고, 도구와 지침으로 할 수 없을 때만
   스크립트를 더한다. Codex는 긴 스킬 목록에서 description을 줄일 수 있으므로 핵심
   용도를 먼저 쓴다.
2. **필요할 때만 Codex 메타데이터:** `agents/openai.yaml`은 표시 메타데이터, 호출
   정책, 도구 의존성이 필요할 때만 쓰고 필드는 최신 가이드에서 고른다. 플러그인
   작업 흐름에서는 [플러그인 스킬 가이드][plugins]로 스킬의 판단과 도구가 맡는
   데이터·권한·동작을 구분한다.
3. **크기 확인:** frontmatter를 포함한 `SKILL.md` 전체를 `wc -c`로 잰다. 한도보다
   여유를 두고, 옮기기 전에 지침을 먼저 지운다.
4. **로딩 확인:** 설치된 이름으로 스킬을 호출하고 이벤트와 주입된 프롬프트를 살펴
   파일 끝까지 잘림이나 경고 없이 도착하는지 확인한다.
5. **동작 확인:** 대표 작업, 암묵적 선택, 스킬을 로딩하면 안 되는 인접 요청을
   실행한다. 필요한 참고 문서를 실제로 읽는지 확인한다([평가 가이드][evals]).

## 주의할 점

- Codex CLI `0.163.0`은 플러그인 스킬의 주 프롬프트를 **8,000 UTF-8 바이트**로
  제한한다([renderer][renderer], [injection][injection]). 버전별 플러그인 한도이므로
  지원 버전이 바뀌면 다시 확인한다.
- 바이트는 줄, 문자, 토큰과 다르다.
- 플러그인 스킬은 `$skill-workflow:authoring-skills`처럼 한정된 이름으로 호출한다.
  `0.163.0`에서 `$authoring-skills`만으로는 플러그인 스킬이 선택되지 않는다.
- 파일 존재, `skills/list`, 형식 검증은 로딩을 증명하지 않는다.
- Codex에는 평가 실행기가 없다. `evaluating-skills`나 프로젝트 도구를 쓴다. 로컬
  요청 캡처는 로딩을 증명할 뿐 동작은 증명하지 않는다.
- 허가된 모델 접근이 없으면 동작은 미검증으로 보고한다. 다른 클라이언트의 실행이나
  텍스트 리뷰만으로 Codex 지원을 주장하지 않는다.

[skills]: https://learn.chatgpt.com/docs/build-skills
[plugins]: https://developers.openai.com/plugins/build/skills
[evals]: https://developers.openai.com/blog/eval-skills
[renderer]: https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/ext/skills/src/render.rs
[injection]: https://github.com/openai/codex/blob/83086188ae0614bd882818ff1aa23f3194962012/codex-rs/ext/skills/src/host_prompt.rs
