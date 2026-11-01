# 출처와 변형 기록

> 영문 정본: [provenance.md](provenance.md) (`fcbe81d` 기준 번역).
> 사람이 읽기 위한 번역본이며 에이전트는 이 파일을 읽지 않는다.

[coji/natural-japanese][source]의 커밋 `03bc944a0c4a9f0b2a66eab065b30de5c529bf08`을
upstream의 [MIT 라이선스](../LICENSE) 그대로(저작권 2026 coji) 가져와 만든 이
변형을 감사, 갱신, 설명할 때 읽는다. 산문을 편집하는 데는 필요하지 않다.

지침과 보조 가이드는 영어로 번역했으며, 일본어 예시와 언어학적 구분은 유지했다.
런타임은 upstream의 탐지기, 일본어 진단 문구, 의존성 범위를 그대로 유지한다.
로컬 수정은 코드 펜스로 감싼 예시를 구조 통계에서 제외하고, 탐지기 임계값을
바꾸지 않으면서 baseline 비교 사이에 문서 전체 결과가 안정적으로 유지되게 한다.
이 변형은 클라이언트별 메타데이터를 제거하고, 설치된 스킬을 기준으로 리소스를
확인하며, runner 실패를 명시적으로 다루고, 기술 산문도 대상에 남긴다.
upstream의 `semantic.py`와 `exp` 진단(선택 사항이며 약 1 GB의 모델 다운로드),
코퍼스 보정, 개발용 검사, 릴리스/설치 스캐폴딩, 벤치마크 픽스처는 제외했다.
남은 워크플로 어디에서도 제외한 구성 요소를 호출하지 않는다.

[source]: https://github.com/coji/natural-japanese/tree/03bc944a0c4a9f0b2a66eab065b30de5c529bf08/skills/natural-japanese
