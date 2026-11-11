"""Consolida arquitetura, escopos, backlogs e os seis planos existentes em PDF.

Dependências: reportlab, svglib e pypdf. Instalação local em tmp/pdf-deps é aceita.
Execução: python modelos/gerar_apresentacao_pdf.py
Não recalcula nem altera estimativas dos arquivos de origem.
"""
from pathlib import Path
import sys
import json
import re
import math
import io
import xml.etree.ElementTree as ET
from collections import Counter
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg
from pypdf import PdfReader, PdfWriter

OUT = ROOT / 'output/pdf/apresentacao-consolidada-arquitetura-backlogs-cronogramas.pdf'
TEMP = ROOT / 'tmp/pdfs'
OUT.parent.mkdir(parents=True, exist_ok=True)
TEMP.mkdir(parents=True, exist_ok=True)
for name, file in [('Body', 'arial.ttf'), ('Bold', 'arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts') / file)))

NAVY = '#001E62'
BLUE = '#0033CC'
INK = '#17233B'
MUTED = '#56637A'
PALE = '#F0F4FA'
LINE = '#D8E0ED'
ROLE_COLORS = {'Backend': BLUE, 'Frontend': '#098477', 'Arquiteto': '#7152A3',
               'QA': '#B76C00', 'ITLead': '#606772'}
W, H = landscape(A3)
M = 40
CW = W - 2*M
raw_pdf = TEMP / 'apresentacao-sem-indice.pdf'
c = canvas.Canvas(str(raw_pdf), pagesize=(W, H))
c.setTitle('Arquitetura de crédito | Escopos, backlogs e cronogramas')
c.setAuthor('Planejamento de arquitetura')
pages = []
sections = []

def clean(s):
    return str(s).replace('—', '-').replace('–', '-').replace('‑', '-').replace('→', '>')

def p(text, size=11, color=INK, bold=False):
    text = escape(clean(text)).replace('\n', '<br/>')
    return Paragraph(text, ParagraphStyle('p', fontName='Bold' if bold else 'Body',
                     fontSize=size, leading=size*1.28, textColor=colors.HexColor(color)))

def paragraph(text, x, top, width, size=12, color=INK, bold=False):
    obj = p(text, size, color, bold)
    _, height = obj.wrap(width, 5000)
    obj.drawOn(c, x, top-height)
    return top-height

def begin(title, subtitle='', section=None, size=None):
    global PW, PH
    PW, PH = size or (W, H)
    c.setPageSize((PW, PH))
    pages.append(title)
    if section:
        sections.append((section, len(pages)))
    key = f'page-{len(pages)}'
    c.bookmarkPage(key)
    c.addOutlineEntry(clean(title), key, 0)
    c.setFillColor(colors.HexColor(NAVY))
    c.rect(0, PH-12, PW, 12, fill=1, stroke=0)
    paragraph('ARQUITETURA DE CRÉDITO  /  CONSOLIDADO', M, PH-30, PW-2*M, 10, BLUE, True)
    title_bottom = paragraph(title, M, PH-53, PW-2*M, 24, NAVY, True)
    if subtitle:
        paragraph(subtitle, M, title_bottom-10, PW-2*M, 11, MUTED)

def end():
    c.setStrokeColor(colors.HexColor(LINE))
    c.line(M, 37, PW-M, 37)
    c.setFillColor(colors.HexColor(MUTED))
    c.setFont('Body', 9)
    c.drawString(M, 22, 'Consolidação: 11/11/2026 | Dias úteis relativos; datas de início não definidas')
    c.drawRightString(PW-M, 22, str(len(pages)))
    c.showPage()

def table(headers, rows, widths, top=None, font=11):
    top = top or H-140
    vals = [[p(x, font, '#FFFFFF', True) for x in headers]]
    vals += [[p(x, font) for x in row] for row in rows]
    t = Table(vals, colWidths=widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(NAVY)),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor(PALE)]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 9),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 9),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor(BLUE)),
    ]))
    _, height = t.wrap(CW, PH)
    assert top-height >= 62, f'Tabela excede a página: {pages[-1]} ({height})'
    t.drawOn(c, M, top-height)
    return top-height

