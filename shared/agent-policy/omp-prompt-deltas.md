# omp 모델·실행 차이

역할 agent 파일은 Claude Code와 공유하므로 omp 모델은 사용자 설정 `task.agentModelOverrides`로만
적용한다. `@smol`·`@default` 같은 별칭은 사용자의 `modelRoles`로 해석되며, effort는 그 역할의
`:level` 접미사가 정한다. omp의 `task` 도구는 호출마다 model이나 effort를 지정할 수 없다.
override가 없으면 Claude frontmatter 모델이 쓰이지만 `enabledModels`에 막히거나 다른 모델로
대체될 수 있으므로 관측 모델을 기록하고, 필수 검토의 관측 모델이 요청과 다르면 `blocked`/`not_run`으로 둔다.
