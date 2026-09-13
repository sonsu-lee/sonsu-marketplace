export interface ProviderSession {
  id: string;
}

export interface Provider {
  open(): Promise<ProviderSession>;
  execute(session: ProviderSession, input: string): Promise<string>;
  close(session: ProviderSession): Promise<void>;
}

export async function runWithProvider(provider: Provider, input: string): Promise<string> {
  const session = await provider.open();
  const result = await provider.execute(session, input);
  await provider.close(session);
  return result;
}
