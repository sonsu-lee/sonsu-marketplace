# Prompting

Codex, ChatGPT와 OpenAI API에서 바로 사용할 prompt artifact 하나를 만드는 `1.0.0` capability pack이다.
`prompt-builder`와 OpenAI prompt guidance snapshot만 배포한다.

사용자가 지정한 결과, 제약, product surface, model, 언어와 출력 형식을 보존하고 동작을 바꾸지
않는 섹션·중복·placeholder를 제거한다. 특정 현재 OpenAI 동작, API parameter나 model capability를
요청하면 snapshot만 신뢰하지 않고 official documentation을 다시 확인한다. host model profile,
reasoning 설정, continuity나 일반 구현 workflow를 소유하지 않는다.

```sh
codex plugin add prompting@sonsu-marketplace
```
