"""One-page executivo V3 com composição editorial e cronograma linear."""
from pathlib import Path
import hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf/one-page-executivo-entrega-1-v3.pdf'
V2=ROOT/'output/pdf/one-page-executivo-entrega-1-v2.pdf'
v2_hash=hashlib.sha256(V2.read_bytes()).hexdigest()
W,H=1200,848.5
SCALE=841.89/W
NAVY='#001E62';BLUE='#0033CC';INK='#202B3C';MUTED='#546174'
PALE='#EDF2FF';LIGHT='#F4F6FA';LINE='#CFD8E7';WHITE='#FFFFFF'
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
OUT.parent.mkdir(parents=True,exist_ok=True)
c=canvas.Canvas(str(OUT),pagesize=(841.89,H*SCALE))
c.scale(SCALE,SCALE)
c.setTitle('Entrega 1 - Plano executivo - Versão 3')
c.setAuthor('Arquitetura de crédito')
text_boxes=[]


def rect(x,y,w,h,fill,r=0):
    c.setFillColor(HexColor(fill));c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=0)


def line(x1,y1,x2,y2,color=LINE,width=1):
    c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.line(x1,H-y1,x2,H-y2)


def text(value,x,y,w,size=13.3,color=INK,bold=False,maxh=55,leading=None,align=0):
    p=Paragraph(value,ParagraphStyle('p',fontName='Arial-Bold' if bold else 'Arial',
        fontSize=size,leading=leading or size*1.3,textColor=HexColor(color),alignment=align))
    _,h=p.wrap(w,maxh)
    assert h<=maxh+.1,(value,h,maxh)
    assert x>=0 and x+w<=W and y>=0 and y+h<H-12,(value,x,y,w,h)
    text_boxes.append((x,y,w,h,value));p.drawOn(c,x,H-y-h)


def diamond(cx,y,r,fill):
    c.setFillColor(HexColor(fill))
    p=c.beginPath();p.moveTo(cx,H-y+r);p.lineTo(cx+r,H-y)
    p.lineTo(cx,H-y-r);p.lineTo(cx-r,H-y);p.close()
    c.drawPath(p,fill=1,stroke=0)


def arrow_band(x,y,w,h,fill):
    c.setFillColor(HexColor(fill))
    p=c.beginPath();p.moveTo(x,H-y);p.lineTo(x+w-12,H-y)
    p.lineTo(x+w,H-y-h/2);p.lineTo(x+w-12,H-y-h)
    p.lineTo(x,H-y-h);p.close();c.drawPath(p,fill=1,stroke=0)


# Faixa lateral: compromisso, entregáveis e fronteira de escopo.
rect(0,0,288,H,NAVY)
text('NOVA MESA FIDC',28,30,232,11.5,'#CCD9FF',True,16)
text('Entrega 1',28,61,232,34,WHITE,True,46)
rect(28,118,48,4,'#7094FF')
text('DATA-ALVO',28,140,232,11.5,'#CCD9FF',True,16)
text('11 JAN',24,162,240,48,WHITE,True,64)
text('2027',28,225,232,27,'#CCD9FF',True,37)

text('O QUE SERÁ ENTREGUE',28,291,232,11.5,'#CCD9FF',True,17)
text('API de simulação<br/>síncrona',28,321,232,21,WHITE,True,55)
text('Dados da simulação e resultado salvos na base. Resposta na mesma chamada com resultado e identificador.',28,384,232,13.3,WHITE,maxh=78)
line(28,469,260,469,'#34538A',1)
text('API de análise de<br/>crédito assíncrona',28,490,232,21,WHITE,True,55)
text('Análise automática vinculada à simulação salva. Aceite com protocolo e retorno posterior do resultado ao parceiro.',28,552,232,13.3,WHITE,maxh=89)

rect(20,657,248,83,'#173777',5)
text('SEM ANÁLISE MANUAL',32,669,224,13,WHITE,True,19)
text('Não entra derivação inicialmente.',32,697,224,13.3,'#E0E8FF',maxh=36)
text('<b>Entrega 2:</b> API de status e análise julgamental mínima.<br/><b>Entrega 3:</b> pendências e arquivos.<br/>E2 e E3: datas a definir.',28,765,232,11.6,'#CCD9FF',maxh=66)

# Área editorial principal.
text('PLANO EXECUTIVO',324,29,600,11.5,MUTED,True,17)
text('V3',1114,29,50,11.5,BLUE,True,17,align=2)
text('Cronograma e condições de entrega',324,54,840,26,NAVY,True,36)
text('MARCOS DEFINIDOS',324,108,840,12,BLUE,True,17)

