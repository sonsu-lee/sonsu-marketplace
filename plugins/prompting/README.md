# Prompting

Codex, ChatGPT와 OpenAI API에서 바로 사용할 수 있는 간결한 프롬프트를 작성하는 개인용
플러그인입니다.

## 포함된 스킬

- `prompt-builder`: 사용자가 요청한 결과, 제약, 대상 제품과 출력 형식을 보존하면서 프롬프트를
  생성·재작성·최적화합니다.

단순한 prompt engineering 개념 설명에는 이 스킬을 사용하지 않습니다. 실제 프롬프트 산출물을
요청했을 때만 선택하며, 다른 플러그인의 설치나 선행 실행을 가정하지 않습니다.

## OpenAI 제품과 모델

특정 OpenAI 모델, 제품 surface 또는 API 배치가 프롬프트 구성에 영향을 줄 때에는
`skills/prompt-builder/references/openai-prompt-guidance.md`를 참고합니다. 이 문서는
`2026-08-29` snapshot이며, 최신 또는 현재 권고를 요청받으면 snapshot만 신뢰하지 않고 OpenAI
공식 문서를 다시 확인합니다.

## 설치

마켓플레이스를 등록한 뒤 다음 명령으로 설치합니다.

```sh
codex plugin add prompting@sonsu-marketplace
```

기존 standalone `prompt-builder` 스킬을 함께 노출하면 두 스킬이 같은 요청에 경쟁할 수 있습니다.
플러그인판을 검증한 뒤에는 기존 standalone 복사본을 discovery 경로에서 제외합니다.