def bullets(items, top=None, width=CW):
    y = top or H-145
    for title, text in items:
        y = paragraph(title, M, y, width, 15, NAVY, True)-9
        y = paragraph(text, M, y, width, 13)-22
    assert y >= 55, pages[-1]

source = json.loads((ROOT/'modelos/backlog-fidc-documentos.json').read_text(encoding='utf-8'))
teams = json.loads((ROOT/'modelos/cronogramas-equipes-fidc.json').read_text(encoding='utf-8'))
md = (ROOT/'docs/cronograma-implementacao.md').read_text(encoding='utf-8')

def original(prefix):
    result = []
    for line in md.splitlines():
        if not line.startswith('| '+prefix+'-'):
            continue
        v = [s.strip().replace('\\|','|') for s in re.split(r'(?<!\\)\|',line)[1:-1]]
        ident, typ, title, team, size, deps, span, start, finish = v
        a,b = map(int,re.split('[–-]',span))
        result.append(dict(id=ident,type=typ,title=title,team=team,size=size,
                           deps=[] if deps=='—' else deps.split(', '),
                           duration=int(re.search(r'\((\d+)\)',size)[1]), start=a,end=b))
    return result

ejb, fidc, modern = original('E2'), original('F3'), original('M4')
docs = [x for x in source['items'] if x['id'].startswith('D3')]
assert [len(ejb),len(fidc),len(modern),len(docs)] == [25,30,40,16]
assert [sum(x['duration'] for x in a) for a in [ejb,fidc,modern,docs]] == [131,145,235,81]
for g in teams['groups']:
    for plan in g['plans']:
        by_id = {x['id']:x for x in plan['items']}
        assert sum(x['duration'] for x in plan['items']) == plan['delivery_effort']
        for x in plan['items']:
            assert x['end']-x['start']+1 == x['duration']
            assert all(by_id[d]['end'] < x['start'] for d in x['deps'])
        for res in {x['resource'] for x in plan['items']}:
            seq=sorted([x for x in plan['items'] if x['resource']==res],key=lambda x:x['start'])
            assert all(a['end']<b['start'] for a,b in zip(seq,seq[1:]))

# A primeira página reserva um índice preenchido depois da paginação final.
begin('Arquitetura, escopos e plano de entrega', 'Apresentação consolidada | Quatro vistas de arquitetura e seis alternativas de equipe')
paragraph('CRÉDITO / FIDC', M, H-172, CW, 40, NAVY, True)
paragraph('Do escopo ao cronograma', M, H-232, CW, 28, BLUE, True)
paragraph('Backlogs completos, dependências e planejamento da base FIDC e da extensão documental com 2, 3 e 4 desenvolvedores.', M, H-290, 860, 18)
paragraph('ÍNDICE', M, H-402, CW, 14, NAVY, True)
end()

begin('Comparativo dos escopos', 'Os modelos são alternativas de arquitetura; documentos ampliam somente o escopo FIDC.', 'Escopos e premissas')
table(['Dimensão','AS IS','Mantendo EJB','Base FIDC','Supermodernizado'],[
    ['Objeto','Proposta de crédito','Proposta interna ou externa','Solicitação de análise FIDC, sem proposta','Proposta externa + análise de crédito'],
    ['Captura e dados','EJB / Sybase','EJB / Sybase, com origem e novos status','Esteira no GCP / MySQL cloud','Captura separada; análise no GCP / MySQL cloud'],
    ['Análise manual','PTA + PowerApps','PTA + PowerApps adaptados','PCRE-JULG | Argos; fila única FIDC','Nova mesa; gestão de filas'],
    ['Integração','PDEC e MQ no fluxo legado','Retorno externo a definir; bloqueio na MQ','API + callback com mTLS; Kafka interno','Proposta persistida e conclusão via Kafka'],
    ['Limite do fluxo','Aprovadas seguem para formalização e pagamento','Origem externa bloqueada para formalização e pagamento internos','Encerra na análise; resultado ao parceiro','Conclusão atualiza proposta externa; ciclo de vida na captura'],
    ['Papel no plano','Referência do estado atual','Transição; não é a arquitetura alvo','Entrega específica FIDC','Arquitetura alvo moderna'],
], [105]+[(CW-105)/4]*4, font=11)
end()

