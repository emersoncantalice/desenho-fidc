"""One-page executivo V4: design remodelado, com cronograma proporcional em A4 paisagem.

Mesmo conteúdo da V2; muda a organização visual:
- cabeçalho com indicadores-chave e data-alvo em destaque;
- escopo e premissas lado a lado (o que entra / o que precisa ser verdade);
- cronograma em Gantt com escala proporcional em dias;
- trade-offs com o impacto de cada frente em destaque.
"""
from datetime import date, timedelta
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
OUT = ROOT / 'output/pdf/one-page-executivo-entrega-1-v4.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
# Versões anteriores do one-page não podem ser alteradas por este script.
previous = {p: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in OUT.parent.glob('one-page-*.pdf') if p != OUT}

# A área lógica permite controlar alinhamento sem perder texto vetorial no PDF.
W, H = 1200, 848.5
SCALE = 841.89 / W
NAVY, BLUE, INK, MUTED = '#001E62', '#0033CC', '#202B3C', '#536174'
PALE, LIGHT, LINE, GRID, ZEBRA = '#EDF2FF', '#F4F6FA', '#CCD7ED', '#E3E9F4', '#F8FAFD'
ON_NAVY, NAVY_RULE = '#CEDCFF', '#2B467F'
WARN, WARN_BG, WARN_INK = '#E08A00', '#FFF4DF', '#7A4300'

pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial', boldItalic='Arial-Bold')
c = canvas.Canvas(str(OUT), pagesize=(841.89, H * SCALE))
c.scale(SCALE, SCALE)
c.setTitle('Entrega 1 - Plano executivo visual - Versão 4')
c.setAuthor('Arquitetura de crédito')
text_boxes = []


def font(bold):
    return 'Arial-Bold' if bold else 'Arial'


def width(value, size, bold=False):
    return pdfmetrics.stringWidth(value, font(bold), size)


def box(x, y, w, h, fill=None, radius=0, stroke=None, lw=1, dash=None):
    c.saveState()
    if fill:
        c.setFillColor(HexColor(fill))
    if stroke:
        c.setStrokeColor(HexColor(stroke)); c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    c.roundRect(x, H - y - h, w, h, radius, fill=bool(fill), stroke=bool(stroke))
    c.restoreState()


def line(x1, y1, x2, y2, color=LINE, lw=1, dash=None):
    c.saveState()
    c.setStrokeColor(HexColor(color)); c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    c.line(x1, H - y1, x2, H - y2)
    c.restoreState()


def circle(x, y, r, fill):
    c.setFillColor(HexColor(fill))
    c.circle(x, H - y, r, fill=1, stroke=0)


def diamond(cx, cy, r, fill, stroke=None, lw=1.5):
    c.saveState()
    c.setFillColor(HexColor(fill))
    if stroke:
        c.setStrokeColor(HexColor(stroke)); c.setLineWidth(lw)
    p = c.beginPath()
    p.moveTo(cx, H - cy + r); p.lineTo(cx + r, H - cy)
    p.lineTo(cx, H - cy - r); p.lineTo(cx - r, H - cy); p.close()
    c.drawPath(p, fill=1, stroke=bool(stroke))
    c.restoreState()


def arrow(x1, x2, y, color=BLUE, lw=1.6, head=6):
    line(x1, y, x2 - head, y, color, lw)
    c.setFillColor(HexColor(color))
    p = c.beginPath()
    p.moveTo(x2, H - y); p.lineTo(x2 - head, H - y + head * .65)
    p.lineTo(x2 - head, H - y - head * .65); p.close()
    c.drawPath(p, fill=1, stroke=0)


def text(value, x, y, w, size=12, color=INK, bold=False, maxh=40, leading=None, align=0):
    p = Paragraph(value, ParagraphStyle('p', fontName=font(bold), fontSize=size,
                  leading=leading or size * 1.3, textColor=HexColor(color), alignment=align))
    _, h = p.wrap(w, maxh)
    assert h <= maxh + .1, (value, h, maxh)
    assert 0 <= x and x + w <= W and 0 <= y and y + h < H - 12, (value, x, y, w, h)
    text_boxes.append((x, y, w, h, value))
    p.drawOn(c, x, H - y - h)
    return h


def label(value, x, y, size=12, color=INK, bold=False, align='left'):
    """Texto de uma linha com largura exata; align define a âncora em x."""
    w = width(value, size, bold) + 1
    x = {'left': x, 'right': x - w, 'center': x - w / 2}[align]
    text(value, x, y, w, size, color, bold, maxh=size * 1.3 + .5)
    return x, w


