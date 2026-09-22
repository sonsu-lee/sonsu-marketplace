from __future__ import annotations

import os
import unittest

import test_design_md as fixture


@unittest.skipUnless(os.environ.get("DESIGN_MD_INTEGRATION") == "1",
                     "set DESIGN_MD_INTEGRATION=1 to run the pinned npm package")
class DesignMdCompositeReferenceTests(unittest.TestCase):
    check_document = fixture.DesignMdIntegrationTests.check_document

    def test_missing_typography_dimension_reference_fails(self) -> None:
        report = self.check_document(
            '---\nname: Broken\ntypography:\n  body:\n'
            '    fontFamily: sans-serif\n    fontSize: "{spacing.missing}"\n---\n',
            "failed", 1, "broken-ref",
        )
        self.assertTrue(any("typography.body.fontSize" in f["message"]
                            for f in report["findings"] if f["rule"] == "broken-ref"))

    def test_missing_references_in_component_object_and_array_fail(self) -> None:
        for value, path in (
            ('{nested: "{spacing.missing}"}', 'components.button.padding.nested'),
            ('[16px, "{spacing.missing}"]', 'components.button.padding.1'),
        ):
            with self.subTest(value=value):
                report = self.check_document(
                    '---\nname: Broken\nspacing:\n  base: 16px\n'
                    f'components:\n  button:\n    padding: {value}\n---\n',
                    "failed", 1, "broken-ref",
                )
                self.assertTrue(any(path in f["message"] for f in report["findings"]
                                    if f["rule"] == "broken-ref"))

    def test_composite_reference_cycles_fail(self) -> None:
        for value in ('{nested: "{spacing.loop}"}', '[16px, "{spacing.loop}"]'):
            with self.subTest(value=value):
                self.check_document(
                    '---\nname: Broken\nspacing:\n  base: 16px\n'
                    '  loop: "{typography.body}"\ntypography:\n  body:\n'
                    '    fontFamily: "{spacing.loop}"\n'
                    f'components:\n  button:\n    padding: {value}\n---\n',
                    "failed", 1, "broken-ref",
                )

    def test_circular_typography_dimension_reference_fails(self) -> None:
        self.check_document(
            '---\nname: Broken\ntypography:\n  body:\n'
            '    fontFamily: sans-serif\n    fontSize: "{typography.body}"\n---\n',
            "failed", 1, "broken-ref",
        )

    def test_fenced_yaml_reference_is_checked(self) -> None:
        self.check_document(
            '---\nname: Broken\nspacing:\n  base: 16px\n---\n'
            '```yml\ntypography:\n  body:\n    fontFamily: sans-serif\n'
            '    fontSize: "{spacing.missing}"\n```\n',
            "failed", 1, "broken-ref",
        )

    def test_reference_text_outside_token_groups_is_not_checked(self) -> None:
        self.check_document(
            '---\nname: "{spacing.missing}"\ndescription: "{spacing.missing}"\n'
            'omitted:\n  - section: typography\n    reason: "{spacing.missing}"\n'
            'spacing:\n  base: 16px\n---\n'
            'Use `{spacing.missing}` to describe an absent token.\n'
            '```text\ntypography:\n  body:\n    fontSize: "{spacing.missing}"\n```\n',
            "passed", 0,
        )

    def test_valid_composite_references_and_aliases_pass(self) -> None:
        self.check_document(
            '---\nname: Valid\nspacing:\n  base: 16px\n  alias: "{spacing.base}"\n'
            'typography:\n  body:\n    fontFamily: sans-serif\n'
            '    fontSize: "{spacing.alias}"\ncomponents:\n  button:\n'
            '    typography: "{typography.body}"\n'
            '    padding: {top: "{spacing.base}", sides: ["{spacing.alias}"]}\n---\n',
            "passed", 0,
        )

    def test_yaml_alias_cycles_fail(self) -> None:
        for definition in ('button: &button\n    padding: *button',
                           'button:\n    padding: &padding [16px, *padding]'):
            with self.subTest(definition=definition):
                self.check_document(
                    '---\nname: Cycle\nspacing:\n  good: 16px\ncomponents:\n  '
                    + definition + '\n---\n', "failed", 1, "broken-ref",
                )

    def test_component_only_composite_values_are_tokens(self) -> None:
        for value in ('[16px, 8px]', '{top: 16px, bottom: 8px}'):
            with self.subTest(value=value):
                self.check_document(
                    f'---\nname: Composite\ncomponents:\n  button:\n    padding: {value}\n---\n',
                    "passed", 0,
                )

    def test_empty_composite_values_are_not_tokens(self) -> None:
        for value in ('[]', '{}', '{nested: []}'):
            with self.subTest(value=value):
                self.check_document(
                    f'---\nname: Empty\ncomponents:\n  button:\n    padding: {value}\n---\n',
                    "failed", 1, "tokens",
                )


if __name__ == "__main__":
    unittest.main()
