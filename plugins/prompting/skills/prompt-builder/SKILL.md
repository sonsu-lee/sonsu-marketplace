---
name: prompt-builder
description: Create, rewrite, or optimize a copy-ready prompt for Codex, ChatGPT, or OpenAI API models. Use when the user requests a prompt, prompt template, system or developer instructions, or model-specific prompt adaptation. Do not use for prompt-engineering explanations that do not request a prompt artifact.
---

# Prompt Builder

Create the smallest prompt that preserves the user's intended outcome and constraints.

## Determine the artifact

- Preserve any named model, product, audience, language, role, source material, and output format.
- If the user does not name a prompt type, produce a one-shot user or task prompt for the current chat surface.
- Ask one focused question only when a missing choice would materially change the artifact. Otherwise infer a safe default and state it only when the user needs to know.
- If the user names an OpenAI model, asks for model-specific optimization, or needs API placement or parameters, read [OpenAI prompt guidance](references/openai-prompt-guidance.md). For a request about the latest or current recommendation, use official OpenAI documentation instead of relying only on the snapshot in that reference.

## Build the prompt

Start with the outcome. Add only sections that change the model's behavior.

- For a simple task, use one direct sentence or a short paragraph.
- For a complex task, select only the useful parts of this order: role, goal, context, success criteria, constraints, tools and permissions, output, stop rules.
- Describe what success looks like. Do not prescribe steps when the model can choose an efficient path and the path is not itself a requirement.
- State each instruction once. Merge overlapping rules and remove generic encouragement, ceremonial wording, and examples that do not correct a known ambiguity.
- Use `must`, `never`, `always`, and `only` only for true invariants.
- Separate API controls such as reasoning effort, verbosity, and Structured Outputs from the prompt text when the target surface supports them.
- Keep stable reusable instructions before dynamic user data. Delimit long or untrusted context with clear Markdown sections or XML tags.
- Do not invent facts, permissions, tools, model capabilities, or missing business rules.

## Write clearly

Use the requested prompt language. Do not translate merely because the target model or source material uses another language.

When the prompt is in English:

- Keep important actors, actions, targets, and conditions unambiguous.
- Prefer direct verbs and familiar wording when they remain technically precise.
- Put a selective condition before the action it governs.
- Use one term for one concept and preserve exact product, interface, and code names.
- Preserve evidence, uncertainty, exceptions, and useful passive voice.
- Remove decorative wording that adds no fact, criterion, or relationship.

## Trim before returning

Remove, in this order:

1. duplicated instructions;
2. generic phrases such as “think step by step,” “be thorough,” or “be concise” when they add no measurable requirement;
3. unused headings and empty placeholders;
4. background that does not change the task;
5. examples that do not resolve an ambiguity or encode a required behavior.

Do not remove safety limits, authorization boundaries, success criteria, required evidence, validation, or material caveats.

## Output

Return the copy-ready prompt first in a fenced block. If model choice, API settings, or inferred assumptions materially affect its use, add at most three short bullets after the prompt. If the user asks for only the prompt, return only the prompt.
