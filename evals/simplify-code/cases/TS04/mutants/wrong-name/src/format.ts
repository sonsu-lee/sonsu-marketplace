type Row = { name: string; count: number };
export function format(row: Row): string {
  return `${row.name.toUpperCase()}:${row.count}`;
}