def pill(value, x_right, y, fill, color, stroke=None, size=9.5):
    w = width(value, size, True) + 18
    box(x_right - w, y, w, 19, fill, 9.5, stroke)
    label(value, x_right - w / 2, y + 4, size, color, True, 'center')
    return w


# ── Cabeçalho ────────────────────────────────────────────────────────────────
box(0, 0, W, 86, NAVY)
label('NOVA MESA FIDC  ·  PLANO EXECUTIVO', 40, 17, 11, ON_NAVY, True)
_, w_title = label('Entrega 1', 40, 34, 31, '#FFFFFF', True)
label('Prazos, premissas e trade-offs', 40 + w_title + 18, 48, 14.5, '#FFFFFF')

for x, value, caption in [(586, '2 APIs', 'no escopo da entrega'),
                          (748, '8 semanas', '16/11/2026 a 11/01/2027')]:
    line(x - 18, 20, x - 18, 66, NAVY_RULE)
    label(value, x, 20, 22, '#FFFFFF', True)
    label(caption, x, 50, 10.5, ON_NAVY)

box(936, 14, 224, 58, BLUE, 8)
label('DATA-ALVO', 954, 22, 10, ON_NAVY, True)
label('11/01/2027', 954, 36, 27, '#FFFFFF', True)

# ── Escopo (esquerda) ────────────────────────────────────────────────────────
label('ESCOPO DA ENTREGA 1', 40, 102, 13, BLUE, True)
CARD_Y, CARD_H, CARD_W = 128, 116, 323
for i, (x, mode, title, body) in enumerate([
    (40, 'SÍNCRONA', 'API de simulação',
     'Simulação e resultado salvos na base.<br/>Resposta na mesma chamada com resultado e identificador.'),
    (407, 'ASSÍNCRONA', 'API de análise de crédito',
     'Análise automática vinculada à simulação salva.<br/>Aceite com protocolo e retorno posterior do resultado ao parceiro.'),
]):
    box(x, CARD_Y, CARD_W, CARD_H, PALE, 8)
    box(x, CARD_Y, 5, CARD_H, BLUE, 2)
    label(f'0{i + 1}', x + 20, CARD_Y + 15, 11, BLUE, True)
    pill(mode, x + CARD_W - 14, CARD_Y + 12, BLUE, '#FFFFFF')
    label(title, x + 20, CARD_Y + 36, 17, NAVY, True)
    text(body, x + 20, CARD_Y + 64, CARD_W - 38, 11.5, INK, maxh=46, leading=15)

# Correlação entre simulação e análise: o vínculo é o objetivo da entrega.
arrow(363 + 6, 407 - 6, CARD_Y + CARD_H / 2)
label('vínculo', 385, CARD_Y + CARD_H / 2 - 17, 9, BLUE, True, 'center')

OUT_Y = 258
box(40, OUT_Y, 690, 76, LIGHT, 8)
label('SEM ANÁLISE MANUAL NA ENTREGA 1', 56, OUT_Y + 12, 12.5, NAVY, True)
label('A decisão é automática. A análise julgamental mínima entra na Entrega 2.', 56, OUT_Y + 31, 11.5, MUTED)
_, w_out = label('FORA DO ESCOPO', 56, OUT_Y + 53, 9.5, MUTED, True)
chip_x = 56 + w_out + 12
for chip in ['API de status', 'Análise manual', 'Pendência documental']:
    w_chip = width(chip, 10) + 18
    box(chip_x, OUT_Y + 49, w_chip, 19, '#FFFFFF', 9.5, LINE)
    label(chip, chip_x + w_chip / 2, OUT_Y + 53, 10, INK, align='center')
    chip_x += w_chip + 8

# ── Premissas (direita) ──────────────────────────────────────────────────────
PX0 = 770
label('PREMISSAS DO PRAZO', PX0, 102, 13, BLUE, True)
y = 128
for n, (title, body, due, dated) in enumerate([
    ('Definições de negócio',
     'A REF deve contemplar as regras de simulação e análise de crédito. Não entra derivação inicialmente.',
     '20/11/2026', True),
    ('Pessoas e ambientes', 'Confirmar realocação da equipe.', 'Em aberto', False),
    ('Parceiro e implantação',
     'Certificado mTLS enviado pelo parceiro. Alinhar homologação, aceite e implantação para 11/01.',
     '12/12/2026', True),
], start=1):
    circle(PX0 + 10, y + 9, 10, BLUE)
    label(str(n), PX0 + 10, y + 3.5, 10.5, '#FFFFFF', True, 'center')
    label(title, PX0 + 30, y + 1, 12.5, NAVY, True)
    if dated:
        pill(due, 1160, y, PALE, BLUE)
    else:
        pill(due, 1160, y, '#FFFFFF', MUTED, LINE)
    y += 20 + text(body, PX0 + 30, y + 20, 1160 - PX0 - 30, 11, MUTED, maxh=29, leading=14) + 7

