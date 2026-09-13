import type { TrustedWebhook } from "./webhook";

export function dispatch(event: TrustedWebhook): string {
  return `${event.kind}:${event.accountId}`;
}
