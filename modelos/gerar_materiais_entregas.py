"""Consolida o backlog das três entregas e gera o one-page da Entrega 1."""
from pathlib import Path
import json
import sys
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/one-page-entrega-1-nova-mesa.pdf'
EPIC = 'EP-01 - Jornada de simulação e análise de crédito FIDC'
FEATURES = [
    ('FT-01', 1, 'API de simulação', 'Simulação síncrona salva na base; resultado e identificador retornados na mesma chamada.'),
    ('FT-02', 1, 'API de análise de crédito assíncrona', 'Aceite com protocolo, decisão automática, correlação com simulação e retorno posterior ao parceiro.'),
    ('FT-03', 2, 'API de status', 'Consulta autorizada do andamento e resultado da análise, com correlação.'),
    ('FT-04', 2, 'Análise julgamental mínima', 'Derivação, fila única FIDC na PCRE-JULG, consulta, decisão manual e consolidação do resultado.'),
    ('FT-05', 3, 'Pendência documental e troca de arquivos', 'Pendenciar, notificar, enviar, validar, corrigir e consultar arquivos; concluir a pendência e retomar a análise.'),
]
SOURCE = json.loads((ROOT / 'modelos/backlog-fidc-documentos.json').read_text(encoding='utf-8'))
ORIGINAL = {x['id']: x for x in SOURCE['items']}
items = []


def add(ident, delivery, feature, title, deps, acceptance, origin='', kind='Story', start=None, deadline=None):
    items.append(dict(id=ident, delivery=delivery, feature=feature, type=kind, title=title,
                      deps=deps.split(', ') if deps else [], acceptance=acceptance,
                      origin=origin, owner='', status='A planejar', effort=None,
                      start=start, deadline=deadline))


def f(num, delivery, feature, title, deps, acceptance):
    ident=f'F3-{num:02}'
    add(ident, delivery, feature, title, deps, acceptance, ident, ORIGINAL[ident]['type'],
        deadline='2026-11-20' if num==2 else '2026-11-24' if num==6 else None)


shared = 'FT-01 + FT-02'
add('PRE-01',1,shared,'Iniciar trabalhos preliminares em 16/11/2026','',
    'Levantar dependências, acessos e capacidade; iniciar preparação técnica em paralelo aos contratos e à REF.',
    'E1-00', 'Task', start='2026-11-16')
add('REF-01',1,shared,'Definir a REF de simulação e análise automática','PRE-01',
    'Regras e cenários de aceite definidos, incluindo tratamento de casos sem decisão automática e sem mesa disponível.',
    'E1-02','Spike',deadline='2026-11-20')
f(1,1,shared,'Definir runtime, região no GCP e produto MySQL','PRE-01','Ambientes e produtos definidos para o recorte das APIs.')
f(2,1,shared,'Definir contratos das APIs, correlação e retorno assíncrono','PRE-01','Contratos acordados até 20/11: payloads, erros, aceite, resultado, identificadores, validade e cardinalidade da correlação.')
f(3,1,shared,'Definir mTLS e identidade do parceiro','F3-02','Emissão, rotação, revogação e vínculo dos certificados ao parceiro definidos.')
f(5,1,'FT-02','Definir timeout, retentativas e recuperação do retorno','F3-02','Mecanismo de retorno e política de falhas acordados; callback com mTLS é a proposta a confirmar.')
f(6,1,shared,'Desenhar arquitetura, integrações, dados e execução assíncrona','F3-01, F3-02, F3-03, F3-05, REF-01','Desenho do recorte das APIs concluído; mecanismo assíncrono dimensionado sem dependência da mesa.')
f(7,1,shared,'Provisionar ambientes no GCP e CI/CD','F3-06','Ambientes, acessos e pipeline disponíveis para desenvolver e homologar.')
f(8,1,shared,'Provisionar MySQL, rede, usuários e backup','F3-06','Persistência acessível com permissões e recuperação definidas.')
f(10,1,shared,'Provisionar mTLS e certificados de homologação','F3-03, F3-07','Entrada e retorno externo com segurança disponível em homologação.')
add('SIM-01',1,'FT-01','Implementar a API de simulação síncrona','F3-02, REF-01, F3-07, F3-08',
    'Validar entrada, executar regras, salvar dados e resultado da simulação na base e retornar resultado e idSimulacao na mesma chamada; erros e timeout conforme contrato.', 'E1-04')
