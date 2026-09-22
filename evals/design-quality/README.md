# Design quality evaluation

`cases.json`은 디자인 일반론을 실제 판단 행동으로 바꾸는 behavior fixture다. 특정 문구보다
`primary_question`, 정보 역할·표현 추적, environment, 위험 분류, 사전 등록 metric과 차원별 floor가
산출물에 나타나는지를 평가한다.

자동 단위 테스트는 JSON 계약과 허위 통과를 검사한다. 실제 모델 행동, Figma canvas, browser runtime,
대표 사용자 결과는 별도 실행 근거가 없으면 `not_run`이다.

```bash
python3 -m unittest discover -s evals/design-quality -p 'test_*.py'
python3 scripts/validate_madia_design_catalog.py docs/research/madia-design-practice-catalog.json
```

DESIGN.md 통합 검사는 고정 npm 패키지를 실제 실행한다. Python 3.9+, Node.js 18+, npm과
POSIX 환경에서 아래 명령을 사용한다. 최초 실행에는 패키지 다운로드가 필요할 수 있다.

```bash
DESIGN_MD_INTEGRATION=1 python3 -m unittest discover -s evals/design-quality -p 'test_design_md*.py'
```

이미 패키지가 npm cache에 있으면 `npm_config_offline=true`를 함께 지정할 수 있다. 통합
검사를 켜지 않은 기본 실행은 npm 부재·실행 실패·출력 오류 처리만 검사하고, 공식 parser/linter
사례와 세 플러그인의 독립 실행 검사는 skipped로 남긴다. 통합 검사는 YAML·필수 항목·참조·
순서·key 오류, 빈 token, 숫자 spacing, 공식 제목 별칭과 대비 경고의 상태·종료 코드·digest를
확인한다. 복합 token의 객체·배열 내부 참조, UTF-8 오류 입력의 digest, 프로젝트 `.npmrc`의
연결·캐시 설정 적용과 실행 옵션 제외도 검사한다. 같은 이름·버전의 가짜 로컬·workspace·npx cache
패키지가 실행되지 않는지 확인한다. 매 실행은 임시 디렉터리에 새로 설치하며 다운로드 cache는 재사용한다.
실제 Figma나 제품 UI 품질 검증은 포함하지 않는다.
