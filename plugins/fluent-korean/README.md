# Fluent Korean

이 패키지는 [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai/tree/92b2936956d65d62ff4b19b75cccad8e3429bf43)를 바탕으로 기존 한국어 글의 AI 티·번역투를 윤문하거나 진단한다. 일상 메시지와 기술 문서의 설명문도 요청한 범위에서 다룬다. 일반적인 새 글 작성·맞춤법 교정·번역은 선택 대상이 아니다.

```sh
codex plugin add fluent-korean@sonsu-marketplace
```

Codex는 [단일 호출 스킬](codex/skills/fluent-korean/SKILL.md)을, Claude Code는 [다단계 스킬](skills/fluent-korean/SKILL.md)을 사용한다. 두 경로 모두 `fluent-korean:fluent-korean`으로 선택한다. 짧은 일상 문장의 국소 윤문은 채팅에 반환하고, 파일·정량 윤문은 스킬의 검사 절차를 따른다.

[고정 원본과 포함 범위](UPSTREAM.md) · [라이선스](THIRD_PARTY_NOTICES.md)
