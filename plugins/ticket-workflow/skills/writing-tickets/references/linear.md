# Linear

Use this procedure when drafting or publishing a Linear issue.

## Workflow

1. **Select a template.** Establish the workspace and team; inspect applicable
   workspace and team templates, including those available from parent teams,
   and team defaults. Use an explicitly selected applicable template or the
   relevant team/workspace template before the bundled fallback. Inspect its
   content and properties; preserve required answers and established metadata
   without inventing priority, assignment or due dates. If creation supports a
   template parameter, use it and verify the result; otherwise incorporate
   required content and applicable properties explicitly.
2. **Review metadata.** Inspect team/workspace labels, team members and
   ownership guidance, priority conventions, the team's estimate configuration
   and the intended project's milestones. Apply the
   [common criteria](metadata.md); do not ask the user for metadata already
   established by the template or project guidance. Explain priority using
   reported impact rather than treating every bug as urgent. Use the team's
   actual estimate scale only when estimation is enabled and scope permits a
   meaningful suggestion; do not enable estimates or substitute zero for an
   unknown value. Distinguish explicit assignees and valid template defaults
   from suggested owners. Select a milestone only in the intended project when
   the outcome fits its goal; if the project is unresolved, leave the milestone
   unresolved. Resolve actual user, label, project and milestone identities
   before publication; matching display names can be ambiguous.
3. **Choose structure.** Follow team practice: sub-issues suit work too large
   for one issue but too small for a project; a project groups issues with a
   clear outcome or planned completion date and can span teams. Propose a new
   project rather than creating one unless authorized. Check parent
   auto-close settings before leaving integration or verification on the parent.
4. **Publish and connect.** Search existing issues in scope before creation.
   Respect configured GitHub Issues Sync rather than recreating a synchronized
   counterpart as independent work. Before recording a suspected vulnerability,
   check team visibility and any sync to a public GitHub repository. Use actual
   Linear issue identifiers and preserve relations when updating or splitting.
5. **Link PR work.** Inspect the integration workflow before relying on status
   changes, establish the appropriate relationship and check the resulting
   linkage. Keep intermediate work non-closing; distinguish merged code from an
   outcome still needing deployment or verification. Reuse the PR skill for
   actual PR work; do not change integration settings to write a ticket.

## Gotchas

- Template defaults can differ for team members and non-members; a familiar
  name does not establish the default. Workspace templates cannot preset
  team-specific labels or statuses. API creation does not necessarily apply
  the UI default, and matching headings do not prove a named template was used.
- Sub-issues inherit the parent's team, priority and project, not its labels.
  Teams can configure the parent to close automatically when all sub-issues
  are done.
- A synced issue can expose vulnerability details in a public repository.
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
