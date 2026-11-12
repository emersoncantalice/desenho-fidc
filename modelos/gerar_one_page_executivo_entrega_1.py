"""Gera um novo one-page executivo; preserva o material técnico anterior."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/one-page-executivo-entrega-1.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
W, H = 841.89, 595.28
NAVY, BLUE, INK, MUTED = '#001E62', '#0033CC', '#202B3C', '#526176'
PALE, LIGHT = '#EDF2FF', '#F4F6FA'
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial', boldItalic='Arial-Bold')
c = canvas.Canvas(str(OUT), pagesize=(W,H))
c.setTitle('Entrega 1 - Plano executivo de prazos, premissas e trade-offs')
c.setAuthor('Arquitetura de crédito')


def rect(x,y,w,h,color):
    c.setFillColor(HexColor(color))
    c.rect(x,H-y-h,w,h,fill=1,stroke=0)


def txt(value,x,y,w,size=10,color=INK,bold=False,maxh=40,leading=None):
    style=ParagraphStyle('body',fontName='Arial-Bold' if bold else 'Arial',fontSize=size,
                         leading=leading or size*1.28,textColor=HexColor(color))
    p=Paragraph(value,style)
    _,h=p.wrap(w,maxh)
    assert h<=maxh+.1,(value,h,maxh)
    assert y+h<=H-10,(value,y+h)
    p.drawOn(c,x,H-y-h)


rect(0,0,W,77,NAVY)
txt('NOVA MESA FIDC',30,14,520,9,'#C7D7FF',True,14)
txt('Entrega 1 - Plano executivo',30,34,560,24,'#FFFFFF',True,32)
txt('DATA-ALVO',650,13,160,9,'#C7D7FF',True,14)
txt('11/01/2027',650,33,160,25,'#FFFFFF',True,33)

txt('ESCOPO EM DUAS FEATURES',30,91,780,9,BLUE,True,14)
txt('<b>API de simulação síncrona</b><br/>Simulação salva na base; resultado e identificador na mesma chamada.',30,110,365,10,maxh=38)
txt('<b>API de análise de crédito assíncrona</b><br/>Análise vinculada à simulação salva e resultado posterior ao parceiro.',435,110,375,10,maxh=38)

txt('MARCOS DEFINIDOS',30,157,780,9,BLUE,True,14)
for x,date,label in [
    (30,'16/11/2026','Início dos trabalhos preliminares'),
    (230,'20/11/2026','Contratos e REF definidos'),
    (430,'24/11/2026','Arquitetura da Entrega 1 definida'),
    (630,'11/01/2027','Disponibilização da Entrega 1'),
]:
    rect(x,177,180,52,PALE)
    txt(date,x+10,185,160,16,BLUE,True,22)
    txt(label,x+10,209,160,8.7,maxh=13)

txt('CRONOGRAMA ATÉ A ENTREGA',30,245,450,10,BLUE,True,15)
txt('Janelas intermediárias propostas, sujeitas à validação da capacidade.',30,264,450,8.5,MUTED,maxh=14)
rect(30,285,450,23,NAVY)
txt('Período',40,290,110,9,'#FFFFFF',True,13)
txt('Resultado esperado',175,290,295,9,'#FFFFFF',True,13)
schedule=[
    ('16 a 24/11/2026','Preparação técnica; contratos e REF em 20/11; arquitetura definida em 24/11.'),
    ('25/11 a 18/12/2026','Desenvolvimento das duas APIs, persistência, correlação e testes dos componentes.'),
    ('21 a 30/12/2026','Integração ponta a ponta, testes de falhas e correções.'),
    ('04 a 08/01/2027','Homologação com o parceiro, aceite e preparação da implantação.'),
    ('11/01/2027','Disponibilização da Entrega 1 e acompanhamento inicial.'),
]
for i,(period,outcome) in enumerate(schedule):
    y=308+i*25
    rect(30,y,450,25,LIGHT if i%2==0 else '#FFFFFF')
    txt(period,40,y+4,125,8.8,NAVY,i==4,18)
    txt(outcome,175,y+3,295,8.8,maxh=23,leading=10.5)

txt('PREMISSAS PARA SUSTENTAR O PRAZO',510,245,300,10,BLUE,True,15)
for y,title,body in [
    (269,'Definições no prazo','Contratos e REF até 20/11; arquitetura da Entrega 1 até 24/11. Definir casos sem decisão automática.'),
    (326,'Capacidade e ambientes','Realocar a equipe e garantir acessos e ambientes. Validar disponibilidade no fim do ano.'),
    (383,'Homologação e implantação','Alinhar agenda do parceiro, critérios de aceite e janela de implantação para 11/01.'),
]:
    txt(title,510,y,300,9.5,NAVY,True,14)
    txt(body,510,y+17,300,9.2,maxh=35)

txt('TRADE-OFFS PARA REALOCAR CAPACIDADE',30,449,780,10,BLUE,True,15)
for y,name,body in [
    (471,'Vitor','Modernização da esteira automática: redução de <b>2 devs para 1 dev</b>; ritmo desacelerado.'),
    (495,'Gustavo','Migração da tela PTA para PCRE-JULG passa para <b>15/02/2027</b>. <b>Renegociar com a Serasa</b> a desativação da API String.'),
    (531,'Aine','Migração de bureaux desacelera; Neurotech passa integralmente de início previsto em 2026 para <b>2027</b>.'),
]:
    txt(name,30,y,65,9.5,NAVY,True,14)
    txt(body,110,y,700,9.5,maxh=26)

rect(30,560,780,1,'#CAD4E8')
txt('Fora da Entrega 1: API de status, julgamental e documentos. Entregas 2 e 3 sem data definida.',30,568,655,8.5,MUTED,maxh=12)
txt('12/11/2026',742,568,68,8.5,MUTED,maxh=12)
c.showPage(); c.save()
pdf=PdfReader(OUT)
assert len(pdf.pages)==1
content=pdf.pages[0].extract_text()
for value in ['16/11/2026','20/11/2026','24/11/2026','11/01/2027','15/02/2027','Serasa','2027']:
    assert value in content,value
assert '\ufffd' not in content
print(f'OK: one-page executivo, uma pagina, marcos conferidos: {OUT}')
