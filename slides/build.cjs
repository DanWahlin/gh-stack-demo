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
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 8.18, y: 0.16, w: 1.18, h: 0.31,
      rectRadius: 0.06,
      fill: { color: '1A5D2A' },
      line: { color: '2EA043', width: 1 }
    });
    slide.addText('gh.io/stacks', {
      x: 8.18, y: 0.16, w: 1.18, h: 0.31,
      fontFace: 'Arial', fontSize: 10.5, bold: true,
      color: 'FFFFFF', underline: false, align: 'center', valign: 'mid',
      margin: 0,
      hyperlink: { url: 'https://gh.io/stacks' }
    });
    slide.addImage({
      path: path.join(__dirname, 'github-invertocat.png'),
      x: 9.48, y: 0.15, w: 0.33, h: 0.33,
      hyperlink: { url: 'https://github.com' }
    });
    slide.addNotes(`Video visual ${i} of 3. See VIDEO.md for narration and shot timing.`);
  }

  await pptx.writeFile({ fileName: path.join(__dirname, '..', 'github-stacked-prs.pptx') });
}

main().catch(err => { console.error(err); process.exit(1); });