begin('Premissas de leitura e de capacidade', 'A soma do esforço não equivale ao prazo de calendário.')
bullets([
 ('Calendário relativo','Dia 1 = início de cada cenário. Semana = 5 dias úteis; mês = 20 dias úteis. Feriados, férias, onboarding e esperas externas não foram incorporados.'),
 ('Dois modelos de planejamento','EJB e Supermodernizado mantêm os cronogramas originais por frentes de trabalho. A base FIDC também tem referência histórica por frentes; para comparar 2, 3 e 4 devs, usar os seis planos por perfil da parte final.'),
 ('Composição da equipe','2 devs = 1 Backend + 1 Frontend; 3 devs = 2 Backend + 1 Frontend; 4 devs = 3 Backend + 1 Frontend. Em todos os casos, há 1 Arquiteto, 1 QA e 1 ITLead adicionais.'),
 ('Alocação e esforço','Arquiteto atua nos 10 dias do desenho; QA nas janelas indicadas; ITLead tem dedicação estimada de 20% ao longo do cenário. Gestão é esforço adicional e não integra os 145 du da base ou os 81 du documentais.'),
 ('Execução e dependências','Uma atividade por profissional de cada vez. Desenvolvimento inclui revisão e testes da entrega. APIs precedem as telas. Os sufixos B, F e Q dividem atividades originais sem duplicar seu esforço.'),
 ('Extensão documental','Os cronogramas documentais começam no seu próprio dia 1 e pressupõem a base FIDC pronta. Não representam execução simultânea pelas mesmas pessoas. O tempo do cliente para enviar documentos é operacional e não integra o desenvolvimento.'),
], top=H-140)
end()

architecture = [
 ('Vista 1 | AS IS','as-is.svg','Estado atual de referência. Não há backlog de implementação para esta vista.'),
 ('Vista 2 | Proposta mantendo EJB','proposta-com-ejb.svg','Alternativa de transição. O fluxo externo deve bloquear formalização e pagamento internos.'),
 ('Vista 3 | Mesa simplificada FIDC','proposta-nova-mesa.svg','Solicitação de análise, fila única na PCRE-JULG | Argos e retorno ao parceiro. Sem proposta.'),
 ('Vista 4 | Supermodernizado','proposta-modernizada-gcp.svg','Captura separada do domínio de crédito; entrada e conclusão por eventos Kafka.'),
]
def drawing_with_arrows(path):
    # svglib não desenha marker-end. Expande o marcador em um polígono vetorial
    # equivalente, apenas na cópia em memória usada para exportar o PDF.
    root = ET.parse(path).getroot()
    ns = '{http://www.w3.org/2000/svg}'
    for parent in list(root.iter()):
        for elem in list(parent):
            if elem.tag != ns+'polyline' or 'marker-end' not in elem.attrib:
                continue
            nums = list(map(float,re.findall(r'[-+]?(?:\d*\.)?\d+(?:[eE][-+]?\d+)?',elem.attrib['points'])))
            points = list(zip(nums[0::2],nums[1::2]))
            x,y = points[-1]
            px,py = next(pt for pt in reversed(points[:-1]) if pt != (x,y))
            length = math.hypot(x-px,y-py)
            ux,uy = (x-px)/length,(y-py)/length
            # Marcador original: viewBox 0 0 10 10, largura 6 e refX 9.
            unit = 0.6*float(elem.attrib.get('stroke-width','1'))
            coords = [(x-9*unit*ux+5*unit*uy,y-9*unit*uy-5*unit*ux),
                      (x+unit*ux,y+unit*uy),
                      (x-9*unit*ux-5*unit*uy,y-9*unit*uy+5*unit*ux)]
            arrow = ET.Element(ns+'polygon', {'points':' '.join(f'{a},{b}' for a,b in coords),
                                             'fill':elem.attrib.get('stroke','#52606d')})
            parent.insert(list(parent).index(elem)+1,arrow)
            del elem.attrib['marker-end']
    return svg2rlg(io.BytesIO(ET.tostring(root)))

