type Row = { name: string; count: number };
function hasName(row: Row): boolean {
  return typeof row.name === "string";
}
export function format(row: Row): string {
  if (!hasName(row)) throw new Error("invalid name");
  if (typeof row.count !== "number") throw new Error("invalid count");
  return `${row.name}:${row.count}`;
}
