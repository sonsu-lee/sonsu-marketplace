# omp 모델·실행 차이

이 자료는 Engineering을 omp에서 직접 설치한 선택·legacy 호출자를 위한 실행 참고다.
기본 5개 배포에는 Engineering 역할·gate가 없으며, 개발 실행·task·todo·session·review는
omp 순정 기능이 맡는다. 기본 구성에 아래 `task.agentModelOverrides`를 추가하지 않는다.
`omp-profiles.json`은 기존 Engineering gate와 실행·독립 검토 소비자를 위해 보존한다.

역할 agent 파일은 Claude Code와 공유하므로 omp 모델은 사용자 설정 `task.agentModelOverrides`로만
적용한다. `@smol`·`@default` 같은 별칭은 사용자의 `modelRoles`로 해석되며, effort는 그 역할의
`:level` 접미사가 정한다. omp의 `task` 도구는 호출마다 model이나 effort를 지정할 수 없다.
override가 없으면 Claude frontmatter 모델이 쓰이지만 `enabledModels`에 막히거나 다른 모델로
대체될 수 있으므로 관측 모델을 기록하고, 필수 검토의 관측 모델이 요청과 다르면 `blocked`/`not_run`으로 둔다.
