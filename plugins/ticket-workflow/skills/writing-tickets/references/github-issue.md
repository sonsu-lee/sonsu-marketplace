# GitHub Issues

Use this procedure when drafting or publishing a GitHub issue.

## Workflow

1. **Select a template.** Read contribution guidance and issue templates on
   the target repository's default branch, including issue forms, `config.yml`
   and legacy templates in supported locations. If repository templates and
   configuration are absent, check the owner's public `.github` repository
   for inherited defaults. Choose the template matching the request; if
   materially different templates remain, clarify the intended issue type.
   Use the bundled fallback only when none applies. Preserve required fields,
   labels and other mandated metadata. For API or CLI creation, turn form
   answers into readable sections and apply properties separately. Required
   checkboxes must reflect known facts, not assumed reproduction, search or
   agreement.
2. **Check routing and visibility.** If a `config.yml` contact link routes the
   request elsewhere, such as Discussions or private vulnerability reporting,
   report that destination instead of filing an issue; create a discussion only
   when asked. For a suspected vulnerability, follow the security policy; if it
   names no channel, use private vulnerability reporting when enabled, not an
   issue.
3. **Review metadata.** Inspect repository labels, eligible assignees,
   milestones and issue types; recommend values using the
   [common criteria](metadata.md). Inspect the actual priority and estimate
   setup and use its scale and classification convention. For project fields,
   identify the intended project, field definitions and options, and issue
   project item; distinguish organization fields displayed in a project from
   same-named project-local fields. If no convention exists, report the field
   as not configured, rather than inventing a body value or priority label.
   Do not create fields or add an issue to an unrelated project to supply a
   priority or estimate.
4. **Publish and connect.** Confirm owner and repository before creation or
   update; search that scope and inspect likely duplicates. Respect existing
   Linear sync instead of creating a second independent ticket. For splits,
   record parent/child or dependency relations through supported operations,
   using sub-issues for parent and child. Apply organization fields through
   supported operations when authorized; project membership and project-local
   fields may also require separate operations. Verify each intended result and
   report unavailable access or tooling and unapplied recommendations
   separately.
5. **Handle evidence and PR links.** In a public repository, attach local images
   and videos with GitHub CLI only when the user has push access; otherwise
   link evidence or leave upload to the user. Check which attachments rendered
   before reporting them. Use `owner/repository#123` or a full URL for
   cross-repository references. Link intermediate PRs without completion
   keywords; reuse the PR skill for actual PR work.

## Gotchas

- A local issue template or chooser configuration suppresses the inherited
  `.github/ISSUE_TEMPLATE` directory, even when no local template matches. The
  working branch may not contain the templates GitHub currently offers.
- Form YAML is a creation schema, not an issue description. Organization issue
  fields cannot currently be populated through issue templates.
- GitHub milestones belong to a repository, not Linear project milestones or
  GitHub Projects iterations. Priority and estimates may use organization
  issue fields, Projects custom fields or established labels; do not assume
  universal fields or invent a Linear-style mapping.
- Issue creation alone does not prove project fields were set. A prose mention
  does not prove a structured relation was created; issue types classify work
  but do not create hierarchy.
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
