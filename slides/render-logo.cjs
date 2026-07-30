const sharp = require('sharp');
const fs = require('fs');
const svg = fs.readFileSync('slides/github-invertocat.svg', 'utf8')
  .replace('fill="currentColor"', 'fill="#FFFFFF"');
sharp(Buffer.from(svg)).resize(256, 256).png().toFile('slides/github-invertocat.png');
