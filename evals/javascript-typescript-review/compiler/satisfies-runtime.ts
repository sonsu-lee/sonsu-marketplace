type User = { id: string };

const externalValue: any = JSON.parse('{"id":42}');
const user = externalValue satisfies User;

console.log(`satisfies-does-not-validate-runtime:${typeof user.id}`);
