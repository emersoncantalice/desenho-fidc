"""One-page executivo V2: entregáveis e cronograma linear, em A4 paisagem."""
from pathlib import Path
import hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/one-page-executivo-entrega-1-v2.pdf'
PREVIOUS = ROOT / 'output/pdf/one-page-executivo-entrega-1.pdf'
previous_hash = hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()
OUT.parent.mkdir(parents=True, exist_ok=True)
# A área lógica permite controlar alinhamento sem perder texto vetorial no PDF.
W,H = 1200,848.5
SCALE = 841.89/W
NAVY, BLUE, INK, MUTED = '#001E62', '#0033CC', '#202B3C', '#536174'
PALE, LIGHT, LINE = '#EDF2FF', '#F4F6FA', '#CCD7ED'
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial', boldItalic='Arial-Bold')
c=canvas.Canvas(str(OUT),pagesize=(841.89,H*SCALE))
c.scale(SCALE,SCALE)
c.setTitle('Entrega 1 - Plano executivo visual - Versão 2')
c.setAuthor('Arquitetura de crédito')
text_boxes=[]


def box(x,y,w,h,fill,radius=0,stroke=None):
    c.setFillColor(HexColor(fill))
    if stroke:
        c.setStrokeColor(HexColor(stroke));c.setLineWidth(1)
    c.roundRect(x,H-y-h,w,h,radius,fill=1,stroke=bool(stroke))


def line(x1,y1,x2,y2,color=LINE,width=1):
    c.setStrokeColor(HexColor(color));c.setLineWidth(width)
    c.line(x1,H-y1,x2,H-y2)


def circle(x,y,r,fill,stroke=None,width=1):
    c.setFillColor(HexColor(fill))
    if stroke:
        c.setStrokeColor(HexColor(stroke));c.setLineWidth(width)
    c.circle(x,H-y,r,fill=1,stroke=bool(stroke))


def text(value,x,y,w,size=13,color=INK,bold=False,maxh=42,leading=None,align=0):
    p=Paragraph(value,ParagraphStyle('p',fontName='Arial-Bold' if bold else 'Arial',
        fontSize=size,leading=leading or size*1.3,textColor=HexColor(color),alignment=align))
    _,h=p.wrap(w,maxh)
    assert h<=maxh+.1,(value,h,maxh)
    assert 0<=x and x+w<=W and 0<=y and y+h<H-12,(value,x,y,w,h)
    text_boxes.append((x,y,w,h,value))
    p.drawOn(c,x,H-y-h)


box(0,0,W,105,NAVY)
text('NOVA MESA FIDC',40,18,600,12,'#CEDCFF',True,18)
text('Entrega 1',40,42,190,34,'#FFFFFF',True,45)
text('Plano executivo de prazos, premissas e trade-offs',260,57,590,15,'#FFFFFF',False,22)
text('DATA-ALVO',942,18,218,11,'#CEDCFF',True,16)
text('11/01/2027',942,40,218,32,'#FFFFFF',True,43)

text('O QUE SERÁ ENTREGUE',40,121,700,13,BLUE,True,19)
text('2 FEATURES',1035,121,125,11,MUTED,True,18,align=2)
for x,title,body in [
    (40,'API de simulação síncrona',
     'Simulação e resultado salvos na base.<br/>Resposta na mesma chamada com resultado e identificador.'),
    (610,'API de análise de crédito assíncrona',
     'Análise automática vinculada à simulação salva.<br/>Aceite com protocolo e retorno posterior do resultado ao parceiro.'),
]:
    box(x,148,550,83,PALE,7)
    box(x,148,5,83,BLUE,2)
    text(title,x+19,160,512,17,NAVY,True,23)
    text(body,x+19,191,512,13,maxh=35)

box(40,244,1120,35,LIGHT,5)
text('SEM ANÁLISE MANUAL NA ENTREGA 1',54,253,375,12.8,NAVY,True,18)
text('A decisão é automática. A análise julgamental mínima entra na Entrega 2.',445,253,701,12.5,MUTED,maxh=18)

text('CRONOGRAMA LINEAR',40,299,600,15,BLUE,True,21)
circle(900,310,5,BLUE)
text('Marco definido',913,302,115,11.5,MUTED,maxh=17)
circle(1054,310,5,'#FFFFFF',BLUE,2)
text('Proposta',1067,302,93,11.5,MUTED,maxh=17)

for x,w,label in [(40,480,'NOVEMBRO 2026'),(520,320,'DEZEMBRO 2026'),(840,320,'JANEIRO 2027')]:
    box(x,333,w,26,LIGHT)
    text(label,x,339,w,11,MUTED,True,15,align=1)
