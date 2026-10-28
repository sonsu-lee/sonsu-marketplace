import { box } from "../src/box.js";
const text: "hello" = box("hello" as const).value;
const input = { count: 1 };
const count: number = box(input).value.count;
const bool: boolean = box(true).value;
void [text, count, bool];
const nil: null = box(null).value;
const absent: undefined = box(undefined).value;
function roundTrip<T>(value: T): T {
  return box(value).value;
}
void [nil, absent, roundTrip];
