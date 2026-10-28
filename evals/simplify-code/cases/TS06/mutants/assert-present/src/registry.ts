export class Registry {
  private items = new Map<string, string>();
  set(key: string, value: string): void { this.items.set(key, value); }
  remove(key: string): void { this.items.delete(key); }
  get(key: string): string { return this.items.get(key)!; }
}
