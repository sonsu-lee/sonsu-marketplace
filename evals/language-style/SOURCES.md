# 한국어 문체 평가 후보의 원본 출처

이 디렉터리의 후보 지침은 아래 두 MIT 라이선스 원본을 고정된 commit에서 선별하고 생성용으로 다시 표현한 `derived and adapted subset`이다. 원본 파일을 그대로 가져온 vendor snapshot은 아니다.

## `im-not-ai`

- 저장소: [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai)
- 기준 commit: [`31a66d165a9cc6c26c4c1246553f95d0468d27fb`](https://github.com/epoko77-ai/im-not-ai/commit/31a66d165a9cc6c26c4c1246553f95d0468d27fb)
- 참고한 원본:
  - [생성 단계와 후편집 규칙의 구분](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/docs/en/integration.md#L7-L21)
  - [보존·서법 계약](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/skills/humanize-korean/references/quick-rules.md#L9-L15)과 [장르·register 보존](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/skills/humanize-korean/references/quick-rules.md#L112-L118)
  - [이중 피동](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/skills/humanize-korean/references/quick-rules.md#L28), [광고성 buzzword](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/skills/humanize-korean/references/quick-rules.md#L42), [결산·과장·비유 규칙](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/skills/humanize-korean/references/quick-rules.md#L56-L69)
  - [기술 보고서 baseline 한계](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/skills/humanize-korean/references/ai-tell-taxonomy.md#L722-L729)
  - [원본 LICENSE](https://github.com/epoko77-ai/im-not-ai/blob/31a66d165a9cc6c26c4c1246553f95d0468d27fb/LICENSE)
- 적용 범위: 공통 의미 보존 원칙과 장르·register 보존, 이중 피동, 광고성 buzzword, 근거 없는 의의 과장, 반복 결산 문구와 불필요한 비유에 관한 규칙을 생성 단계에 맞게 선별했다. 빈도·분포 규칙은 금지 목록으로 사용하지 않고 완성된 초안에서 반복이 두드러질 때만 확인한다.
- 제외 범위: workspace, 위험도 점수, 심각도와 등급, 변경률 계산, 파일 산출물, 진단·수정·finalizer의 다중 호출 흐름은 후보 지침에 포함하지 않았다.

### MIT License notice

```text
MIT License

Copyright (c) 2026 epoko77-ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## `fluent-korean`

- 저장소: [snflkd/fluent-korean](https://github.com/snflkd/fluent-korean)
- 기준 commit: [`ce8683f0eba8cddb91de4dcd151425ff73e60498`](https://github.com/snflkd/fluent-korean/commit/ce8683f0eba8cddb91de4dcd151425ff73e60498)
- 참고한 원본:
  - [문장 성분, 완결 문장, 조사와 어미 규칙](https://github.com/snflkd/fluent-korean/blob/ce8683f0eba8cddb91de4dcd151425ff73e60498/plugins/fluent-korean/output-styles/fluent-korean.md#L30-L39)
  - [원본 LICENSE](https://github.com/snflkd/fluent-korean/blob/ce8683f0eba8cddb91de4dcd151425ff73e60498/LICENSE)
- 적용 범위: `b-hybrid.md`에만 다음 세 규칙을 추가했다. 의미가 모호할 때 생략된 문장 성분을 보완하고, 필요한 조사와 어미로 어휘 관계를 분명히 하며, 제목·목록·UI 문구를 제외한 본문을 완결된 문장으로 쓴다.
- 제외 범위: 사용자 어조를 따르지 않는다는 규칙, 한자어·부사·보조사·선어말어미·보조 용언의 적극적 확대, 엠대시의 일괄 회피는 포함하지 않았다.

### MIT License notice

아래 고지는 기준 commit의 원문을 오타로 보이는 부분까지 정규화하지 않고 그대로 보존한다.

```text
MIT License

Copyright (c) 2026 snflkd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OF OR IN CONNECTION WITH
THE SOFTWARE.
```
