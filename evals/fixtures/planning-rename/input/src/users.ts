export function getUsr(id: number): string {
  return `user-${id}`;
}

export function describeUser(id: number): string {
  return getUsr(id);
}