# Linha ordenada de marcos, incluindo a dependência do parceiro.
centers=[402,572,742,912,1082]
rect(1001,138,162,116,PALE,6)
line(centers[0],181,centers[-1],181,LINE,3)
milestones=[
    ('16/11/2026','Início<br/>preliminar'),
    ('20/11/2026','Contratos<br/>e REF'),
    ('24/11/2026','Arquitetura da<br/>Entrega 1'),
    ('12/12/2026','Envio do certificado<br/>mTLS pelo parceiro'),
    ('11/01/2027','Disponibilização<br/>da Entrega 1'),
]
for cx,(date,label) in zip(centers,milestones):
    text(date,cx-79,146,158,17.2,BLUE,True,24,align=1)
    diamond(cx,181,8,BLUE)
    text(label,cx-79,202,158,13.3,NAVY,True,40,align=1)

text('JANELAS PROPOSTAS',324,275,840,12,BLUE,True,17)
for x,period,title,desc in [
    (324,'25/11 A 18/12/2026','Desenvolvimento','Duas APIs, correlação e testes.'),
    (608,'21 A 30/12/2026','Integração','Fluxo completo e testes de falhas.'),
    (892,'04 A 08/01/2027','Homologação','Aceite e preparação da implantação.'),
]:
    arrow_band(x,302,272,80,LIGHT)
    text(period,x+14,313,244,11.2,MUTED,True,16)
    text(title,x+14,334,244,16,NAVY,True,23)
    text(desc,x+14,359,244,11.7,MUTED,maxh=18)
text('Períodos sujeitos à validação da capacidade e da disponibilidade no fim do ano.',324,393,840,11.5,MUTED,maxh=17)

text('PREMISSAS DE EXECUÇÃO',324,433,840,12,BLUE,True,17)
for x,title,body in [
    (324,'Definições de negócio','A REF deve contemplar as regras de simulação e análise de crédito. Não entra derivação inicialmente.'),
    (608,'Pessoas e ambientes','Confirmar realocação da equipe.'),
    (892,'Parceiro e implantação','Certificado mTLS enviado até <b>12/12/2026</b>. Alinhar homologação, aceite e implantação para 11/01.'),
]:
    line(x,463,x+272,463,LINE,1)
    text(title,x,476,272,14,NAVY,True,20)
    text(body,x,506,272,13.3,MUTED,maxh=70)

rect(324,594,840,49,PALE,5)
rect(324,594,4,49,BLUE)
text('PONTO DE ATENÇÃO',340,610,173,11.5,BLUE,True,17)
text('Priorizar o processo de modelagem da base de dados com o time de AD.',526,603,620,13.3,NAVY,maxh=35)

text('TRADE-OFFS DA REALOCAÇÃO',324,668,840,12,BLUE,True,17)
tradeoffs=[
    (698, 'Modernização da esteira',
     'Redução de <b>2 devs para 1 dev</b> desacelera a modernização da esteira automática. Novo prazo da frente a replanejar com resultado do orçamento de 2027.'),
    (743, 'Desativação Serasa',
     'Migração da tela PTA para PCRE-JULG passa para <b>15/02/2027</b>. Renegociar com a Serasa a desativação da API String.'),
    (788, 'Bureau Neurotech',
     'Migração de bureaux desacelera. Neurotech, com início previsto para 2026, passa integralmente para <b>1T27</b>.'),
]
for y,title,body in tradeoffs:
    line(324,y-9,1164,y-9,LINE,1)
    text(title,324,y,237,15,NAVY,True,40)
    text(body,585,y,579,12.1,INK,maxh=34,leading=14.8)

text('12/11/2026',1064,824,100,9.2,MUTED,maxh=13,align=2)

# A validação geométrica complementa a inspeção visual do PDF renderizado.
for i,(x,y,w,h,t) in enumerate(text_boxes):
    for x2,y2,w2,h2,t2 in text_boxes[i+1:]:
        assert not (x<x2+w2-.1 and x+w>x2+.1 and y<y2+h2-.1 and y+h>y2+.1),(t,t2)
c.showPage();c.save()
pdf=PdfReader(OUT)
assert len(pdf.pages)==1
content=pdf.pages[0].extract_text()
normalized=' '.join(content.split())
for token in ['16/11/2026','20/11/2026','24/11/2026','12/12/2026','11/01/2027',
              '15/02/2027','1T27','SEM ANÁLISE MANUAL','Confirmar realocação da equipe.',
              'time de AD','orçamento de 2027','mTLS','Dados da simulação e resultado salvos na base.',
              'Não entra derivação inicialmente.']:
    assert token in normalized,token
assert '\ufffd' not in content
assert not any(name in content.upper() for name in ['VITOR','GUSTAVO','AINE'])
assert hashlib.sha256(V2.read_bytes()).hexdigest()==v2_hash
print(f'OK: V3, uma pagina, conteudo e layout conferidos; V2 preservada: {OUT}')