f(16,1,'FT-02','Receber e validar a solicitação de análise assíncrona','F3-02, F3-07','Aceitar requisição sem aguardar a decisão de crédito; validar payload conforme contrato.')
f(17,1,'FT-02','Persistir solicitação e devolver protocolo único de aceite','F3-08, F3-16','Aceite só após persistência; identificador de análise retornado ao parceiro.')
add('COR-01',1,'FT-02','Vincular análise à simulação de origem','F3-02, F3-17',
    'Consultar a simulação salva na base e vincular a análise a ela por idSimulacao; persistir idAnalise, validar titularidade, validade e compatibilidade e manter vínculo no resultado.', 'E1-05')
f(18,1,'FT-02','Controlar os estados internos da análise automática','F3-17','Transições auditáveis e tratamento de falhas conforme REF, sem API externa de status ou derivação manual.')
f(19,1,'FT-02','Solicitar decisão à PDEC e persistir o resultado automático','F3-18, REF-01, COR-01','Processar após o aceite e registrar decisão ou tratamento de ausência de decisão conforme REF.')
f(21,1,'FT-02','Garantir idempotência da solicitação de análise','F3-17','Reenvio com a mesma chave preserva protocolo e correlação; conflitos tratados conforme contrato.')
f(27,1,'FT-02','Proteger decisão automática contra resultados duplicados ou tardios','F3-19, F3-21','Resultado final não é sobrescrito indevidamente; removida a dependência da decisão manual F3-26.')
f(28,1,'FT-02','Entregar resultado assíncrono correlacionado ao parceiro','F3-05, F3-10, F3-19','Retorno posterior identifica simulação e análise; confirmação e autenticação conforme contrato.')
f(29,1,'FT-02','Registrar tentativas e recuperar falhas de retorno','F3-28','Falhas ficam rastreáveis e permitem recuperação sem duplicar decisões.')
f(11,1,shared,'Implementar logs, métricas, alertas e rastreio','F3-07','Simulação, análise e retorno rastreáveis pelos identificadores correlacionados.')
f(30,1,'FT-02','Manter trilha de auditoria da solicitação e decisão','F3-18, COR-01','Registrar transições e decisões com vínculo à simulação e ao parceiro.')
add('SEC-01',1,shared,'Autenticar e autorizar o consumo das APIs','F3-10, F3-16, SIM-01',
    'Isolar parceiros; bloquear acesso ou referência a simulação de outro parceiro; testar falhas de autenticação.', 'E1-03, E1-08')
f(12,1,shared,'Executar testes de carga e resiliência das APIs','F3-27, F3-29, SEC-01, SIM-01','Validar carga, indisponibilidade da PDEC, timeout, duplicação e recuperação conforme requisitos acordados.')
f(13,1,shared,'Homologar simulação, análise e retorno com o parceiro','SIM-01, COR-01, F3-27, F3-29, F3-30, SEC-01','Fluxo completo homologado, incluindo correlação inválida/expirada e ausência de decisão automática.')
f(14,1,shared,'Preparar implantação, runbook, rollback e onboarding','F3-11, F3-29','Operação e procedimentos de recuperação documentados e revisados.')
f(15,1,shared,'Disponibilizar a Entrega 1 e obter aceite do negócio','F3-12, F3-13, F3-14','Duas APIs e correlação homologadas e disponibilizadas para a data-alvo de 11/01/2027.')
items[-1]['deadline']='2027-01-11'

