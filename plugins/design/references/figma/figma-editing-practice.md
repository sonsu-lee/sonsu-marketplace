# Figma native editing practice

이 문서는 사람의 Figma workflow와 manual cleanup을 돕는다. UI shortcut을 MCP나 Plugin API capability로
바꾸지 않으며 shortcut 숙련도는 artifact quality gate가 아니다.

| native action | 유용한 목적 | 자동화 시 주의 |
| --- | --- | --- |
| deep select, layer menu | nested layer를 structure 손상 없이 target | API는 UI gesture 대신 explicit node ID/query를 사용 |
| parent/child/sibling navigation | hierarchy 이해 | tree traversal과 동일시하지 않음 |
| select matching layers, multi-edit | semantic role이 같은 target의 controlled batch edit | component/property/token/explicit target predicate와 readback 필요 |
| multi-edit variants | variant 간 corresponding layer 일관성 | current component structure와 public contract 확인 |
| Smart selection, Tidy up | 탐색 중 spacing·ordering 정리 | final repeatable relationship은 Auto Layout으로 표현 |
| batch rename | 합의한 semantic name 적용 | broad text replace 금지; companion은 exact plan만 허용 |
| copy/paste properties | compatible appearance/layout transfer | token/component binding flatten 여부 확인 |
| measurement | spacing·size·relationship 검토 | automated exact claim은 metadata/readback을 우선 |

batch edit 전에는 same component property, semantic role, token binding 또는 explicit target처럼 equivalence
predicate를 정한다. 후에는 first/middle/last representative node와 unrelated instance를 확인한다. manual optical
correction은 scoped exception으로 남기고 global spacing rule로 일반화하지 않는다.

keyboard shortcut은 OS별로 달라지고 변경될 수 있다. 사용자가 exact shortcut을 요청하면 이 문서가 아니라
현재 Figma 공식 문서를 확인한다.
