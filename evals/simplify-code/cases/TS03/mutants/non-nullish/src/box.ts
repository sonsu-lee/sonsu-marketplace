export function box<T extends {}>(value: T): { value: T } {
  return { value };
}