for i,(title,file,note) in enumerate(architecture):
    drawing=drawing_with_arrows(ROOT/'diagramas'/file)
    assert drawing is not None
    # Folha ajustada à vista: mantém o desenho vetorial e a tipografia de origem.
    sw,sh=drawing.width,drawing.height
    begin(title,note, 'Modelos de arquitetura' if i==0 else None, (max(W,sw+80),sh+190))
    renderPDF.draw(drawing,c,(PW-sw)/2,55)
    end()

def balanced_chunks(items, limit):
    count = math.ceil(len(items)/limit)
    small, extra = divmod(len(items), count)
    result, start = [], 0
    for i in range(count):
        end = start + small + (i < extra)
        result.append(items[start:end])
        start = end
    return result

def backlog(name, items, section=None, with_dates=True):
    chunks=balanced_chunks(items,12)
    effort=sum(x['duration'] for x in items)
    counts=Counter(x['type'] for x in items)
    for i,chunk in enumerate(chunks):
        begin(f'Backlog | {name} | {i+1}/{len(chunks)}',
              f'{len(items)} itens: {counts["Story"]} stories, {counts["Spike"]} spikes e {counts["Task"]} tasks | Esforço: {effort} du',section if i==0 else None)
        rows=[]
        for x in chunk:
            deps=', '.join(x['deps']) or '-'
            prereq=', '.join(x.get('prerequisites',[])) or '-'
            rows.append([x['id'],x['type'],x['title'],x['team'],x['size'],deps,
                         f'{x["start"]}-{x["end"]}' if with_dates else prereq])
        table(['ID','Tipo','Entrega / atividade','Frente','Tamanho (du)','Dependências',
               'Período (du)' if with_dates else 'Base exigida'],rows,
              [65,56,CW-65-56-58-100-145-120,58,100,145,120],font=11)
        paragraph('Datas por frentes de trabalho, conforme cronograma original.' if with_dates else
                  'Datas e responsáveis variam por equipe: consulte os três cronogramas documentais a seguir.',M,70,CW,10,MUTED)
        end()

def gantt(name,items,finish,section=None,plan=None):
    # Cabeçalho e eixo comuns em todas as páginas de um mesmo cenário.
    detail=bool(plan)
    chunks=balanced_chunks(items,13)
    for n,chunk in enumerate(chunks):
        sub=(f'{plan["developers"]} devs: {plan["backend"]} Backend + 1 Frontend | Apoio: Arquiteto + QA + ITLead (20%) | '
             f'Prazo: {finish} du ({plan["milestone"]}) | Entregas: {plan["delivery_effort"]} du; gestão: {str(plan["lead_effort"]).replace(".",",")} du') if detail else f'Planejamento original por frentes | Conclusão do escopo: dia útil {finish}'
        begin(f'Cronograma | {name} | {n+1}/{len(chunks)}',sub,section if n==0 else None)
        # Colunas: identificação, título, responsável, dependências, janela e Gantt.
        widths=[62,275,85,135,62]
        gx=M+sum(widths)
        gw=PW-M-gx
        weeks=math.ceil(finish/5)
        unit=gw/(weeks*5)
        top=PH-168
        x=M
        for label,width in zip(['ID','Atividade','Perfil / frente','Depende de / base','DU início-fim'],widths):
            paragraph(label,x+3,top+30,width-6,10,MUTED,True)
            x+=width
        for w in range(weeks):
            x=gx+w*5*unit
            if w%4==0:
                paragraph(f'M{w//4+1}',x,top+46,60,10,BLUE,True)
            paragraph(f'S{w%4+1}',x+1,top+27,5*unit,8,MUTED)
        y=top
        for idx,item in enumerate(chunk):
            dep=', '.join(item['deps']) or '-'
            prereq=item.get('prerequisites',[])
            if prereq: dep+='\nBase: '+', '.join(prereq)
            texts=[item['id'],item['title'],item.get('resource',item.get('team','')),dep,f'{item["start"]}-{item["end"]}']
            heights=[]
            for txt,width in zip(texts,widths):
                heights.append(p(txt,10).wrap(width-8,1000)[1])
            rh=max(34,max(heights)+14)
            assert y-rh>=100,f'Gantt excede a página: {pages[-1]}'
            c.setFillColor(colors.HexColor(PALE if idx%2==0 else '#FFFFFF'))
            c.rect(M,y-rh,CW,rh,fill=1,stroke=0)
            x=M
            for col,(txt,width) in enumerate(zip(texts,widths)):
                paragraph(txt,x+4,y-7,width-8,10,NAVY if col==0 else INK,col==0)
                x+=width
            for w in range(weeks+1):
                c.setStrokeColor(colors.HexColor(LINE))
                c.setLineWidth(0.6 if w%4 else 1.1)
                c.line(gx+w*5*unit,y,gx+w*5*unit,y-rh)
            color=ROLE_COLORS.get(item.get('role'),BLUE)
            c.setFillColor(colors.HexColor(color))
            c.roundRect(gx+(item['start']-1)*unit,y-rh/2-7,item['duration']*unit,14,2,fill=1,stroke=0)
            y-=rh
        if detail:
            if n==len(chunks)-1:
                y-=15
                paragraph('ITLead: gestão transversal do dia 1 ao '+str(finish)+' (20% de dedicação).',M,y,gx-M-8,10,MUTED)
                c.setFillColor(colors.HexColor(ROLE_COLORS['ITLead']))
                c.rect(gx,y-13,finish*unit,9,fill=1,stroke=0)
            x=M
            for role,color in ROLE_COLORS.items():
                c.setFillColor(colors.HexColor(color)); c.rect(x,72,10,10,fill=1,stroke=0)
                paragraph(role,x+16,83,100,10,MUTED); x+=135
        paragraph('Cada barra usa dias úteis; semanas e meses são relativos. IDs B / F / Q remetem ao item original do backlog.' if detail else
                  'As frentes trabalham em paralelo. Não interpretar a quantidade de frentes como quantidade de desenvolvedores.',M,59,CW,9,MUTED)
        end()

