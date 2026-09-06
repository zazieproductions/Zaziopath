const fs = require('fs');
const assert = require('assert');
const html = fs.readFileSync('stewardship_receipt.html', 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new Function(script); // parse-only syntax check; DOM code is exercised in the browser
for (const marker of [
  'Stewardship Receipt',
  'localStorage',
  'download',
  'Interpretation Sovereign',
  'Reparative Auteur',
  'let readings be declined',
  'Am I communicating, or constructing a story',
  'Nothing filed yet'
]) assert(html.includes(marker), `missing console marker: ${marker}`);
assert(!html.includes('fetch('), 'console must not make network requests');
assert(!html.includes('XMLHttpRequest'), 'console must not make network requests');
console.log('stewardship receipt smoke test: PASS');