add('STS-01',2,'FT-03','Definir contrato da API de status','F3-02','Estados, autorização, identificadores e conteúdo do resultado definidos.',kind='Spike')
add('STS-02',2,'FT-03','Implementar consulta de andamento e resultado','STS-01, F3-18, F3-15','Consulta autorizada retorna estado e resultado correlacionados, incluindo andamento manual quando disponível.')
f(4,2,'FT-04','Mapear pontos de extensão da PCRE-JULG para a mesa mínima','','Pontos de integração, campos e regras da atuação manual definidos.')
f(9,2,'FT-04','Provisionar tópicos, schemas e ACLs Kafka para a mesa','F3-04, F3-06','Eventos de derivação e decisão disponíveis com permissões e contratos definidos.')
f(20,2,'FT-04','Publicar derivação para a mesa com outbox','F3-09, F3-19, F3-15','Casos de decisão manual encaminhados com entrega confiável e correlação.')
f(22,2,'FT-04','Consumir derivações e exibir fila única FIDC','F3-04, F3-09, F3-20','Solicitações disponíveis na PCRE-JULG, sem gestão avançada de filas.')
f(23,2,'FT-04','Exibir dados da solicitação e resultado automático','F3-22','Analista consulta os dados necessários ao julgamento, sem fluxo documental.')
f(24,2,'FT-04','Registrar e publicar decisão manual','F3-23','Decisão registrada e auditada; sem ação de pendenciar nesta entrega.')
f(25,2,'FT-04','Controlar perfis de acesso à mesa','F3-22','Somente analistas autorizados consultam e decidem solicitações.')
f(26,2,'FT-04','Consolidar decisão manual e atualizar retorno e status','F3-20, F3-24, F3-27, STS-02','Decisão manual protegida contra duplicação; status atualizado e resultado comunicado pelo fluxo de retorno existente.')
add('HML-02',2,'FT-03 + FT-04','Homologar status e análise julgamental mínima','F3-26, F3-25, STS-02','Validar autorização, derivação, fila, decisão, duplicação e retorno ponta a ponta.',kind='Task')
add('REL-02',2,'FT-03 + FT-04','Implantar Entrega 2 e atualizar operação','HML-02, F3-14','Aceite do negócio, monitoramento e plano de implantação e rollback definidos.',kind='Task')

acceptances = [
    'Motivos, documentos obrigatórios, prazo, expiração e condições para reanálise acordados.',
    'Armazenamento privado, retenção, limites de arquivo e isolamento definidos.',
    'Contratos documentais e notificações definidos com protocolo e versão da pendência; ampliar API de status.',
    'Desenho de estados, eventos, upload, acessos e responsabilidades concluído.',
    'Bucket privado, permissões, notificações e quarentena disponíveis.',
    'Analista registra motivo, documentos, prazo e versão ativa da pendência na PCRE-JULG.',
    'Esteira registra a pendência e notifica o parceiro para avisar o cliente; andamento disponível no status.',
    'Cliente autorizado recebe acesso temporário por documento, vinculado à pendência ativa.',
    'Cliente consulta os requisitos e envia arquivos pelo canal ao armazenamento privado.',
    'Arquivos validados antes da liberação; conteúdo inválido isolado; envio parcial mantém a pendência.',
    'Conclusão publicada com outbox e idempotência somente após todos os documentos obrigatórios válidos.',
    'Retomar análise uma única vez por versão ativa; evento antigo não reabre análise encerrada.',
    'Analista autorizado consulta arquivos válidos e histórico; acesso auditado.',
    'Permitir corrigir arquivo rejeitado ou envio expirado preservando histórico e vínculo.',
    'Homologar pendência, envio parcial, acesso indevido, falhas, correção e retomada sem duplicação.',
    'Implantar com métricas, alertas, runbook e rollback; aceite do negócio obtido.',
]
for num in range(1,17):
    ident=f'D3-{num:02}'; x=ORIGINAL[ident]
    deps=list(dict.fromkeys(x['deps']+x.get('prerequisites',[])))
    if num==6: deps.append('REL-02')
    if num==7: deps.append('STS-02')
    if num==15: deps=[('REL-02' if d=='F3-15' else d) for d in deps]
    add(ident,3,'FT-05',x['title'],', '.join(deps),acceptances[num-1],ident,x['type'])

assert len(items)==55
assert len({x['id'] for x in items})==len(items)
assert set(ORIGINAL).issubset({x['id'] for x in items})
byid={x['id']:x for x in items}
done=set()
while len(done)<len(items):
    ready={x['id'] for x in items if x['id'] not in done and set(x['deps'])<=done}
    assert ready, 'Dependência ausente ou circular'
    done|=ready
