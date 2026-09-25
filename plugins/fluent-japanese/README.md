# Fluent Japanese

이 패키지는 [coji/natural-japanese](https://github.com/coji/natural-japanese/tree/9a78a42964096da509b8f3e011f0085a5f080151)의 일본어 작성·윤문·문서 진단 스킬을 제공한다.

```sh
codex plugin add fluent-japanese@sonsu-marketplace
```

[스킬](skills/fluent-japanese/SKILL.md)의 공개 ID는 `fluent-japanese:fluent-japanese`이다. 일상 메시지와 기술 설명의 문장에도 적용한다. 기술 문서의 장 구성·Markdown 정리는 범위 밖이다. 원본 참고 자료와 스크립트가 함께 설치된다. 짧은 문서에도 quick 경로의 lint를 실행하며, 파일을 만들지 않는 짧은 대화 답변은 육안으로 점검한다. 점수 진단은 대상 파일을 요구하며 100자 미만에는 점수를 매기지 않는다. full 경로의 추가 검토와 exp 경로의 모델 다운로드 조건은 원본 지침을 따른다.

[고정 원본과 포함 범위](UPSTREAM.md) · [라이선스](THIRD_PARTY_NOTICES.md)
