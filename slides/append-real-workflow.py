import re
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "github-stacked-prs-animated-base.pptx"
NEW = ROOT / "slides/real-workflow-only.pptx"
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
    return path.read_bytes().decode("utf-8")


def write(path, text):
    path.write_bytes(text.encode("utf-8"))


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        base, new = td / "base", td / "new"
        unpack(BASE, base)
        unpack(NEW, new)

        # On the high-level workflow slide, sync is the complete maintenance command:
        # fetch, rebase when needed, push, and update PR/stack state.
        slide4_path = base / "ppt/slides/slide4.xml"
        slide4 = read(slide4_path)
        if '<a:t>gh stack rebase</a:t>' not in slide4:
            raise RuntimeError('Expected gh stack rebase text was not found on slide 4')
        write(slide4_path, slide4.replace('<a:t>gh stack rebase</a:t>', '<a:t>gh stack sync</a:t>', 1))

        # Import the generated terminal slide as slide5. Keep slides 1-3 byte-for-byte intact
        # and preserve slide 4's existing animation tree while changing only one text run.
        shutil.copy2(new / "ppt/slides/slide1.xml", base / "ppt/slides/slide5.xml")
        rels = read(new / "ppt/slides/_rels/slide1.xml.rels")
        rels = re.sub(r'<Relationship[^>]+Type="[^"]+/notesSlide"[^>]*/>', "", rels)
        rels = rels.replace('../media/image-1-1.png', '../media/image1.png')
        write(base / "ppt/slides/_rels/slide5.xml.rels", rels)

        # Append slide5 to the presentation.
        pres_rels_path = base / "ppt/_rels/presentation.xml.rels"
        pres_rels = read(pres_rels_path)
        ids = [int(x) for x in re.findall(r'Id="rId(\d+)"', pres_rels)]
        rid = f"rId{max(ids) + 1}"
        rel = f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide5.xml"/>'
        write(pres_rels_path, pres_rels.replace('</Relationships>', rel + '</Relationships>'))

        pres_path = base / "ppt/presentation.xml"
        pres = read(pres_path)
        slide_ids = [int(x) for x in re.findall(r'<p:sldId id="(\d+)"', pres)]
        entry = f'<p:sldId id="{max(slide_ids) + 1}" r:id="{rid}"/>'
        write(pres_path, pres.replace('</p:sldIdLst>', entry + '</p:sldIdLst>', 1))

        types_path = base / "[Content_Types].xml"
        types = read(types_path)
        slide_type = '<Override PartName="/ppt/slides/slide5.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        write(types_path, types.replace('</Types>', slide_type + '</Types>'))

        # Update document statistics without normalizing the rest of the package.
        app_path = base / "docProps/app.xml"
        app = read(app_path).replace('<Slides>4</Slides>', '<Slides>5</Slides>')
        app = app.replace('<vt:variant><vt:i4>4</vt:i4></vt:variant></vt:vector></HeadingPairs>',
                          '<vt:variant><vt:i4>5</vt:i4></vt:variant></vt:vector></HeadingPairs>')
        m = re.search(r'<TitlesOfParts><vt:vector size="(\d+)" baseType="lpstr">', app)
        if m:
            app = app.replace(m.group(0), m.group(0).replace(m.group(1), str(int(m.group(1)) + 1)), 1)
        app = app.replace('</vt:vector></TitlesOfParts>', '<vt:lpstr>Create Three Stacked Pull Requests</vt:lpstr></vt:vector></TitlesOfParts>', 1)
        write(app_path, app)

        pack(base, OUTPUT)
        print(OUTPUT)


if __name__ == "__main__":
    main()