begin('Prazos originais por frentes', 'Referência das alternativas de arquitetura; a comparação FIDC por equipe aparece na parte seguinte.', 'Backlogs e cronogramas originais')
table(['Alternativa','Itens','Esforço (du)','Frentes','Go-live','Encerramento'],[
    ['EJB','25','131','4','49 du / M3·S2','49 du'],
    ['Base FIDC','30','145','4','63 du / M4·S1','63 du'],
    ['Supermodernizado','40','235','6','69 du / M4·S2','79 du, após desativação do legado'],
],[270,70,140,100,230,CW-810],font=13)
bullets([
 ('Esforço preservado','Os backlogs a seguir reproduzem todos os itens originais, suas durações, frentes e dependências. Não houve reestimativa nesta consolidação.'),
 ('Marcos de arquitetura','O desenho da solução ocupa os dias 1 a 10, em paralelo aos spikes. Nenhuma story ou task de implementação começa antes de sua conclusão. Dependências adicionais podem alongar esse início.'),
 ('AS IS','Representa o estado atual. Não possui backlog nem cronograma de implementação.'),
],top=H-380)
end()
for name,items in [('EJB',ejb),('Base FIDC - referência por frentes',fidc),('Supermodernizado',modern)]:
    backlog(name,items)
    gantt(name,items,max(x['end'] for x in items))

begin('Comparativo das equipes | 2, 3 e 4 devs','Seis cenários existentes, preservados conforme o planejamento de 11/11/2026.','Comparativo de equipes')
rows=[]
for g in teams['groups']:
    for plan in g['plans']:
        rows.append([g['name'],str(plan['developers']),f'{plan["backend"]} BE + 1 FE',str(plan['people']),
                     str(plan['finish']),plan['milestone'],str(plan['delivery_effort']),str(plan['lead_effort']).replace('.',',')])
table(['Escopo','Devs','Composição','Pessoas¹','Prazo (du)','Marco','Entregas (du)','Gestão (du)'],rows,
      [230,65,145,100,115,130,130,CW-915],font=12)
bullets([
 ('¹ Pessoas envolvidas','Inclui devs, Arquiteto, QA e ITLead. Isso não representa dedicação integral de todos durante todo o prazo. BE = Backend; FE = Frontend.'),
 ('Ganho de prazo','Na base, 2 > 3 devs reduz o plano de 111 para 64 du; 3 > 4 reduz para 63 du. Em documentos, os planos são 61, 48 e 48 du. As dependências e os recursos especializados limitam a redução.'),
 ('Execução sequencial, se adotada','Com a mesma composição em ambas as etapas, a soma base + documentos é 172 du (2 devs), 112 du (3 devs) ou 111 du (4 devs). É uma soma derivada dos planos, sem intervalo ou sobreposição entre as etapas.'),
],top=H-470)
end()

