type Route = {
  path: `/${string}`;
  auth: "public" | "user" | "admin";
};

const routes = {
  home: { path: "/", auth: "public" },
  settings: { path: "/settings", auth: "user" },
} satisfies Record<string, Route>;

const settingsPath: "/settings" = routes.settings.path;
void settingsPath;

const immutable = {
  draft: ["submitted"],
} as const satisfies Record<string, readonly string[]>;

// @ts-expect-error readonly configuration must not accept later mutation.
immutable.draft.push("cancelled");

const inferredMutable = { enabled: true } satisfies { enabled: boolean };

// @ts-expect-error contextual typing preserves the literal true here.
inferredMutable.enabled = false;

const explicitlyMutable: { enabled: boolean } = { enabled: true };
explicitlyMutable.enabled = false;

type Config = { timeout?: number };
const inferredConfig = {} satisfies Config;

// @ts-expect-error satisfies does not add an absent optional property to {}.
inferredConfig.timeout = 1_000;

const mutableConfig: Config = {};
mutableConfig.timeout = 1_000;

declare const externalValue: unknown;

// @ts-expect-error unknown data must be narrowed or parsed before it satisfies User.
externalValue satisfies { id: string };
