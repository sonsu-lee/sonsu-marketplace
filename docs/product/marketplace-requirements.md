# 마켓플레이스 요구사항

- Status: Current
- Last reviewed: 2026-09-23

## 목표

Codex와 OMP의 host baseline 위에 필요한 domain judgment와 external artifact contract만 독립 설치하는
로컬 Git marketplace를 유지합니다. 출처·license·runtime prerequisite와 host별 load 결과를 추적합니다.

## 요구사항

- Codex와 OMP catalog는 exact 10개 plugin을 같은 이름과 `1.0.0` version으로 제공해야 합니다.
- 두 host는 exact 31개 공통 skill을 읽어야 하며 OMP skill name은 전역으로 유일해야 합니다.
- 각 plugin은 다른 marketplace plugin, router, setup skill, hook, fixed model roster나 continuity engine 없이
  핵심 기능을 수행해야 합니다.
- 일반 구현·debugging·test·Git·웹 조사·문장 교정·memory·session resume는 host baseline에 남깁니다.
- 외부 파일은 repository, exact commit, license와 포함 범위를 기록합니다. consulted-only 자료와 runtime
  dependency는 재배포 material과 구분합니다.
- Code Intelligence는 Codex에서만 pinned mcpls fallback metadata를 선언하고 OMP에서는 native LSP를
  사용해야 합니다. installer, trust bypass, secret 또는 user-specific path를 포함하지 않아야 합니다.
- Figma connector metadata는 Codex에만 선언하고 OMP에서는 current host가 노출한 official capability를
  사용해야 합니다. capability가 없으면 다른 API/writer를 추정하지 않아야 합니다.
- package 선택은 code edit, remote ticket/PR, review 게시, rename 또는 canvas mutation 권한을 만들지 않아야 합니다.
- 정적 계약, model-free native loader와 behavior smoke를 분리해 검증해야 합니다. 미실행을 성공으로
  표시하지 않고 blocker를 기록해야 합니다.
- raw prompt export나 collector endpoint를 marketplace default로 켜지 않아야 합니다. host와 operator가
  log retention/export/deletion을 소유해야 합니다.
- secret을 repository에 저장하지 않아야 합니다.

## 제외 범위

- 공개 marketplace hosting과 사용자 계정의 자동 install/activation
- host baseline을 다시 구현하는 general engineering/research/writing/memory package
- 삭제한 package 이름의 alias, wrapper 또는 deprecated path
- 요청 없는 commit, push, PR/issue/review 게시, deploy와 Figma mutation
- cache, `.sonsu/continuity`와 `.engineering` artifact의 자동 이동·삭제

## 완료 기준

catalog/manifest/path/version/inventory 정적 계약, Codex·OMP native loader 결과와 대표 routing/behavior 결과가
각각 evidence로 남고, package README·migration·license 문서가 현재 major cutover를 설명해야 합니다.
