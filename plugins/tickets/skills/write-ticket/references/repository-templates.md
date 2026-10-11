# 저장소 이슈 양식 설치

대상 GitHub 저장소에 버그·요청 issue form을 설치하는 절차다. 양식 파일은 [`../assets/github/ISSUE_TEMPLATE/`](../assets/github/ISSUE_TEMPLATE/)에 있다.

## 절차

1. 사용자가 저장소 이슈 양식 설정을 요청했을 때만 실행한다.
2. `1-bug.yml`, `2-request.yml`, `config.yml`을 대상 저장소의 `.github/ISSUE_TEMPLATE/`에 복사한다. 같은 이름의 파일이 이미 있으면 덮어쓰기 전에 차이를 알린다.
3. 대상 저장소의 기능에 맞춰 `config.yml`에 `contact_links`를 추가한다.
   - `gh api repos/{o}/{r} --jq .has_discussions`가 `true`이면 Questions 항목을 추가한다.
   - `gh api repos/{o}/{r}/private-vulnerability-reporting --jq .enabled`가 `true`이면 보안 제보 항목을 추가한다.

   ```yaml
   contact_links:
     - name: Questions
       url: https://github.com/{o}/{r}/discussions
       about: Ask and answer questions in Discussions.
     - name: Security vulnerability
       url: https://github.com/{o}/{r}/security/advisories/new
       about: Report a vulnerability privately.
   ```

4. 저장소 언어가 한국어이면 label·description을 [섹션 제목 대응](ticket-writing.md#출력-언어와-섹션-제목)에 따라 바꾼다.
5. `gh api orgs/{o}/issue-types --jq '.[].name'`가 비어 있지 않으면 `labels` 대신 `type: Bug`·`type: Feature`를 쓴다. 해당 이름이 목록에 없으면 `labels`를 유지한다. 개인 계정이라 404가 나오면 조직 타입이 없는 것으로 본다.
6. 다음 사실을 사용자에게 보고한다.
   - `required` 검증은 공개 저장소에서만 동작한다.
   - `blank_issues_enabled: false`여도 쓰기 이상 권한자에게는 "유지 관리자만" 표시가 붙은 빈 이슈가 계속 보인다.
7. PR 양식 설치는 `git` 플러그인의 `write-pr`이 맡는다. 설치한 파일의 commit·push는 `git` 플러그인의 `commit`·`push`가 맡는다.
