export interface ProviderV3Response {
  requestId?: string;
  value: string;
}

export function readValue(response: ProviderV3Response): string {
  return response.value;
}
