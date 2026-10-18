export default {
  defaultIgnores: false,
  parserPreset: {
    parserOpts: {
      headerPattern: /^(\w+)(?:\((.*)\))?!?: (.+)$/,
      headerCorrespondence: ["type", "scope", "subject"],
      breakingHeaderPattern: /^(\w+)(?:\((.*)\))?!: (.+)$/,
      noteKeywords: ["BREAKING CHANGE", "BREAKING-CHANGE"],
    },
  },
  rules: {
    "type-empty": [2, "never"],
    "type-case": [2, "always", "lower-case"],
    "type-enum": [
      2,
      "always",
      [
        "feat", "fix", "docs", "refactor", "perf", "test",
        "build", "ci", "chore", "style", "revert",
      ],
    ],
    "scope-case": [2, "always", "lower-case"],
    "subject-empty": [2, "never"],
    "subject-case": [
      2, "never", ["sentence-case", "start-case", "pascal-case", "upper-case"],
    ],
    "subject-full-stop": [2, "never", "."],
    "header-max-length": [2, "always", 72],
    "body-leading-blank": [2, "always"],
    "body-max-line-length": [2, "always", 72],
    "footer-leading-blank": [2, "always"],
    "footer-max-line-length": [2, "always", 72],
  },
};
