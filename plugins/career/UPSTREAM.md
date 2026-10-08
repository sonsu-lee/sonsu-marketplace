# Career 출처

- 작성 방식: 독자 작성. 외부 스킬·프롬프트·템플릿의 파일이나 문구를 복사하거나 번역해 포함하지 않음.
- 확인일: 2026-10-07
- 배포 범위: Codex 정본과 생성된 Claude Code 패키지, omp 기본 배포. 다섯 스킬, 공통 reference와
  작업 공간 템플릿. hook과 script는 없음.
- 라이선스: 이 플러그인에는 현재 별도 라이선스를 선언하지 않음.

## 설계 참고

아래 저장소는 모두 MIT 라이선스이며, 동작 관점만 참고했습니다.

| 출처와 고정 revision | 참고한 관점 | 포함하지 않은 부분 |
| --- | --- | --- |
| [career-ops-hq/career-ops](https://github.com/career-ops-hq/career-ops/tree/24745c5f8a6b2ee56d7c25176d05c4dfe97c5b3b) | 원본 독점, 수치 창작 금지, 철회한 주장, six-second clarity, bullet 공식, 상투어 목록, 라운드별 평가자, plan/practice/debrief | 공고 스캔·지원 자동화, PDF 생성, 모드 원문 |
| [CaesiumY/claude-interview-agents](https://github.com/CaesiumY/claude-interview-agents/tree/9dc438a69c0c78cf01e05ddd2dc53cb6837125df) | 한 번에 한 질문, 꼬리질문 0~2개, 리허설 중 피드백 금지, 회고 A/B/C, 자기 판정 3단계, PSR, 작성자와 평가자 분리 | 점수 배점표와 3년차 체크리스트 원문, 명령·에이전트 파일 |
| [younnieCutler/japan-career-agent](https://github.com/younnieCutler/japan-career-agent/tree/ff0d4d07c0cea33f797dd88904f7f8308ad58f57) | Unknown 원칙, "JD는 렌즈를 바꾸지 사실을 바꾸지 않는다", Matched/Missing/Unknown, 棚卸し 질문 순서, 한 턴 질문 3개 이하 | Python runtime과 ledger 스키마 |
| [unagi/jtr-generator](https://github.com/unagi/jtr-generator/tree/3539b63a33a9849227b46ff7dd3d667210e4fba5) | 職務経歴書 순서와 NG 패턴, 履歴書 일관성 | PDF 렌더링 |

## 실무·공식 자료

- [Tech Interview Handbook: resume](https://www.techinterviewhandbook.org/resume/): 미국식 resume 형식과 bullet 작성.
- [Tech Interview Handbook: software engineering interview guide](https://www.techinterviewhandbook.org/software-engineering-interview-guide/): 미국 면접 라운드 구성.
- [GreatFrontEnd: RADIO framework](https://www.greatfrontend.com/front-end-system-design-playbook/framework): 프론트엔드 시스템 설계 진행 틀.
- 厚生労働省 履歴書様式例: [宮城県 안내](https://www.pref.miyagi.jp/soshiki/koyou/rirekisho.html), [青森労働局 안내](https://jsite.mhlw.go.jp/aomori-roudoukyoku/news_topics/topics/_00051.html).
- [スキルシートの項目](https://proengineer.internous.co.jp/content/columnfeature/8336): スキルシート 기본 구성.
