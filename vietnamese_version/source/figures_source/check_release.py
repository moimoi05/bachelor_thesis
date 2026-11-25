"""Artifact-level regression checks; requires PyMuPDF and Pillow for QA only."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from xml.etree import ElementTree
import pymupdf as fitz
from PIL import Image, ImageOps, ImageDraw

S = Path(__file__).resolve().parents[1]
FIGURES = {
    "1.1": "mci-progression-timeline",
    "2.1": "concept-survival", "2.2": "concept-longitudinal", "2.3": "concept-sources",
    "2.4": "concept-fusion", "2.5": "cp-concept-general", "2.6": "literature-gates",
    "3.1": "final-pipeline", "3.2": "cohort-construction", "3.3": "input-three-sources",
    "3.4": "mri-preprocessing", "3.5": "mri-registration", "3.6": "clinical-18-inputs",
    "3.7": "concat-baseline", "3.8": "mr-outer-product", "3.9": "pair-update-routes", "3.10": "outer-vs-cp",
    "3.11": "gated-residual-route", "3.12": "rcfree-update", "3.13": "temporal-model",
    "3.14": "evaluation-map", "4.1": "empirical-training", "4.2": "empirical-ipcw-roc",
    "4.3": "survival-km", "A.1": "master-pipeline",
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(reference=None,pdf=None,render=None):
    chapters = [*sorted((S / 'chapters').glob('chapter*.tex')), S / 'chapters/appendix.tex']
    tex = '\n'.join(p.read_text(encoding='utf-8') for p in chapters)
    figures = re.findall(r'\\includegraphics\[[^]]*\]\{image/([^}]+)\.pdf\}', tex)
    assert figures == list(FIGURES.values()), figures
    result = {'figures': {}, 'evidence_identical': None, 'tables_identical': None}
    for name in figures:
        path=S/'image'/f'{name}.pdf'
        doc=fitz.open(path); assert len(doc)==1
        page = doc[0]
        assert page.get_drawings() and page.get_fonts() and page.get_text().strip(), name
        assert all(doc.extract_font(font[0])[3] for font in page.get_fonts()), name
        svg = ElementTree.parse(S / 'image' / f'{name}.svg')
        assert any(node.tag.endswith('}text') and ''.join(node.itertext()).strip()
                   for node in svg.iter()), name
        assert bool(page.get_images()) == (name in {'input-three-sources', 'mri-preprocessing', 'mri-registration'}), name
        assert '\ufffd' not in page.get_text(), name
        outside=[]
        for block in page.get_text('dict')['blocks']:
            for row in block.get('lines',[]):
                for span in row['spans']:
                    if not page.rect.contains(fitz.Rect(span['bbox'])):
                        outside.append(span['text'])
        assert not outside,(name,outside)
        with Image.open(S/'image'/f'{name}.png') as im:
            dpi=im.info.get('dpi',(0,0)); assert min(dpi)>299,(name,dpi)
            dimensions=im.size
        result['figures'][name]={'pdf_size_pt':list(page.rect)[2:],
          'png_dimensions':dimensions,'dpi':dpi,'text_spans_outside_page':outside}
    if reference:
        reference=Path(reference)
        for directory in ('evidence', 'tables'):
            actual = {p.relative_to(S): digest(p) for p in (S / directory).rglob('*') if p.is_file()}
            expected = {p.relative_to(reference): digest(p) for p in
                        (reference / directory).rglob('*') if p.is_file()}
            assert actual == expected, directory
            result[f'{directory}_identical'] = True
    if pdf:
        doc=fitz.open(pdf); result['pages']=len(doc)
        text='\n'.join(p.get_text() for p in doc)
        result['lambda_count']=sum(text.count(c) for c in ['λ','𝜆','𝝀','𝝺','𝞴'])
        assert result['lambda_count']>0
        assert '\ufffd' not in text
        captions = {}
        for i, p in enumerate(doc):
            for label in re.findall(r'Hình\s+((?:\d+|A)\.\d+)\s*:', p.get_text()):
                assert label not in captions, label
                captions[label] = i + 1
        assert set(captions) == set(FIGURES), captions
        appendix = doc[captions['A.1'] - 1]
        assert appendix.rect.width > appendix.rect.height
        listed = {}
        for page in doc.pages(0, captions["1.1"] - 1):
            words = page.get_text("words")
            for link in page.get_links():
                destination = link.get("page", -1)
                if destination < 0:
                    continue
                linked_words = [
                    word[4] for word in words
                    if link["from"].contains(fitz.Point((word[0] + word[2]) / 2, (word[1] + word[3]) / 2))
                ]
                if len(linked_words) >= 2 and linked_words[0] == "Hình" and linked_words[1] in captions:
                    listed[linked_words[1]] = destination + 1
        assert listed == captions, (listed, captions)
        result['figure_caption_pages'] = captions
        if render:
            out=Path(render);out.mkdir(exist_ok=True,parents=True)
            thumbs=[]
            for i,p in enumerate(doc):
                path=out/f'page-{i+1:02}.png'
                p.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(path)
                with Image.open(path) as im:
                    thumb=ImageOps.contain(im.convert('RGB'),(238,337))
                    tile=Image.new('RGB',(258,370),'#e7e7e7');tile.paste(thumb,((258-thumb.width)//2,20))
                    ImageDraw.Draw(tile).text((8,3),str(i+1),fill='black')
                    thumbs.append(tile)
            for start in range(0,len(thumbs),12):
                contact=Image.new('RGB',(258*4,370*3),'white')
                for j,im in enumerate(thumbs[start:start+12]):contact.paste(im,((j%4)*258,(j//4)*370))
                contact.save(out/f'contact-{start+1:02}.png')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reference');p.add_argument('--pdf');p.add_argument('--render');p.add_argument('--report')
    args=p.parse_args();r=audit(args.reference,args.pdf,args.render)
    payload=json.dumps(r,ensure_ascii=False,indent=2)
    if args.report:Path(args.report).write_text(payload,encoding='utf-8')
    print(payload)
