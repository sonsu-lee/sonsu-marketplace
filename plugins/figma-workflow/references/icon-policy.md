# Icon and vector asset policy

## Source priority

1. existing design-system icon component
2. consuming component의 `INSTANCE_SWAP` property
3. supported replacement를 식별하는 preferred instance
4. product codebase 또는 approved icon set의 exact SVG
5. exact asset 요청 또는 확인

emoji, guessed glyph, primitive line reconstruction으로 missing icon을 대체하거나 brand mark를 발명하지 않는다.
exact asset이 없으면 영향 scope를 멈춘다. SVG는 source `viewBox`, aspect ratio, stroke/fill behavior, explicit
width/height를 보존하고 intended slot(예: 16, 20, 24px)에 맞춘다. `currentColor`는 target system이 요구하는
literal 또는 semantic variable로 해석하되 meaningful vector structure를 flatten하지 않는다.

Figma asset insertion은 current official provider schema와 required prerequisite가 확인한 path만 사용한다.
stale community tool name이나 존재하지 않는 API를 사용하지 않는다. 반복적인 exact instance replacement만
Desktop companion의 `replace-icon-instance-exact` allowlist를 사용할 수 있으며, preview receipt와 apply-time
readback 계약은 [deterministic execution](deterministic-execution.md)을 따른다.

icon family, outlined/filled state, stroke weight, optical alignment, semantic color와 실제 지원 state를
검증한다. icon-only control은 product contract의 accessible name과, 이름이 visible하지 않다면 useful design
annotation을 둔다. 16px·20px·24px asset은 별도의 optical drawing이 필요할 수 있으므로 균일 scale을
가정하지 않는다. interaction 변경 뒤에는 before/after state에서 size, position, meaning이 유지됐는지
확인한다.
