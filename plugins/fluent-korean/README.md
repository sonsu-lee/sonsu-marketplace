# Fluent Korean

이 패키지는 [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai/tree/92b2936956d65d62ff4b19b75cccad8e3429bf43)를 바탕으로 기존 한국어 글의 AI 티·번역투를 윤문·진단하고, 한국어 산출물을 새로 쓸 때 같은 패턴을 피하는 생성 규칙을 적용한다. 일반 대화 답변·맞춤법 교정·번역은 선택 대상이 아니다.

```sh
codex plugin add fluent-korean@sonsu-marketplace
```

Codex는 [단일 호출 스킬](codex/skills/fluent-korean/SKILL.md)을, Claude Code는 [다단계 스킬](skills/fluent-korean/SKILL.md)을 사용한다. 두 경로 모두 `fluent-korean:fluent-korean`으로 선택한다. OMP는 [생성된 단일 호출 스킬](omp/skills/fluent-korean/SKILL.md)을 `/skill:fluent-korean`으로 호출한다. Codex 단일 호출 경로의 보호 규칙과 참고 자료를 유지하고 현재 호스트 모델을 사용한다. Claude Code의 다중 호출·strict 모드는 OMP에서는 제공하지 않는다. 파일·정량 윤문은 원문을 보존하고 동봉된 변경률 검증기로 측정하며, 30% 이상은 경고하고 50% 이상은 채택하지 않는다. 검증기 오류를 완료로 보고하지 않는다. 생성본은 `scripts/render-omp-compat.py`로 갱신한다.

짧은 일상 문장의 국소 윤문은 채팅에 반환하고, 파일·정량 윤문은 스킬의 검사 절차를 따른다.

[고정 원본과 포함 범위](UPSTREAM.md) · [라이선스](THIRD_PARTY_NOTICES.md)