assert all(byid[d]['delivery']<=x['delivery'] for x in items for d in x['deps'])
data=dict(epic=EPIC, features=[dict(id=i,delivery=d,title=t,scope=s) for i,d,t,s in FEATURES],items=items)
(ROOT/'modelos/backlog-entregas-nova-mesa.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if '--backlog-only' in sys.argv:
    print(f'OK: {len(items)} itens; fonte atualizada sem alterar os PDFs.')
    sys.exit(0)

# One-page A4, com texto vetorial e limites de altura verificados.
OUT.parent.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
c=canvas.Canvas(str(OUT),pagesize=(595.28,841.89))
c.setTitle('Entrega 1 - APIs de simulação e análise de crédito')
c.setAuthor('Arquitetura de crédito')
NAVY='#001E62'; BLUE='#0033CC'; INK='#202B3C'; GRAY='#526176'; PALE='#EDF2FF'


def rect(x,y,w,h,color):
    c.setFillColor(HexColor(color)); c.rect(x,841.89-y-h,w,h,fill=1,stroke=0)


def text(value,x,top,w,size=10,color=INK,bold=False,maxh=100,leading=None):
    st=ParagraphStyle('p',fontName='Arial-Bold' if bold else 'Arial',fontSize=size,
                      leading=leading or size*1.36,textColor=HexColor(color))
    p=Paragraph(value,st); _,h=p.wrap(w,maxh)
    assert h<=maxh+0.1,(value,h,maxh)
    p.drawOn(c,x,841.89-top-h)
    return h


rect(0,0,595.28,132,NAVY)
text('NOVA MESA FIDC',32,22,531,10,'#C7D7FF',True,20)
text('Entrega 1',32,43,531,29,'#FFFFFF',True,42)
text('APIs de simulação e análise de crédito',32,88,531,15,'#FFFFFF',False,25)
text('Disponibilizar a jornada automática com correlação entre simulação, análise e resultado.',32,148,531,11,maxh=36)

for x,date,label in [(32,'16/11/2026','Início preliminar'),(214,'20/11/2026','Contratos e REF'),(396,'11/01/2027','Data-alvo da entrega')]:
    rect(x,193,167,64,PALE)
    text(date,x+12,203,143,16,BLUE,True,23)
    text(label,x+12,231,143,9.5,GRAY,maxh=15)

text('DUAS FEATURES',32,277,531,10,BLUE,True,18)
for x,num,title,body in [
    (32,'01','API de simulação','Execução síncrona.<br/>Valida dados e aplica as regras de simulação.<br/>Retorna resultado e identificador na mesma chamada.'),
    (305,'02','API de análise de crédito','Execução assíncrona.<br/>Aceite com protocolo, análise automática e correlação com a simulação.<br/>Retorno posterior ao parceiro.')]:
    rect(x,302,258,147,'#F4F6FA')
    text(num,x+14,314,40,12,BLUE,True,18)
    text(title,x+14,339,230,12,NAVY,True,22)
    text(body,x+14,367,230,10,maxh=70)
text('Segurança, idempotência, persistência, auditoria e recuperação de falhas compõem as duas features. Callback com mTLS é a proposta de retorno, a confirmar no contrato.',32,460,531,9,GRAY,maxh=38)

text('PREMISSAS PARA 11/01',32,511,531,10,BLUE,True,18)
text('Contratos e REF definidos até <b>20/11</b>, incluindo o tratamento dos casos sem decisão automática. Preparação técnica começa em <b>16/11</b>. Confirmar capacidade realocada e homologação com o parceiro.',32,534,531,10,maxh=46)

text('TRADE-OFFS DA REALOCAÇÃO',32,596,531,10,BLUE,True,18)
for top,name,body in [
    (620,'Vitor','Modernização da esteira automática: de 2 devs para 1 dev.'),
    (651,'Gustavo','Migração PTA para PCRE-JULG: <b>15/02/2027</b>. Renegociar com a Serasa a desativação da API String.'),
    (695,'Aine','Migração de bureaux desacelera. Neurotech passa integralmente para 2027.')]:
    text(name,32,top,70,10,NAVY,True,18)
    text(body,112,top,451,9.5,maxh=32)

rect(32,744,531,58,PALE)
text('PRÓXIMAS ENTREGAS',44,753,507,9,BLUE,True,14)
text('<b>2:</b> API de status e julgamental mínima. <b>3:</b> pendências e troca de arquivos.<br/>Datas a definir. Esses escopos ficam fora da Entrega 1.',44,773,507,9,maxh=25)
text('Planejamento atualizado em 12/11/2026',32,818,531,8,GRAY,maxh=12)
c.showPage(); c.save()
print(f'OK: {len(items)} itens, {len(FEATURES)} features; {OUT}')
