# GitHub Issues

## Select the applicable template

Read the target repository's contribution guidance and issue templates on its
default branch. Inspect `.github/ISSUE_TEMPLATE/`, including issue forms and
`config.yml`, and any legacy issue template in the supported locations. A local
issue template or chooser configuration suppresses the inherited
`.github/ISSUE_TEMPLATE` directory; do not merge in the owner's defaults merely
because no local template matches the request. When repository templates and
configuration are absent, check the owner's public `.github` repository for an
inherited default. Do not assume the working branch contains the templates that
GitHub currently offers.

Choose the template matching the request rather than the first file. Preserve
required form fields, labels, and other mandated metadata. A form's YAML is a
creation schema, not the issue description: when using an API or CLI, compose
the answers as readable sections and apply relevant properties separately.
Required checkboxes must reflect known facts; do not claim a reproduction,
search, or agreement merely because the template asks for it.

If several templates remain materially different after reading their purpose,
clarify the intended issue type. Use the bundled fallback only when none applies.

`config.yml` contact links can route questions, support, ideas, or security
reports away from issues, for example to Discussions or private vulnerability
reporting. When the request belongs to such a route, report the destination
instead of filing an issue; do not create a discussion unless asked.

## Review issue and project metadata

Inspect existing repository labels, eligible assignees, milestones, and available
issue types. Recommend relevant values using the [common criteria](metadata.md).
GitHub milestones belong to a repository; they are not Linear project milestones
or GitHub Projects iterations.

Priority and estimates may be represented by organization issue fields, Projects
custom fields, or established label conventions. Inspect the actual setup rather
than assuming universal fields or inventing a Linear-style mapping. For a project
field, identify the intended project, its field definitions and options, and the
issue's project item. Distinguish an organization issue field displayed in a
project from a project-local field with the same name.

Use the existing scale and classification convention; do not create fields or
add the issue to an unrelated project just to supply priority or an estimate.
If no such convention exists, report the field as not configured rather than
adding an arbitrary value to the body or creating a priority label.

Organization issue fields are not currently populated through issue templates.
Apply them with supported field operations when authorized. Project membership
and project-local field values may also require separate operations from issue
creation. Verify each intended result; successful issue creation alone does not
prove that project fields were set. Report unavailable access or tooling and
unapplied recommendations separately.

## Publish and connect work

Confirm the owner and repository before creating or updating an issue. Search
existing issues in that scope and inspect likely duplicates. Respect any existing
Linear sync instead of independently creating a second ticket there.

For splits, record intended parent/child or dependency relationships through
supported tracker operations, using sub-issues for parent and child; mentioning
an issue in prose is not proof that a structured relation was created. Issue
types classify an issue but do not create hierarchy.

A public repository's issues are visible to anyone. For a suspected
vulnerability, follow the repository's security policy and use private
vulnerability reporting when it is enabled, not an issue.

Files attached to an issue in a public repository can be accessed without
authentication. GitHub CLI can attach local images and videos when the user
has push access; otherwise link the evidence or leave the upload to the user.
A partial upload still creates the issue, so check which attachments rendered
before reporting them.

A reference to `#123` is scoped to its repository; use `owner/repository#123` or
the full URL when crossing repositories. Partial PRs should reference the issue
without completion keywords. GitHub closing keywords in a PR description apply
when the PR targets the default branch; merging such a PR closes the referenced
issue. Do not use a completion link for an intermediate PR or assume a
non-default-branch merge closes the issue. Reuse the PR skill for actual PR work.

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
