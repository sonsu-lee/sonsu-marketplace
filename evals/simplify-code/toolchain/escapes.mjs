import ts from 'typescript';
import { readFileSync } from 'node:fs';

function escapes(path) {
  const text = readFileSync(path, 'utf8');
  const source = ts.createSourceFile(path, text, ts.ScriptTarget.Latest, true);
  const found = [];
  function visit(node) {
    const assertion = ts.isAsExpression(node) || ts.isTypeAssertionExpression(node);
    const constAssertion = assertion && ts.isTypeReferenceNode(node.type) &&
      node.type.typeName.getText(source) === 'const';
    if (node.kind === ts.SyntaxKind.AnyKeyword ||
        (assertion && !constAssertion) || ts.isNonNullExpression(node)) {
      found.push(`${ts.SyntaxKind[node.kind]}:${node.getText(source)}`);
    }
    ts.forEachChild(node, visit);
  }
  visit(source);
  // TypeScript identifies directives in comments, not in strings or ordinary code.
  for (const directive of source.commentDirectives || []) {
    found.push(text.slice(directive.range.pos, directive.range.end).trim());
  }
  const scanner = ts.createScanner(ts.ScriptTarget.Latest, false, ts.LanguageVariant.Standard, text);
  for (let token = scanner.scan(); token !== ts.SyntaxKind.EndOfFileToken; token = scanner.scan()) {
    if ((token === ts.SyntaxKind.SingleLineCommentTrivia ||
         token === ts.SyntaxKind.MultiLineCommentTrivia) &&
        /@ts-nocheck\b/.test(scanner.getTokenText())) {
      found.push('@ts-nocheck');
    }
  }
  return found;
}
const original = escapes(process.argv[2]);
const submitted = escapes(process.argv[3]);
for (const item of submitted) {
  const index = original.indexOf(item);
  if (index < 0) console.log(item);
  else original.splice(index, 1);
}
