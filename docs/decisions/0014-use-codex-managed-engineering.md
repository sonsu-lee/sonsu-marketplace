# ADR 0014: Codex 전용 Engineering과 관리형 품질 게이트

- Status: Superseded
- Date: 2026-09-13
- Superseded by: [ADR 0015](0015-independent-skills.md) for public skill boundaries; retained quality gate principles are restated there
- Supersedes: ADR 0003의 Quality Engineering 독립 경계, ADR 0011의 고정 Fast Path 예산·계획 존재 기반 red-team, ADR 0012의 모델 역할 기본값·3+2 수정자 배정

## 문제

개발과 코드 품질 진입점이 나뉘고 직접/위임 실행·모델 정책이 중복되어 같은 요청에 절차가
달라졌다. 하네스가 이미 제공하는 세션 동작을 재정의하는 비용과, stale 근거를 산문으로만
관리하는 공백이 있었다. 불필요한 코드 경로와 절차를 제거하면서 필요한 검증은 보존한다.

## 결정

Codex/GPT 전용 배포로 정리하고 Quality Engineering의 8개 스킬을 Engineering 2.0.0에
통합한다. 별도 QE 패키지·호환 별칭은 두지 않는다. 일반 리뷰는 `engineering:review-quality`,
명시적 독립 리뷰 실행은 `requesting-code-review`, 관점 지정은 해당 focused 스킬이 맡는다.
리뷰 전용 요청은 소스 수정이나 전체 개발 DAG를 시작하지 않는다.

Product는 제품/도메인 규칙을 발견·합의하고 Engineering은 확정 규칙을 타입·상태·경계와 코드에
반영한다. Workflow는 Git·티켓·PR 전달, 나머지 전문 플러그인은 기존 산출물 경계를 유지한다.
공유 정책 원본에서 각 패키지에 필요한 참조만 생성해 단독 설치를 보존한다.

프로그램이 계약 스키마·DAG 순서·snapshot·receipt 최신성·idempotency·검사 실행·라운드 집계를
담당한다. AI가 위험·작업 경계·설계·지적·수정 영향을 판단한다. Codex의 native 실행 루프와
세션·spawn/wait/resume를 재사용하고 root가 할당을 소유한다. 별도 범용 scheduler나 전체 도구
인터셉터는 만들지 않는다. 등록한 unit의 진입/완료를 CLI가 거부할 수 있지만 임의 우회 호출이나
리뷰 의미의 진실성까지 보장하지 않는다. Stop hook은 관찰만 수행한다.

위험에 따라 checks → independent → red-team 정책을 선택한다. 기계적 작업은 검사로,
동작 변경은 독립 리뷰로, 고위험 경계는 별도 red-team으로 검증한다. 설계 깊이와 병렬화
가능성은 별도 축이다. 재개는 현재 계약·소스를 다시 확인하는 사건이며 영구 탈락 사유가 아니다.

일반 최초/전체 리뷰는 동일 고정 산출물·동일 기준의 Luna xhigh 5개 새 문맥을 기본으로 한다.
이는 사용자가 Sol xhigh 이상 단일 리뷰보다 추가 유효 문제를 확인한 경험을 채택한 운영 결정이다.
강제 관점 분할이나 다수결은 사용하지 않는다. 모든 원지적을 root가 검증하고 중복 원인을 합친다.
국소 수정은 이전 전체 근거와 Luna xhigh 1개를 연결하고 계약·의존 변화/영향 불명확성은 전체
5개를 다시 연다. 고위험 red-team은 별도 Astra high다. Sol의 중복 전수 검토는 추가하지 않는다.

자동 수정/재검토 상한 5라운드는 운영 보호장치다. 5개 리뷰어는 1라운드이며 호출수와 별개다.
세션·담당자 변경으로 상한을 초기화하지 않는다. 품질을 우선하고 그다음 전체 시간·재작업을
비교한다. 비용·토큰·지적 수를 통과 기준으로 사용하지 않는다.

정확한 모델/추론 기본값과 날짜·근거는 `shared/agent-policy/profiles.json`에 둔다. 사용자
지정은 우선하고 현재 root 설정을 바꾸지 않는다. 요청/관측 설정을 구분한다. 모델/host 갱신은
지원 스키마·상속·대표 행동 평가를 확인한 뒤 새 프로필 버전으로 반영한다. 기존 근거는 보존하되
새 정책 통과로 자동 승격하지 않는다.

## 근거와 한계

OpenAI Astra 가이드는 전체 SKILL/AGENTS의 충돌 감사, 승인된 작업 지속, 위임 범위·비례적
검증·작성 방식의 명시를 권고한다. 이미 host/common에 있는 내용을 모델 프롬프트에 복제하지
않고 필요한 차이만 제공한다. 공식 예시의 재귀 위임은 조정 가능한 예시로 보고 root 소유 정책에
맞춘다. [Astra 공식 가이드](https://developers.openai.com/api/docs/guides/latest-model#prompting-best-practices)

기본 하네스 활용과 앱의 계약 소유는 Codex platform 구조에 부합한다. 노력 수준은 모델별
지원과 평가 이득을 확인해야 하며 모델 간 같은 이름이 같은 계산량/품질을 뜻하지 않는다.
[Codex platform](https://developers.openai.com/blog/codex-as-a-platform),
[Reasoning effort](https://developers.openai.com/api/docs/guides/reasoning#reasoning-effort)

독립 다중 실행의 발견 범위와 오류 상관관계는 로컬 평가로 확인한다. 외부 연구나 사용자 관찰을
Luna5의 보편적 우월성으로 일반화하지 않는다. 실제 평가와 미실행·환경 한계는
[marketplace-v2](../../evals/marketplace-v2/README.md)에 기록한다.

## 이관

활성 Claude 배포·세션 fallback·runtime adapter를 제거한다. 연구 인용·역사적 ADR·원저작권·
라이선스·upstream provenance는 보존한다. 원본 패턴 카탈로그는 유지한다. 기존 v1 gate 기록은
읽을 수 있는 이력이며 새 v2 unit의 통과가 아니다. 설치 캐시와 사용자 설정은 별도 요청 없이
변경하지 않는다.