ATT_Y = 280
assert y <= ATT_Y + 1, y
box(PX0, ATT_Y, 390, 54, WARN_BG, 8)
box(PX0, ATT_Y, 5, 54, WARN, 2)
label('PONTO DE ATENÇÃO', PX0 + 17, ATT_Y + 11, 10, WARN_INK, True)
text('Priorizar o processo de modelagem da base de dados com o time de AD.',
     PX0 + 17, ATT_Y + 29, 368, 11, INK, maxh=15)

# ── Cronograma proporcional ──────────────────────────────────────────────────
START, END = date(2026, 11, 16), date(2027, 1, 11)
DAYS = (END - START).days + 1
X0, X1 = 300, 1155
PXD = (X1 - X0) / DAYS


def day_x(d):
    return X0 + (d - START).days * PXD


def day_center(d):
    return day_x(d) + PXD / 2


label('CRONOGRAMA', 40, 352, 13, BLUE, True)
label('16/11/2026 a 11/01/2027  ·  escala proporcional em dias', 160, 353.5, 10.5, MUTED)

# Legenda, montada da direita para a esquerda.
lx = 1160
for kind, caption in [('target', 'Data-alvo'), ('window', 'Janela proposta'), ('milestone', 'Marco definido')]:
    _, w_cap = label(caption, lx, 353, 10.5, MUTED, align='right')
    sx = lx - w_cap - 12
    if kind == 'target':
        diamond(sx, 360, 7, NAVY)
    elif kind == 'window':
        box(sx - 18, 354, 22, 12, PALE, 3, BLUE, 1, (3, 2)); sx -= 11
    else:
        diamond(sx, 360, 6, BLUE)
    lx = sx - 26

BAND_Y = 376
label('ETAPA', 48, BAND_Y + 4, 9, MUTED, True)
label('DATA', 196, BAND_Y + 4, 9, MUTED, True)
for first, last, name in [(date(2026, 11, 16), date(2026, 11, 30), 'NOVEMBRO 2026'),
                          (date(2026, 12, 1), date(2026, 12, 31), 'DEZEMBRO 2026'),
                          (date(2027, 1, 1), END, 'JANEIRO 2027')]:
    x1, x2 = day_x(first), day_x(last) + PXD
    box(x1 + 1, BAND_Y, x2 - x1 - 2, 19, LIGHT)
    label(name, (x1 + x2) / 2, BAND_Y + 4, 9.5, MUTED, True, 'center')

ROW_Y, ROW_H = 416, 24
rows = [
    ('Início preliminar', '16/11/2026', 'milestone', date(2026, 11, 16), None, 'Preparação técnica e dependências', 'right'),
    ('Contratos e REF', '20/11/2026', 'milestone', date(2026, 11, 20), None, 'Regras de simulação e análise automática', 'right'),
    ('Arquitetura definida', '24/11/2026', 'milestone', date(2026, 11, 24), None, 'Desenho da Entrega 1 e integrações', 'right'),
    ('Desenvolvimento', '25/11 a 18/12', 'window', date(2026, 11, 25), date(2026, 12, 18), 'APIs, vínculo e testes', 'inside'),
    ('Certificado mTLS', '12/12/2026', 'milestone', date(2026, 12, 12), None, 'Enviado pelo parceiro', 'right'),
    ('Integração', '21 a 30/12', 'window', date(2026, 12, 21), date(2026, 12, 30), 'Fluxo completo e falhas', 'inside'),
    ('Homologação', '04 a 08/01', 'window', date(2027, 1, 4), date(2027, 1, 8), 'Aceite e preparação', 'left'),
    ('Entrega 1', '11/01/2027', 'target', END, None, 'Disponibilização e acompanhamento', 'left'),
]
rows_end = ROW_Y + len(rows) * ROW_H
for i in range(len(rows)):
    if i % 2:
        box(40, ROW_Y + i * ROW_H, 1120, ROW_H, ZEBRA)

# Grade semanal (segundas-feiras) e rótulos das semanas.
d = START
while d <= END:
    gx = day_x(d)
    line(gx, BAND_Y + 36, gx, rows_end, GRID, .8)
    label(d.strftime('%d/%m'), gx, BAND_Y + 23, 8.5, MUTED, align='center')
    d += timedelta(days=7)
