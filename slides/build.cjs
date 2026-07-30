const path = require('path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('/root/.hermes/profiles/work/skills/pptx/scripts/html2pptx.js');

async function main() {
  const pptx = new pptxgen();
  pptx.defineLayout({ name: 'CUSTOM_WIDE', width: 10, height: 5.625 });
  pptx.layout = 'CUSTOM_WIDE';
  pptx.author = 'Dan Wahlin';
  pptx.subject = 'GitHub Stacked PRs';
  pptx.title = 'GitHub Stacked PRs: Smaller Reviews Without Serial Development';
  pptx.company = 'Code with Dan';
  pptx.lang = 'en-US';
  pptx.theme = { headFontFace: 'Arial', bodyFontFace: 'Arial', lang: 'en-US' };

  for (let i = 1; i <= 3; i++) {
    const file = path.join(__dirname, `slide${i}.html`);
    const { slide } = await html2pptx(file, pptx);
    slide.addNotes(`Video visual ${i} of 3. See VIDEO.md for narration and shot timing.`);
  }

  await pptx.writeFile({ fileName: path.join(__dirname, '..', 'github-stacked-prs.pptx') });
}

main().catch(err => { console.error(err); process.exit(1); });
