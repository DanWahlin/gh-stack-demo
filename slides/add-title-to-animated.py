import re
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "github-stacked-prs-animated-base.pptx"
TITLE = ROOT / "slides/title-only.pptx"
OUTPUT = ROOT / "github-stacked-prs.pptx"


def unpack(src, dst):
    with zipfile.ZipFile(src) as z:
        z.extractall(dst)


def pack(src, dst):
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(Path(src).rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(src).as_posix())


def read(path):
    return path.read_text(encoding="utf-8")


def write(path, text):
    path.write_text(text, encoding="utf-8")


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        base, title = td / "base", td / "title"
        unpack(BASE, base)
        unpack(TITLE, title)

        # Import the generated title slide as slide4. Existing slides remain byte-for-byte intact.
        shutil.copy2(title / "ppt/slides/slide1.xml", base / "ppt/slides/slide4.xml")
        rel_src = read(title / "ppt/slides/_rels/slide1.xml.rels")
        rel_src = re.sub(r'<Relationship[^>]+Type="[^"]+/notesSlide"[^>]*/>', "", rel_src)
        rel_src = rel_src.replace('../media/image-1-1.png', '../media/image1.png')
        write(base / "ppt/slides/_rels/slide4.xml.rels", rel_src)

        # Register slide4 with the presentation and place it first in slide order.
        rels_path = base / "ppt/_rels/presentation.xml.rels"
        rels = read(rels_path)
        title_rel = '<Relationship Id="rId10" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide4.xml"/>'
        rels = rels.replace('</Relationships>', title_rel + '</Relationships>')
        write(rels_path, rels)

        pres_path = base / "ppt/presentation.xml"
        pres = read(pres_path)
        pres = pres.replace('<p:sldIdLst>', '<p:sldIdLst><p:sldId id="259" r:id="rId10"/>', 1)
        write(pres_path, pres)

        types_path = base / "[Content_Types].xml"
        types = read(types_path)
        slide_type = '<Override PartName="/ppt/slides/slide4.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        types = types.replace('</Types>', slide_type + '</Types>')
        write(types_path, types)

        # Update slide counts/title inventory without rewriting the surrounding OOXML namespaces.
        app_path = base / "docProps/app.xml"
        app = read(app_path).replace('<Slides>3</Slides>', '<Slides>4</Slides>')
        app = app.replace('<vt:variant><vt:i4>3</vt:i4></vt:variant></vt:vector></HeadingPairs>',
                          '<vt:variant><vt:i4>4</vt:i4></vt:variant></vt:vector></HeadingPairs>')
        app = app.replace('<vt:vector size="6" baseType="lpstr">', '<vt:vector size="7" baseType="lpstr">', 1)
        marker = '<vt:lpstr>Office Theme</vt:lpstr>'
        app = app.replace(marker, marker + '<vt:lpstr>Getting Started with GitHub Stacked PRs</vt:lpstr>', 1)
        write(app_path, app)

        pack(base, OUTPUT)
        print(OUTPUT)


if __name__ == "__main__":
    main()
