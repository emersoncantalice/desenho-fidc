"""Reúne somente a vista FIDC e os cronogramas prontos de diagramas/.

Execução: python modelos/gerar_pdf_cronogramas_fidc.py
Dependências: reportlab, svglib, pillow, pypdf (também aceita tmp/pdf-deps).
O PDF consolidado anterior e os arquivos de origem permanecem intactos.
"""
from pathlib import Path
import sys
import hashlib
import io
import math
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from reportlab.lib.utils import ImageReader
from svglib.svglib import svg2rlg
from PIL import Image
from pypdf import PdfReader

OUTPUT = ROOT/'output/pdf/apresentacao-cronogramas-nova-mesa-fidc-documentos.pdf'
PREVIOUS = ROOT/'output/pdf/apresentacao-consolidada-arquitetura-backlogs-cronogramas.pdf'
SOURCES = [
    ('Nova mesa FIDC | Arquitetura', 'proposta-nova-mesa.svg'),
    ('Comparativo | Equipes e prazos', 'comparativo-equipes-fidc.png'),
    ('Base FIDC | Comparativo dos cronogramas', 'cronograma-fidc.png'),
    ('Base FIDC | 2 desenvolvedores', 'cronograma-fidc-2-devs.png'),
    ('Base FIDC | 3 desenvolvedores', 'cronograma-fidc-3-devs.png'),
    ('Base FIDC | 4 desenvolvedores', 'cronograma-fidc-4-devs.png'),
    ('Pendencia documental | Comparativo dos cronogramas', 'cronograma-pendencia-documental.png'),
    ('Pendencia documental | 2 desenvolvedores', 'cronograma-pendencia-documental-2-devs.png'),
    ('Pendencia documental | 3 desenvolvedores', 'cronograma-pendencia-documental-3-devs.png'),
    ('Pendencia documental | 4 desenvolvedores', 'cronograma-pendencia-documental-4-devs.png'),
]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def vector_drawing(path):
    # Converte os marcadores de setas, não suportados pelo svglib, em polígonos.
    # A transformação ocorre apenas em memória; o SVG original não é alterado.
    root = ET.parse(path).getroot()
    ns = '{http://www.w3.org/2000/svg}'
    for parent in list(root.iter()):
        for elem in list(parent):
            if elem.tag != ns+'polyline' or 'marker-end' not in elem.attrib:
                continue
            nums = list(map(float, re.findall(r'[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?', elem.attrib['points'])))
            points = list(zip(nums[0::2], nums[1::2]))
            x,y = points[-1]
            px,py = next(pt for pt in reversed(points[:-1]) if pt != (x,y))
            length = math.hypot(x-px, y-py)
            ux,uy = (x-px)/length, (y-py)/length
            unit = 0.6*float(elem.attrib.get('stroke-width','1'))
            coords = [(x-9*unit*ux+5*unit*uy,y-9*unit*uy-5*unit*ux),
                      (x+unit*ux,y+unit*uy),
                      (x-9*unit*ux-5*unit*uy,y-9*unit*uy+5*unit*ux)]
            arrow = ET.Element(ns+'polygon', {'points':' '.join(f'{a},{b}' for a,b in coords),
                                             'fill':elem.attrib.get('stroke','#52606d')})
            parent.insert(list(parent).index(elem)+1, arrow)
            del elem.attrib['marker-end']
    return svg2rlg(io.BytesIO(ET.tostring(root)))

def main():
    protected = [ROOT/'diagramas'/filename for _,filename in SOURCES]
    if PREVIOUS.exists():
        protected.append(PREVIOUS)
    hashes = {path:digest(path) for path in protected}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pageCompression=1)
    pdf.setTitle('Nova mesa FIDC e pendência documental | Cronogramas de 2, 3 e 4 devs')
    pdf.setAuthor('Planejamento de arquitetura')
    pdf.setSubject('Diagramas originais: arquitetura FIDC, comparativos e seis cronogramas por equipe')
    width, margin, bottom = 1190.55, 24, 43
    content_width = width-2*margin
    for index,(title,filename) in enumerate(SOURCES,1):
        path = ROOT/'diagramas'/filename
        if path.suffix == '.svg':
            drawing = vector_drawing(path)
            scale = content_width/drawing.width
            content_height = drawing.height*scale
        else:
            with Image.open(path) as im:
                content_height = im.height*content_width/im.width
        height = content_height+margin+bottom
        pdf.setPageSize((width,height))
        key = f'pagina-{index}'
        pdf.bookmarkPage(key)
        pdf.addOutlineEntry(title,key,0)
        if path.suffix == '.svg':
            pdf.saveState()
            pdf.translate(margin,bottom)
            pdf.scale(scale,scale)
            renderPDF.draw(drawing,pdf,0,0)
            pdf.restoreState()
        else:
            # Incorpora os pixels originais sem recorte nem reamostragem.
            pdf.drawImage(ImageReader(str(path)),margin,bottom,content_width,content_height)
        pdf.setStrokeColorRGB(.84,.88,.93)
        pdf.line(margin,32,width-margin,32)
        pdf.setFillColorRGB(.34,.39,.47)
        pdf.setFont('Helvetica',8)
        pdf.drawString(margin,18,'Fonte: diagramas/'+filename)
        pdf.drawRightString(width-margin,18,f'{index} / {len(SOURCES)}')
        pdf.showPage()
    pdf.save()
    reader = PdfReader(str(OUTPUT))
    assert len(reader.pages)==len(SOURCES)
    assert len(reader.outline)==len(SOURCES)
    for i,(_,filename) in enumerate(SOURCES):
        assert filename in reader.pages[i].extract_text()
        if filename.endswith('.png'):
            assert len(reader.pages[i].images)==1
    assert all(digest(path)==original for path,original in hashes.items())
    print(f'PDF: {OUTPUT}\nPáginas: {len(reader.pages)}\nFontes e PDF anterior: preservados (SHA-256).')

if __name__ == '__main__':
    main()