line(day_center(END), BAND_Y + 36, day_center(END), rows_end, NAVY, 1, (3, 2))

for i, (name, when, kind, first, last, detail, place) in enumerate(rows):
    ry = ROW_Y + i * ROW_H
    cy = ry + ROW_H / 2
    is_target = kind == 'target'
    label(name, 48, ry + 5, 11, NAVY, True)
    label(when, 196, ry + 5.5, 10.5, NAVY if is_target else MUTED, is_target)
    if kind == 'window':
        bx, bw = day_x(first), day_x(last) + PXD - day_x(first)
        box(bx, ry + 4, bw, ROW_H - 8, PALE, 4, BLUE, 1.1, (3.5, 2.5))
        left, right = bx, bx + bw
    else:
        cx = day_center(first)
        diamond(cx, cy, 8.5 if is_target else 6.5, NAVY if is_target else BLUE)
        left, right = cx - 10, cx + 10
    size, color = 10.5, NAVY if is_target else INK
    if place == 'inside':
        label(detail, (left + right) / 2, ry + 6, size, NAVY, align='center')
        assert width(detail, size) + 16 < right - left, detail
    elif place == 'right':
        label(detail, right + 6, ry + 6, size, color, is_target)
    else:
        label(detail, left - 6, ry + 6, size, color, is_target, 'right')

text('Janelas de desenvolvimento, integração e homologação propostas; validar capacidade e disponibilidade no fim do ano.',
     40, rows_end + 7, 1120, 10.5, MUTED, maxh=15)

# ── Trade-offs ───────────────────────────────────────────────────────────────
label('TRADE-OFFS DA REALOCAÇÃO', 40, 640, 13, BLUE, True)
label('Frentes desaceleradas para liberar capacidade para a Entrega 1', 1160, 641.5, 10.5, MUTED, align='right')
TO_Y, TO_H, TO_W = 664, 140, 357
for i, (title, metric, metric_caption, body) in enumerate([
    ('Modernização da esteira', '2 → 1 dev', 'na esteira automática',
     'Desacelera a modernização da esteira automática. Novo prazo da frente a replanejar com o resultado do orçamento de 2027.'),
    ('Desativação Serasa', '15/02/2027', 'novo prazo da migração',
     'Migração da tela PTA para PCRE-JULG estendida. Renegociar com a Serasa a desativação da API String.'),
    ('Bureau Neurotech', '1T27', 'migração integral',
     'Migração de bureaux desacelera. Neurotech, com início previsto para 2026, passa integralmente para 1T27.'),
]):
    x = 40 + i * (TO_W + 24.5)
    box(x, TO_Y, TO_W, TO_H, LIGHT, 8)
    label(title, x + 20, TO_Y + 16, 13.5, NAVY, True)
    _, w_metric = label(metric, x + 20, TO_Y + 38, 25, BLUE, True)
    label(metric_caption, x + 20 + w_metric + 10, TO_Y + 51, 10.5, MUTED)
    line(x + 20, TO_Y + 80, x + TO_W - 20, TO_Y + 80, LINE)
    text(body, x + 20, TO_Y + 90, TO_W - 40, 11, INK, maxh=43, leading=14)

# ── Rodapé ───────────────────────────────────────────────────────────────────
label('Entregas 2 e 3: datas a definir.', 40, 819, 10, MUTED)
label('V4 | 12/11/2026', 1160, 819, 10, MUTED, align='right')

# Checagem de caixas de texto para impedir sobreposições na página final.
for i, (x, y, w, h, value) in enumerate(text_boxes):
    for x2, y2, w2, h2, value2 in text_boxes[i + 1:]:
        assert not (x < x2 + w2 - .1 and x + w > x2 + .1 and y < y2 + h2 - .1 and y + h > y2 + .1), (value, value2)
c.showPage(); c.save()

reader = PdfReader(OUT)
assert len(reader.pages) == 1
content = ' '.join(reader.pages[0].extract_text().split())  # quebras de linha viram espaço
for required in ['16/11/2026', '20/11/2026', '24/11/2026', '11/01/2027', '12/12/2026', '15/02/2027',
                 'SEM ANÁLISE MANUAL NA ENTREGA 1', 'Serasa', 'Neurotech', 'API de status',
                 'Confirmar realocação da equipe.', 'time de AD', 'V4']:
    assert required in content, required
assert '\ufffd' not in content
assert all(name not in content.upper() for name in ['VITOR', 'GUSTAVO', 'AINE'])
for path, digest in previous.items():
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, path
print(f'OK: V4 em uma pagina, textos e marcos validados; {len(previous)} versoes anteriores preservadas: {OUT}')
