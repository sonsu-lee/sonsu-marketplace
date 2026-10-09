---
type: career-facts
updated: 2026-10-01
---

# 경력 원본

## 조직

| ID | 조직 | 기간 | 고용 형태 | 직함 | 공개 | 공개 표기 |
| --- | --- | --- | --- | --- | --- | --- |
| O-001 | Acme Mart | 2023-04 – 현재 | 정사원 | Frontend Engineer | public | - |
| O-002 | Bright Labs | 2022-10 – 2023-02 | 정사원 | Junior Frontend Developer | public | - |

## 프로젝트

### P-001 Checkout rewrite

- 조직: O-001
- 기간: 2024-01 – 2024-09
- 개요: Acme Mart 온라인 스토어의 checkout 화면을 Next.js 14 기반으로 다시 만든 프로젝트
- 규모: 전체 12명 / 팀(FE) 4명
- 역할: Frontend Engineer. checkout 결제 단계 화면과 CI 파이프라인 담당
- 담당 공정: 要件定義 – / 基本設計 – / 詳細設計 ● / 実装 ● / テスト ○ / 運用保守 –
- 기술 환경:
  - 언어: TypeScript 5.4
  - FW·라이브러리: React 18, Next.js 14, Vitest
  - DB: -
  - 인프라·클라우드: -
  - 도구: GitHub Actions
- 공개: public
- 공개 표기: -

## 사실

### F-001 checkout CI 시간을 13분에서 4분으로 줄였다

- 프로젝트: P-001
- 기간: 2024-05 – 2024-06
- 내 몫: CI 병목 분석, 의존성 캐시와 병렬 job 도입
- 팀 몫: 팀원들이 변경된 workflow를 리뷰했다
- 수치: CI 소요 시간 13분 → 4분. GitHub Actions 실행 기록의 2주 중앙값, 2024-06 측정
- 출처: GitHub Actions 실행 기록(2024-06, 2주 중앙값)
- 기술: GitHub Actions, Vitest, TypeScript 5.4
- 상태: confirmed
- 공개: public
- 공개 표기: -
- 메모: -

### F-002 Beacon Bank 연동 checkout의 p75 INP를 480ms에서 190ms로 개선했다

- 프로젝트: P-001
- 기간: 2024-03 – 2024-08
- 내 몫: Beacon Bank 결제 연동 단계의 긴 작업 분석, 입력 핸들러 분할과 불필요한 렌더링 지연(defer)
- 팀 몫: QA가 회귀 테스트를 맡았다
- 수치: p75 INP 480ms → 190ms. RUM 대시보드, 2024-02와 2024-08 비교
- 출처: RUM 대시보드 캡처(2024-02, 2024-08)
- 기술: React 18, Next.js 14, INP, Chrome DevTools Performance
- 상태: confirmed
- 공개: anonymize
- 공개 표기: a partner bank / 提携銀行
- 메모: 연동 은행 이름은 계약상 공개하지 않는다

### F-003 주니어 2명의 코드 리뷰를 매주 맡았다

- 프로젝트: - (O-001 팀 업무)
- 기간: 2024-04 – 현재
- 내 몫: 주니어 엔지니어 2명의 PR을 매주 리뷰했다
- 팀 몫: -
- 수치: 없음
- 출처: -
- 기술: React 18, TypeScript 5.4
- 상태: self-reported
- 공개: public
- 공개 표기: -
- 메모: -

### F-004 내부 가격 도구 Project Nightjar의 프로토타입을 만들었다

- 프로젝트: - (O-001 사내 프로젝트)
- 기간: 2025-08 – 2025-10
- 내 몫: 프로토타입 화면 구현
- 팀 몫: 기획과 가격 로직은 가격팀이 맡았다
- 수치: 없음
- 출처: 사내 문서
- 기술: React 18, TypeScript 5.4
- 상태: confirmed
- 공개: private
- 공개 표기: -
- 메모: 미공개 사내 프로젝트

### F-005 번들 크기를 40% 줄였다

- 프로젝트: P-001
- 기간: 2024-01 – 2024-09
- 내 몫: 미상
- 팀 몫: 미상
- 수치: 번들 크기 40% 감소. 측정 방법·시점 미상
- 출처: 예전 이력서 문구에서 옮김
- 기술: Next.js 14
- 상태: unverified
- 공개: public
- 공개 표기: -
- 메모: 측정 자료를 찾지 못했다

### F-006 팀의 App Router 이전에서 20페이지 중 3페이지를 옮겼다

- 프로젝트: P-001
- 기간: 2024-06 – 2024-09
- 내 몫: checkout 관련 3페이지를 App Router로 옮겼다
- 팀 몫: tech lead가 이전을 계획·주도했고, 나머지 17페이지는 다른 팀원이 옮겼다
- 수치: 20페이지 중 3페이지
- 출처: PR 목록, 이전 계획 문서
- 기술: Next.js 14, React 18
- 상태: confirmed
- 공개: public
- 공개 표기: -
- 메모: -