begin('Base FIDC | Escopo e carga por perfil','Solicitação de análise FIDC, sem proposta, formalização ou pagamento.','Base FIDC com 2, 3 e 4 devs')
table(['Perfil','Esforço das entregas','Aplicação no plano'],[
 ['Backend','108 du','APIs, estados, PDEC, Kafka, callback, plataforma e implantação'],
 ['Frontend','15 du','Extensão da PCRE-JULG | Argos, fila única e telas da mesa'],
 ['Arquiteto','10 du','Desenho da solução, contratos e responsabilidades'],
 ['QA','12 du','Testes transversais e homologação'],
 ['Total','145 du','Mesmo esforço de entrega nos três tamanhos de equipe'],
],[180,200,CW-380],font=13)
bullets([
 ('Integração com o parceiro','A entrada devolve protocolo de aceite. Após a análise, uma chamada posterior envia a conclusão ao parceiro. As duas chamadas exigem mTLS. Falha de callback não reinicia nem altera a decisão.'),
 ('Divisão dos itens','34 atividades alocadas representam os 30 itens originais. IDs terminados em B, F ou Q indicam a divisão por perfil, preservando o total de esforço.'),
],top=H-465)
end()
for plan in teams['groups'][0]['plans']:
    gantt(f'Base FIDC / {plan["developers"]} devs',plan['items'],plan['finish'],plan=plan)

begin('Pendência documental | Escopo e sequência','Extensão da base FIDC; os três cronogramas começam após a base estar disponível.','Backlog e fluxo documental')
bullets([
 ('1. Pendenciar e notificar','O analista registra motivo, documentos exigidos e prazo. A esteira registra a pendência; o parceiro comunica o cliente.'),
 ('2. Autorizar e receber','O cliente usa canal autenticado para obter autorização temporária e enviar documentos ao bucket privado. Credenciais do bucket não são entregues ao cliente.'),
 ('3. Validar e consolidar','Arquivos inválidos ficam isolados. Envio parcial ou rejeitado mantém a pendência. A consolidação exige todos os documentos obrigatórios válidos e publicação confiável, com idempotência.'),
 ('4. Retomar e auditar','A análise é retomada uma única vez por versão ativa da pendência. Acesso aos documentos é autorizado e auditado. Eventos antigos ou duplicados não reabrem análises encerradas.'),
 ('Limites e decisões','Upload não aprova a solicitação nem libera pagamento. Expiração, retenção, tipos de arquivo e nova execução da PDEC dependem dos spikes. A proposta comercial permanece com o parceiro.'),
 ('Carga da extensão','81 du de entregas: Backend 54, Frontend 12, Arquiteto 10 e QA 5. São 16 itens originais e 18 atividades após a divisão por perfil. A gestão é adicional.'),
])
end()
backlog('Pendência documental',docs,with_dates=False)
for i,plan in enumerate(teams['groups'][1]['plans']):
    gantt(f'Pendência documental / {plan["developers"]} devs',plan['items'],plan['finish'],
          section='Documentos com 2, 3 e 4 devs' if i==0 else None,plan=plan)

begin('Dependências e decisões para execução','Premissas que podem deslocar os marcos apresentados.','Riscos, decisões e fontes')
table(['Tema','Impacto / condição'],[
 ['Legado EJB / MQ','Mapeamento pode revelar novos pontos de bloqueio; preservar fluxo interno e validar reprocessamento.'],
 ['Contratos e infraestrutura','Runtime, região, Kafka, MySQL, APIs e eventos precisam de decisão ao fim dos spikes para liberar atividades dependentes.'],
 ['Integração com parceiros','Disponibilidade do canal, parceiro e PCRE-JULG | Argos afeta testes ponta a ponta e homologação.'],
 ['mTLS e segurança','Definir autoridade certificadora, emissão, rotação, revogação e associação do certificado ao parceiro.'],
 ['Documentos','Resolver exigências, prazos, retenção, validação, expiração e reanálise. Cumprir os pré-requisitos F3 listados nas atividades D3.'],
 ['Desativação do legado','Na vista 4, migração dos consumidores do GCRE pode adiar a desativação após o go-live.'],
 ['Capacidade','Provisionamento está atribuído ao Backend nos seis planos por perfil; espera por plataforma e parceiro não foi estimada.'],
],[245,CW-245],font=12)
end()

