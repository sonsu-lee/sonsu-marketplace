# Linear

Use these Linear differences with the workflow in [Writing tickets](../SKILL.md).

## Templates

- Inspect workspace and team templates, including those available from parent
  teams, and team defaults.
- If creation supports a template parameter, use it and verify the result;
  otherwise incorporate required content and applicable properties explicitly.

## Fields and structure

- Inspect team/workspace labels, team members and ownership guidance, priority
  conventions, the team's estimate configuration, and the intended project's
  milestones. Use estimates only when enabled; do not enable them to fill a
  ticket.
- Follow team practice: sub-issues suit work too large for one issue but too
  small for a project; a project groups issues with a clear outcome or planned
  completion date and can span teams. Propose a new project rather than creating
  one unless authorized. Check parent auto-close settings before leaving
  integration or verification on the parent.

## Visibility and integration

- Before recording a suspected vulnerability, check team visibility and any
  GitHub Issues Sync connection to a public repository.
- Use actual Linear issue identifiers. Inspect the integration workflow before
  relying on status changes and check the resulting PR linkage.

## Gotchas

- Template defaults can differ for team members and non-members; a familiar
  name does not establish the default. Workspace templates cannot preset
  team-specific labels or statuses. API creation does not necessarily apply
  the UI default, and matching headings do not prove a named template was used.
- Sub-issues inherit the parent's team, priority and project, not its labels.
  Teams can configure the parent to close automatically when all sub-issues
  are done.
- In PR descriptions, `Fixes ENG-123` applies the configured merge status;
  `Refs ENG-123` links partial work without that status but can trigger other
  configured transitions; `Related to ENG-123` links context without status
  changes. PR comments do not create these links. A branch containing an issue
  ID can also link work automatically, so omitting closing keywords alone
  does not disable all automation.
- Linear supports multiple PRs per issue and multiple issues per PR. Its
  documented multi-PR behavior waits for the final linked PR to reach the
  configured state, but cannot account for future unlinked PRs or prove the
  ticket outcome is met.

## Sources

- [Issue templates](https://linear.app/docs/issue-templates)
- [GitHub integration](https://linear.app/docs/github)
- [Parent and sub-issues](https://linear.app/docs/parent-and-sub-issues)
- [Projects](https://linear.app/docs/projects)