box(1005,369,150,131,PALE,7)
line(120,410,1080,410,LINE,4)
phases=[
    ('16/11/2026','Início preliminar','Preparação técnica<br/>e dependências',True),
    ('20/11/2026','Contratos e REF','Regras de simulação<br/>e análise automática',True),
    ('24/11/2026','Arquitetura definida','Desenho da Entrega 1<br/>e integrações',True),
    ('18/12/2026','Desenvolvimento','25/11 a 18/12<br/>APIs, vínculo e testes',False),
    ('30/12/2026','Integração','21 a 30/12<br/>Fluxo completo e falhas',False),
    ('08/01/2027','Homologação','04 a 08/01<br/>Aceite e preparação',False),
    ('11/01/2027','Entrega 1','Disponibilização<br/>e acompanhamento',True),
]
for i,(date,title,detail,defined) in enumerate(phases):
    x=40+i*160;cx=x+80
    text(date,x+5,374,150,17,BLUE if defined else NAVY,True,24,align=1)
    circle(cx,410,10,BLUE if defined else '#FFFFFF',BLUE,2.5)
    if defined:circle(cx,410,3,'#FFFFFF')
    text(title,x+3,434,154,12.7,NAVY,True,19,align=1)
    text(detail,x+3,460,154,11.8,MUTED,maxh=32,align=1)
text('Janelas de desenvolvimento, integração e homologação propostas; validar capacidade e disponibilidade no fim do ano.',40,512,1120,11.3,MUTED,maxh=17)

text('PREMISSAS QUE SUSTENTAM O PRAZO',40,535,1120,13,BLUE,True,19)
for x,title,body in [
    (40,'Definições de negócio','A REF deve contemplar as regras de simulação e análise de crédito. Não entra derivação inicialmente.'),
    (420,'Pessoas e ambientes','Confirmar realocação da equipe.'),
    (800,'Parceiro e implantação','Certificado mTLS enviado pelo parceiro até <b>12/12/2026</b>. Alinhar homologação, aceite e implantação para 11/01.'),
]:
    line(x,560,x+360,560,LINE,1)
    text(title,x,570,360,13,NAVY,True,19)
    text(body,x,594,360,12.4,MUTED,maxh=49)

box(40,647,1120,28,PALE,4)
text('PONTO DE ATENÇÃO',52,654,170,11.5,BLUE,True,16)
text('Priorizar o processo de modelagem da base de dados com o time de AD.',230,653,915,12.4,NAVY,maxh=18)

text('TRADE-OFFS DA REALOCAÇÃO',40,681,1120,13,BLUE,True,19)
cards=[
    (40,330,'Modernização da esteira',
     'Redução de <b>2 devs para 1 dev</b> desacelera a modernização da esteira automática. Novo prazo da frente a replanejar com resultado do orçamento de 2027.'),
    (390,420,'Desativação Serasa',
     'Migração da tela PTA para PCRE-JULG passa para <b>15/02/2027</b>. Renegociar com a Serasa a desativação da API String.'),
    (830,330,'Bureau Neurotech',
     'Migração de bureaux desacelera. Neurotech, com início previsto para 2026, passa integralmente para <b>1T27</b>.'),
]
for x,w,title,body in cards:
    box(x,709,w,106,LIGHT,7)
    text(title,x+15,726,w-30,21,NAVY,True,28)
    text(body,x+15,760,w-30,11.4,maxh=52,leading=12.8)

text('Fora da Entrega 1: API de status, análise manual e pendência documental. Entregas 2 e 3: datas a definir.',40,823,960,10,MUTED,maxh=15)
text('V2 | 12/11/2026',1040,823,120,10,MUTED,maxh=15,align=2)

# Checagem de caixas de texto para impedir sobreposições na página final.
for i,(x,y,w,h,value) in enumerate(text_boxes):
    for x2,y2,w2,h2,value2 in text_boxes[i+1:]:
        assert not (x<x2+w2-.1 and x+w>x2+.1 and y<y2+h2-.1 and y+h>y2+.1), (value,value2)
c.showPage();c.save()
reader=PdfReader(OUT)
assert len(reader.pages)==1
content=reader.pages[0].extract_text()
for required in ['16/11/2026','20/11/2026','24/11/2026','11/01/2027',
                 '15/02/2027','SEM ANÁLISE MANUAL NA ENTREGA 1','Serasa','Neurotech',
                 '12/12/2026','Confirmar realocação da equipe.','time de AD']:
    assert required in content,required
assert '\ufffd' not in content
assert all(name not in content.upper() for name in ['VITOR', 'GUSTAVO', 'AINE'])
assert hashlib.sha256(PREVIOUS.read_bytes()).hexdigest()==previous_hash
print(f'OK: V2 em uma pagina, textos e marcos validados; V1 preservada: {OUT}')