begin('Fontes e rastreabilidade','Conteúdo consolidado dos arquivos locais; cronogramas não foram recalculados.')
table(['Fonte no repositório','Uso na apresentação'],[
 ['docs/analise-externa-de-propostas.md','Descrição das quatro vistas, escopos, integrações e decisões.'],
 ['docs/cronograma-implementacao.md','95 itens originais: EJB (25), FIDC (30) e Supermodernizado (40); prazos por frentes.'],
 ['modelos/backlog-fidc-documentos.json','Backlog FIDC e os 16 itens adicionais de pendência documental, com seus pré-requisitos da base.'],
 ['modelos/cronogramas-equipes-fidc.json','Seis planos por perfil: responsáveis, dependências, esforço, início e fim de cada atividade.'],
 ['docs/cronograma-fidc-documentos.md','Premissas de capacidade, alocação dos perfis e interpretação dos seis cenários.'],
 ['diagramas/as-is.svg; proposta-com-ejb.svg; proposta-nova-mesa.svg; proposta-modernizada-gcp.svg','Vistas vetoriais incluídas integralmente. Folhas ajustadas ao desenho para preservar o detalhamento.'],
],[440,CW-440],font=12)
paragraph('Atualização das fontes: planejamento geral em 10/11/2026; equipes e documentos em 11/11/2026. Diagramas e conteúdo arquitetural conforme versão disponível no repositório.',M,180,CW,12,MUTED)
paragraph('Unidades: du = dias úteis; M = mês relativo; S = semana dentro do mês. Tamanho simples = 3 du, médio = 5 du e complexo = 10 du; arquitetura = 10 du e provisionamento = 4 du por item.',M,125,CW,12,MUTED)
end()
c.save()

# Índice com números efetivos e links internos; mantém os bookmarks de cada folha.
overlay_path=TEMP/'indice.pdf'
o=canvas.Canvas(str(overlay_path),pagesize=(W,H))
y=H-438
for label,num in sections:
    o.setFont('Body',12); o.setFillColor(colors.HexColor(INK))
    o.drawString(M,y,label)
    o.setFont('Bold',12); o.setFillColor(colors.HexColor(BLUE))
    o.drawRightString(W-M,y,str(num)); y-=26
assert y>50
o.showPage(); o.save()
reader=PdfReader(str(raw_pdf))
writer=PdfWriter()
writer.clone_document_from_reader(reader)
writer.pages[0].merge_page(PdfReader(str(overlay_path)).pages[0])
from pypdf.annotations import Link
y=H-438
for label,num in sections:
    writer.add_annotation(page_number=0,annotation=Link(rect=(M,y-4,W-M,y+17),target_page_index=num-1))
    y-=26
with OUT.open('wb') as f: writer.write(f)
check=PdfReader(str(OUT))
texts=[page.extract_text() for page in check.pages]
all_text='\n'.join(texts)
for item in ejb+fidc+modern+docs:
    assert item['id'] in all_text,item['id']
for g in teams['groups']:
    for plan in g['plans']:
        matching=[t for t in texts if f'{g["name"]} / {plan["developers"]} devs' in t]
        assert matching,(g['name'],plan['developers'])
        joined='\n'.join(matching)
        for item in plan['items']:
            assert item['id'] in joined,item['id']
assert len(check.pages)==len(pages)
(TEMP/'manifesto.json').write_text(json.dumps(dict(pdf=str(OUT),pages=pages,sections=sections,
    checks={'original_backlog_items':111,'team_scenarios':6,'team_activities':156,
            'effort_dependencies_resource_conflicts':'validated'}),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pdf':str(OUT),'pages':len(pages),'sections':sections},ensure_ascii=False))
