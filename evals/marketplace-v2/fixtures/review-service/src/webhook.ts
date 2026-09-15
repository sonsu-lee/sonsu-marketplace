export type TrustedWebhook = {
  kind: "account.updated";
  accountId: string;
};

export function receiveWebhook(payload: unknown): TrustedWebhook {
  return payload as TrustedWebhook;
}
