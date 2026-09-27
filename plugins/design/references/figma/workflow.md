# Figma 실행 경로

Figma Design의 제품 화면·상태·overlay·prototype은 Figma 파일 안에서 완성한다.
[도구 선택](tool-routing.md), [capability와 증거](capability-and-evidence.md),
[결정적 실행 경계](deterministic-execution.md)를 먼저 확인한다. agent의 판단형 canvas writer는
공식 Figma MCP 하나다. 설치만으로 도구 권한이나 live capability를 가정하지 않는다.

## 화면과 구조

기존 file/page/frame, selection, nearby screens, component·variable·style, icon과 Code Connect를
읽고 [Figma 품질 계약](figma-quality-contract.md)에 따라 native frame을 만든다.
Auto Layout·HUG/FILL/FIXED·constraint는 content relationship과 resize 의도에 맞춘다.
기존 component와 semantic variable을 우선하고 [icon policy](icon-policy.md)의 exact asset과
출처를 확인한다. 각 visual section을 작은 write로 만든 뒤 screenshot·node 구조·binding을 다시 읽는다.
긴 문구, 현지화, 0/1/many 항목, 좁고 넓은 화면의 resize를 해당 위험에 맞게 확인한다.

## 상호작용

클릭 흐름이 있으면 [interaction specification](interaction-spec.md)에 따라 실제 control에
native reaction을 연결한다. starting point, overlay 닫기, back/cancel, loading, error와 recovery,
조건부 결과를 포함한다. visual state, 실행 가능한 reaction, annotation을 구분한다.
reaction readback과 가능한 playback을 별도로 확인하고 불가한 검사는 `not_run`으로 남긴다.

## 감사와 수동 보조 도구

읽기 전용 감사에서는 official MCP read capability만 사용한다. screenshot으로 보이지 않는
Auto Layout, component·variable binding, reaction을 추정하지 않는다. 수정 요청으로 바뀌면
수정 범위를 다시 고정한다. 사용자가 수동 실행하는 [Desktop companion](../../figma-plugin/README.md)은
allowlisted JSON의 선택 감사·정확한 이름 변경·icon 교체에만 사용한다. agent writer나
일반 canvas editor로 사용하지 않는다.

Figma `artifact_scope`에는 `extensions.figma`의 target, capability, resize·prototype scenario를
기록한다. 현재 공식 도구의 선행 스킬이 요구되면 그 계약을 따른다. 필요한 도구가 없으면
화면·interaction 명세와 실제 미실행 상태를 구분해 전달한다.
