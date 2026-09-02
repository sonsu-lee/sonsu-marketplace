# OpenAI prompt guidance

Read this file only when a named OpenAI model, product surface, or API configuration changes how the prompt should be written. This is a 2026-08-29 snapshot. If the user asks for the latest or current recommendation, retrieve the live official OpenAI documentation before making a model-specific claim.

## Shared structure

Use an outcome-first prompt. For complex work, select only the sections that change behavior:

```text
Role: [the model's function and relevant context]

# Goal
[the user-visible outcome]

# Success criteria
[what must be true before the answer or work is complete]

# Constraints
[hard policy, evidence, safety, permission, and scope limits]

# Tools
[non-obvious routing, side effects, and approval boundaries]

# Output
[required content, format, length, and tone]

# Stop rules
[when to ask, retry, fall back, abstain, or finish]
```

Do not emit every section by default. A short request that already contains the goal and output can remain one paragraph.

## Product surface

### Codex task prompt

State the desired repository or artifact outcome, relevant files or context, constraints, authorization boundary, completion criteria, and validation that matters. Let Codex inspect the workspace and choose implementation steps unless the path itself is required. Do not repeat standing Codex policies or narrate commands the agent can select itself.

### ChatGPT user prompt

State the requested result, relevant context or source material, audience, necessary constraints, and output shape. Add a role or personality only when it changes the result. Do not turn a one-shot request into a reusable system prompt unless the user asks for one.

### Responses API

Put stable identity, behavior, and cross-request rules in `instructions` or the appropriate high-authority message. Put the current task and dynamic user data in `input`. Stable content should precede dynamic content when prompt caching matters.

Use Markdown headings and lists for readable logical sections. Use XML tags when long supporting documents, examples, or untrusted data need explicit boundaries. Keep examples only when they encode a required output contract or fix a demonstrated failure.

Prefer Structured Outputs over a prose description of a JSON schema when the API integration can enforce that schema. Set `reasoning.effort` and `text.verbosity` as API controls; do not simulate them with repeated “think harder” or generic brevity instructions.

## Model profiles

### GPT-5.6 family

This profile applies to `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`. The official guidance distinguishes these models by capability, cost, and throughput, not by a different prompt format. Use the same lean, outcome-first structure unless evaluations show a model-specific failure.

- Rely on the model to infer ordinary execution steps. Provide domain context, hard constraints, approval boundaries, success criteria, and the ambiguity that should trigger a question.
- State each rule once and expose only relevant tools. Repeated policies can cause unnecessary checks and larger accumulated context.
- Do not add broad “be concise” instructions by default. Specify what a short answer must preserve and what it may omit, or use `text.verbosity` in the API.
- Keep the same outcome-focused prompt in pro mode. Configure pro mode and reasoning effort in the API instead of asking the model to think harder or generate several candidates.
- For multi-step work, define safe in-scope actions and the external, destructive, costly, or scope-expanding actions that require confirmation.

### GPT-5.5

Use the same outcome-first structure, with slightly more explicit orchestration when the work is long-running, tool-heavy, or coding-focused.

- State the expected outcome, success criteria, allowed side effects, evidence rules, output shape, and stopping conditions.
- Avoid detailed step-by-step guidance unless the exact path is a product requirement.
- For coding agents, add reuse expectations, test or validation requirements, acceptance criteria, and the condition for continuing versus asking for help only when those points are not already supplied by the environment.
- Define personality and collaboration style for customer-facing work because the default is direct and task-oriented.
- Keep reusable static instructions first and dynamic context last. Do not add the current date unless a user-local, policy-effective, or business timezone date matters.

### GPT-5.4, GPT-5.3 Codex variants, and other GPT-5 models

Use the shared outcome-first structure. Do not invent a special syntax or claim a behavioral difference without current official evidence. When exact optimization matters, retrieve the official guidance for the exact model and preserve the model name rather than substituting a newer model.

### Unknown or non-OpenAI model

Use the shared model-neutral structure. Do not apply an OpenAI-specific behavior claim. If the user wants vendor-specific optimization, consult that vendor's primary documentation when available.

## Final model-aware check

Before returning the prompt, confirm that:

1. the named model and product surface were preserved;
2. API configuration was not embedded as fake natural-language reasoning instructions;
3. every section changes behavior;
4. the prompt contains each rule once;
5. success, permissions, evidence, output, and stopping conditions remain when they matter.

## Official sources

- https://developers.openai.com/api/docs/guides/latest-model
- https://developers.openai.com/api/docs/guides/prompt-engineering
- https://learn.chatgpt.com/docs/build-skills
