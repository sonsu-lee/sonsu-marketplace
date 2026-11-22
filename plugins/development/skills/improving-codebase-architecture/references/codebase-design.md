# Codebase design vocabulary

Use the project's domain language along with these architectural terms:

- **Module:** any unit with an interface and implementation, from a function to
  a package or end-to-end slice.
- **Interface:** everything a caller must know, including invariants, ordering,
  failure modes, configuration, and performance, not just types.
- **Depth:** useful behavior behind an interface relative to what a caller
  needs to learn. Avoid measuring depth by line counts.
- **Seam:** where behavior can change without editing that location; where the
  interface lives. An **adapter** is an implementation fulfilling the interface.
- **Leverage:** capability available to callers through the interface.
  **Locality:** how well knowledge, changes, faults, and verification are
  concentrated for maintainers.

Apply the deletion test: complexity spread across callers indicates the module
was carrying useful responsibility; complexity that disappears suggests a
pass-through. Test through the interface where practical. One adapter alone does
not establish that a second implementation is needed. Compare alternative
interfaces when a consequential choice remains; do not invent abstractions for
hypothetical variation.
