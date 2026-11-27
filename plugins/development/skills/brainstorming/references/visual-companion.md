# Visual Companion Guide

Browser-based visual brainstorming companion for showing mockups, diagrams,
and options.

## When to Use

Decide per-question, not per-session. The test: **would the user understand
this better by seeing it than reading it?**

**Use the browser** when the content itself is visual:

- **UI mockups** — wireframes, layouts, navigation structures, component designs
- **Architecture diagrams** — system components, data flow, relationship maps
- **Side-by-side visual comparisons** — comparing two layouts, two color
  schemes, two design directions
- **Design polish** — when the question is about look and feel, spacing,
  visual hierarchy
- **Spatial relationships** — state machines, flowcharts, entity relationships
  rendered as diagrams

**Use the terminal** when the content is text or tabular:

- **Requirements and scope questions** — "what does X mean?", "which features
  are in scope?"
- **Conceptual A/B/C choices** — picking between approaches described in words
- **Tradeoff lists** — pros/cons, comparison tables
- **Technical decisions** — API design, data modeling, architectural approach selection
- **Clarifying questions** — anything where the answer is words, not a visual preference

A question *about* a UI topic is not automatically a visual question. "What
kind of wizard do you want?" is conceptual — use the terminal. "Which of these
wizard layouts feels right?" is visual — use the browser.

## How It Works

Use an available native preview, diagram, or browser surface after the user
accepts. This package does not install the upstream server, helper scripts, or
event recorder. If there is no suitable surface, offer a text sketch instead.

## The Loop

1. Show the mockup and give a brief text summary of what is on screen.
2. Ask the user what they think. The conversation is their primary feedback;
   a click alone is not approval of a design.
3. If feedback changes the current screen, show the revision. Only move to
   the next question when the current choice is settled.
4. Return to the conversation when the next question does not need a visual.

## Design Tips

- **Scale fidelity to the question** — wireframes for layout, polish for
  polish questions
- **Explain the question on each page** — "Which layout feels more
  professional?" not just "Pick one"
- **Iterate before advancing** — if feedback changes current screen, write a
  new version
- **2-4 options max** per screen
- **Use real content when it matters** — for a photography portfolio, use
  images authorized for the preview. Placeholder content obscures design issues.
- **Keep mockups simple** — focus on layout and structure, not pixel-perfect design
