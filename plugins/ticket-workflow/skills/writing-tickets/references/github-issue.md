# GitHub Issues

Use these GitHub differences with the workflow in [Writing tickets](../SKILL.md).

## Templates and routing

- Read contribution guidance and issue templates on the target repository's
  default branch, including issue forms, `config.yml`, and legacy templates in
  supported locations. If repository templates and configuration are absent,
  check the owner's public `.github` repository for inherited defaults.
- For API or CLI creation, turn form answers into readable sections and apply
  properties separately. Required checkboxes must reflect known facts, not
  assumed reproduction, search, or agreement.
- If a `config.yml` contact link routes the request elsewhere, such as
  Discussions or private vulnerability reporting, report that destination
  instead of filing an issue; create a discussion only when asked. If the
  security policy names no channel for a suspected vulnerability, use private
  vulnerability reporting when enabled, not an issue.

## Fields and relationships

- GitHub offers repository labels, eligible assignees, milestones, and issue
  types. Priority and estimates may use organization issue fields, Projects
  custom fields, or established labels; inspect the actual configuration.
  Without a convention, report the field as not configured, rather than
  inventing a body value or priority label.
- For project fields, identify the intended project, field definitions/options,
  and issue project item. Distinguish organization fields displayed in a project
  from same-named project-local fields. Organization fields, project membership,
  and project-local fields may require separate supported operations.
- Use sub-issues for parent/child relationships. Issue types classify work but
  do not create hierarchy. GitHub milestones belong to a repository, not Linear
  project milestones or GitHub Projects iterations.

## Evidence and PR references

- In a public repository, attach local images and videos with GitHub CLI only
  when the user has push access; otherwise link evidence or leave upload to the
  user. Check which attachments rendered before reporting them.
- Use `owner/repository#123` or a full URL for cross-repository references.

## Gotchas

- A local issue template or chooser configuration suppresses the inherited
  `.github/ISSUE_TEMPLATE` directory, even when no local template matches. The
  working branch may not contain the templates GitHub currently offers.
- Form YAML is a creation schema, not an issue description. Organization issue
  fields cannot currently be populated through issue templates.
- Do not assume universal priority/estimate fields or invent a Linear-style
  mapping. Creating the issue does not also set its Projects fields.
- Public repository issues are visible to anyone, and their attachments are
  accessible without authentication. A partial upload still creates the issue.
- `#123` is scoped to its repository. GitHub closing keywords in a PR
  description apply when the PR targets the default branch, and merging it
  closes the referenced issue; do not assume a non-default-branch merge does.

## Sources

- [Configuring issue templates][templates]
- [Default community health files][defaults]
- [Linking pull requests to issues][linking]
- [Setting organization issue field values][issue-fields]
- [Projects priority and estimate fields][project-fields]
- [Adding sub-issues][sub-issues]
- [Privately reporting a security vulnerability][private-reporting]
- [Attaching files][attaching]
- [Attaching files with GitHub CLI][attaching-cli]

[templates]: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
[defaults]: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
[linking]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
[issue-fields]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-and-managing-issue-fields
[project-fields]: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects
[sub-issues]: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues
[private-reporting]: https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability
[attaching]: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files
[attaching-cli]: https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli
