"""Backlog simplificado da Entrega 1 (11/01/2027) em Excel: título, contexto e critérios de aceite.

Classificação dos itens:
- Spike: descoberta ou definição que destrava o desenvolvimento;
- Task: provisionamento de recursos e atividades de validação e implantação;
- Story: tudo o que muda o comportamento em produção.
O desenho de arquitetura fica na feature (aba Features), não vira item de backlog.

Execução: $env:PYTHONPATH='tmp/pdf-deps'; python modelos/gerar_backlog_simplificado_entrega_1.py
"""
import csv
from math import ceil
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/nova-mesa-20261113/backlog-simplificado-entrega-1.xlsx'
OUT.parent.mkdir(parents=True, exist_ok=True)

NAVY, BLUE, INK, MUTED = '001E62', '0033CC', '202B3C', '536174'
ZEBRA, LINE = 'F4F6FA', 'CCD7ED'
TYPE_FILL = {'Spike': 'FFF4DF', 'Task': 'EDF2FF', 'Story': 'E8F5EC'}
FT1, FT2, BOTH = 'FT-01', 'FT-02', 'FT-01 + FT-02'

FEATURES = [
    (FT1, 'API de simulação',
     'O parceiro envia os dados da simulação e recebe o resultado e o idSimulacao na mesma chamada. '
     'A simulação fica salva na base e é a origem da análise de crédito.',
     ['Parceiro → Apigee (mTLS e credencial do app) → serviço de simulação no GCP.',
      'Serviço executa a política de simulação na PDEC e salva dados e resultado no MySQL cloud.',
      'idSimulacao é a chave de correlação com a análise de crédito.',
      'SLA de tempo de resposta e timeouts de cada chamada definidos (SPK-06).'],
     ['Desenho de arquitetura da feature aprovado até 24/11/2026.',
      'API em produção atendendo ao contrato e ao SLA acordados.',
      'Simulação e resultado salvos e recuperáveis pelo idSimulacao.',
      'Fluxo homologado com o parceiro.']),
    (FT2, 'API de análise de crédito assíncrona',
     'O parceiro solicita a análise informando o idSimulacao, recebe um protocolo de aceite e, depois, '
     'o resultado por callback com mTLS. Não há API de status nem análise manual nesta entrega.',
     ['Parceiro → Apigee (mTLS) → orquestrador da esteira: valida, vincula à simulação, persiste e devolve o protocolo.',
      'Execução assíncrona (mecanismo do SPK-04) → política de análise na PDEC → resultado no MySQL cloud.',
      'Callback síncrono com mTLS à API do parceiro, com retentativas e reprocessamento.',
      'Estados internos, idempotência e auditoria correlacionados por protocolo e idSimulacao.'],
     ['Desenho de arquitetura da feature aprovado até 24/11/2026.',
      'Toda análise fica vinculada a uma simulação válida do mesmo parceiro.',
      'Resultado entregue por callback com protocolo e idSimulacao, sem perda em caso de falha.',
      'Fluxo homologado com o parceiro.']),
]
OUT_OF_SCOPE = ('API de status; análise manual e mesa julgamental na PCRE-JULG; pendência documental; '
                'geração de proposta, formalização ou pagamento.')

# (id, feature, tipo, título, contexto, critérios de aceite)
ITEMS = [
    # ── Spikes: descobertas e definições ──────────────────────────────────────
    ('SPK-01', BOTH, 'Spike', 'Definir os contratos de entrada e saída das APIs',
     'As APIs de simulação (síncrona) e de análise (assíncrona) precisam de contrato acordado com o parceiro até '
     '20/11/2026. Sem API de status, o contrato do callback é o único meio de o parceiro receber o resultado.',
     ['Contrato da API de simulação: requisição, resposta com resultado e idSimulacao, erros e timeout.',
      'Contrato da API de análise: requisição com idSimulacao, aceite com protocolo, chave de idempotência e erros.',
      'Contrato do callback: payload com protocolo e idSimulacao, confirmação de recebimento, códigos de resposta e política de retentativas.',
      'Regras de correlação definidas: validade da simulação, titularidade, compatibilidade dos dados e quantas análises uma simulação admite.',
      'Contratos versionados (OpenAPI), com exemplos, aceitos pelo parceiro até 20/11/2026.']),
    ('SPK-02', BOTH, 'Spike', 'Especificar as políticas de crédito a partir da REF',
     'O negócio entrega até 20/11/2026 a REF com as regras de simulação e de análise automática. Não entra '
     'derivação para análise manual, então a REF precisa definir o que acontece quando não há decisão automática.',
     ['Variáveis de entrada, fontes de dados e saídas de cada política mapeadas.',
      'Regras de simulação e de análise especificadas para implementação na PDEC.',
      'Tratamento definido para casos sem decisão automática, sem encaminhamento à mesa.',
      'Dados externos usados pelas políticas (ex.: bureaux) identificados, com integração disponível no prazo.',
      'Massa de cenários de teste com resultado esperado validada com o negócio.']),
    ('SPK-03', BOTH, 'Spike', 'Definir o modelo de dados com o time de AD',
     'Ponto de atenção do plano: a modelagem da base precisa ser priorizada com o time de AD para não bloquear '
     'o desenvolvimento. A base guarda simulação, análise, vínculo entre elas e tentativas de callback.',
     ['Modelo lógico e físico aprovado pelo time de AD.',
      'Entidades cobertas: simulação e resultado, solicitação de análise e protocolo, estados da análise, vínculo simulação ↔ análise, tentativas de callback e auditoria.',
      'Chaves, índices e restrições de unicidade para idempotência definidos.',
      'Retenção e tratamento de dados pessoais (LGPD) definidos.']),
    ('SPK-04', FT2, 'Spike', 'Definir o mecanismo de execução assíncrona do orquestrador',
     'A análise é aceita com protocolo e processada depois. Sem mesa nesta entrega, o Kafka da derivação manual '
     'não é obrigatório; é preciso decidir como o orquestrador enfileira e processa as análises.',
     ['Opções avaliadas (ex.: Pub/Sub, Kafka, outbox no MySQL) com prós, contras e custo.',
      'Decisão registrada considerando garantia de entrega, reprocessamento e volume esperado.',
      'Estratégia de retentativa e de mensagens com falha definida.',
      'Decisão incorporada ao desenho de arquitetura da FT-02 até 24/11/2026.']),
    ('SPK-05', BOTH, 'Spike', 'Definir o mTLS e a identificação do parceiro no Apigee e no callback',
     'As duas chamadas com o parceiro (entrada nas APIs e callback) exigem mTLS. O parceiro precisa enviar o '
     'certificado até 12/12/2026.',
     ['Terminação mTLS de entrada no Apigee definida, com a cadeia de certificados aceita.',
      'Certificado cliente do callback definido: emissão, armazenamento, rotação e revogação.',
      'Identificação do parceiro na requisição definida (certificado e credencial do app no Apigee).',
      'Insumos e prazos combinados com o parceiro, incluindo o certificado até 12/12/2026.']),
    ('SPK-06', FT1, 'Spike', 'Definir o SLA e validar o tempo de resposta da simulação síncrona',
     'A simulação responde na mesma chamada. O tempo total soma Apigee, serviço, PDEC e base, e ainda não há '
     'SLA nem volume acordados.',
     ['SLA de tempo de resposta e volume de pico acordados com o parceiro.',
      'Latência da política de simulação na PDEC medida.',
      'Timeout de cada chamada definido de forma coerente com o SLA.',
      'Riscos de capacidade registrados no desenho da FT-01.']),

    # ── Tasks: provisionamento de recursos ────────────────────────────────────
    ('TSK-01', BOTH, 'Task', 'Provisionar os ambientes no GCP e o pipeline de CI/CD',
     'O serviço de simulação e o orquestrador rodam no GCP. Ambientes e pipeline precisam estar prontos para o '
     'início do desenvolvimento, previsto para 25/11/2026.',
     ['Ambientes de desenvolvimento, homologação e produção criados no runtime definido no desenho.',
      'Repositórios e pipeline com build, testes, análise de código e deploy por ambiente.',
      'Service accounts com permissões mínimas por serviço.',
      'Secret Manager configurado para credenciais e certificados.']),
    ('TSK-02', BOTH, 'Task', 'Provisionar o MySQL cloud',
     'Base da esteira com simulação, análise, vínculo e callback, conforme o modelo do SPK-03.',
     ['Instâncias de homologação e produção criadas em rede privada.',
      'Usuários por serviço com privilégios mínimos.',
      'Backup, recuperação e alta disponibilidade configurados conforme o desenho.',
      'Conexão validada a partir dos serviços em cada ambiente.']),
    ('TSK-03', BOTH, 'Task', 'Provisionar o Apigee para as APIs do parceiro',
     'A entrada do parceiro passa pelo Apigee. Antes dos proxies, é preciso ter ambientes, produto de API e '
     'credenciais.',
     ['Ambientes e hostnames de homologação e produção configurados.',
      'Produto de API da nova mesa FIDC criado com as duas APIs.',
      'App e credenciais do parceiro criados em homologação.',
      'Truststore do mTLS de entrada configurado com o certificado do parceiro.']),
    ('TSK-04', FT2, 'Task', 'Provisionar certificados e conectividade de saída para o callback',
     'O callback chama a API do parceiro com mTLS. O parceiro pode exigir IP de origem fixo para liberar o acesso.',
     ['Certificado cliente emitido para homologação e produção e guardado no Secret Manager.',
      'IP de saída fixo configurado e informado ao parceiro, se exigido.',
      'Rota de saída até a API do parceiro liberada e testada em homologação.',
      'Cadeia de certificados do servidor do parceiro configurada como confiável.']),
    ('TSK-05', BOTH, 'Task', 'Liberar a conectividade dos serviços com a PDEC',
     'O serviço de simulação e o orquestrador chamam as políticas de crédito na PDEC (GCP / Kubernetes).',
     ['Rotas e regras de firewall entre os serviços e a PDEC liberadas em homologação e produção.',
      'Credenciais de acesso à PDEC emitidas por serviço.',
      'Chamada de teste à PDEC executada com sucesso a partir de cada ambiente.']),
    ('TSK-06', FT2, 'Task', 'Provisionar a fila de execução assíncrona',
     'Infraestrutura do mecanismo decidido no SPK-04. Se a decisão for outbox no MySQL, esta task se limita à '
     'configuração do processamento.',
     ['Fila ou tópico e fila de falhas criados em homologação e produção.',
      'Permissões de publicação e consumo por service account.',
      'Retenção e política de reentrega configuradas conforme o SPK-04.']),
    ('TSK-07', BOTH, 'Task', 'Provisionar a observabilidade: logs, métricas, dashboards e alertas',
     'Sem API de status, o time precisa enxergar sozinho onde está cada análise e cada callback.',
     ['Logs estruturados centralizados e pesquisáveis por idSimulacao e protocolo.',
      'Dashboard com volume, latência e erros de simulação, análise, PDEC e callback.',
      'Alertas para falha da PDEC, fila acumulando e callbacks esgotados, com destino de plantão definido.']),

    # ── Stories: mudanças em produção ─────────────────────────────────────────
    ('US-01', BOTH, 'Story', 'Criar o schema da base no MySQL',
     'Implementa o modelo de dados aprovado no SPK-03 com migrations versionadas, aplicadas pelo pipeline.',
     ['Migrations criam tabelas, índices e restrições do modelo aprovado.',
      'Migrations aplicadas pelo pipeline em homologação e produção, com rollback testado.',
      'Restrições de unicidade garantem a idempotência definida no contrato.']),
    ('US-02', FT1, 'Story', 'Desenvolver a política de crédito de simulação na PDEC',
     'Implementa na PDEC as regras de simulação da REF, especificadas no SPK-02.',
     ['Regras da REF implementadas e versionadas na PDEC.',
      'Todos os cenários da massa de teste retornam o resultado esperado.',
      'Entrada e saída da política documentadas para o serviço de simulação.',
      'Política publicada em homologação, com aprovação do negócio para produção.']),
    ('US-03', FT2, 'Story', 'Desenvolver a política de crédito de análise automática na PDEC',
     'Implementa na PDEC as regras de análise automática da REF, especificadas no SPK-02.',
     ['Regras da REF implementadas e versionadas na PDEC.',
      'Todos os cenários da massa de teste retornam o resultado esperado.',
      'Casos sem decisão automática retornam o tratamento definido na REF, sem derivação para análise manual.',
      'Política publicada em homologação, com aprovação do negócio para produção.']),
    ('US-04', FT1, 'Story', 'Desenvolver o serviço da API de simulação',
     'Serviço no GCP que recebe a simulação, executa a política na PDEC, salva dados e resultado e responde na '
     'mesma chamada.',
     ['Valida o payload conforme o contrato e retorna erros padronizados.',
      'Executa a política de simulação e salva dados e resultado na base antes de responder.',
      'Retorna o resultado e o idSimulacao na mesma chamada.',
      'Respeita o timeout acordado; com a PDEC indisponível, retorna o erro do contrato sem gravar simulação inconsistente.',
      'A simulação fica associada ao parceiro que a criou.']),
    ('US-05', FT1, 'Story', 'Publicar a API de simulação no Apigee',
     'Proxy que expõe o serviço de simulação ao parceiro com mTLS e controles de consumo.',
     ['Proxy publicado com mTLS de entrada e validação da credencial do parceiro.',
      'Identidade do parceiro repassada ao serviço pelo proxy, sem depender de dado enviado pelo cliente.',
      'Limites de taxa e quota configurados conforme o volume acordado.',
      'Requisições sem certificado válido ou de app não autorizado são rejeitadas.',
      'Especificação OpenAPI publicada para o parceiro.']),
    ('US-06', FT2, 'Story', 'Publicar a API de análise de crédito no Apigee',
     'Proxy que expõe o orquestrador ao parceiro com mTLS e controles de consumo.',
     ['Proxy publicado com mTLS de entrada e validação da credencial do parceiro.',
      'Identidade do parceiro repassada ao orquestrador pelo proxy.',
      'Limites de taxa e quota configurados conforme o volume acordado.',
      'Requisições sem certificado válido ou de app não autorizado são rejeitadas.',
      'Especificação OpenAPI publicada para o parceiro.']),
    ('US-07', FT2, 'Story', 'Orquestrador: receber a análise, vincular à simulação e devolver o protocolo',
     'Entrada da esteira de análise. É aqui que a análise de crédito passa a ficar correlacionada à simulação.',
     ['Valida o payload e o idSimulacao: simulação inexistente, expirada, de outro parceiro ou incompatível é recusada com o erro do contrato.',
      'Persiste a solicitação com o vínculo à simulação antes de responder.',
      'Responde com o protocolo de aceite sem aguardar a decisão de crédito.',
      'A mesma chave de idempotência devolve o mesmo protocolo, sem criar nova análise.',
      'Solicitação encaminhada para processamento assíncrono.']),
    ('US-08', FT2, 'Story', 'Orquestrador: executar a análise automática e registrar o resultado',
     'Processamento assíncrono da análise: controla os estados internos, chama a política de análise na PDEC e '
     'grava o resultado.',
     ['Estados internos controlados (ex.: recebida, em análise, concluída, sem decisão, erro), com transições auditáveis.',
      'Chama a política de análise na PDEC com os dados da solicitação e da simulação vinculada.',
      'Resultado gravado com o vínculo ao protocolo e à simulação.',
      'Falha temporária da PDEC gera retentativa; esgotadas as tentativas, a análise fica em erro para reprocessamento, sem perder a solicitação.',
      'Processamento duplicado ou tardio não sobrescreve um resultado final.']),
    ('US-09', FT2, 'Story', 'Enviar o resultado da análise ao parceiro por callback',
     'Sem API de status, o callback é o único meio de o parceiro receber o resultado. É uma chamada síncrona, '
     'com mTLS, à API do parceiro, que confirma o recebimento.',
     ['Ao concluir a análise, chama a API do parceiro com mTLS e o payload do contrato.',
      'O payload identifica o protocolo e o idSimulacao.',
      'O callback só é marcado como entregue após a confirmação de recebimento do parceiro.',
      'Cada tentativa é registrada com data, resposta e tempo.']),
    ('US-10', FT2, 'Story', 'Retentar e reprocessar callbacks com falha',
     'Falhas na API do parceiro não podem fazer o resultado se perder.',
     ['Falhas temporárias são retentadas conforme a política do contrato (intervalo e limite).',
      'Esgotadas as tentativas, o callback fica pendente e gera alerta.',
      'A operação consegue reenviar o callback de uma análise sem reprocessar a decisão.',
      'O reenvio mantém o mesmo protocolo e idSimulacao.']),
    ('US-11', BOTH, 'Story', 'Registrar a trilha de auditoria e o rastreio ponta a ponta',
     'A correlação precisa ser verificável internamente: simulação → análise → resultado → callback.',
     ['Identificador de correlação propagado do Apigee aos serviços, à PDEC e ao callback.',
      'Auditoria registra a simulação, o aceite, as transições, a decisão e as entregas do callback, com data e origem.',
      'A jornada completa pode ser consultada internamente pelo idSimulacao ou pelo protocolo.',
      'Logs não expõem dados pessoais sem máscara.']),

    # ── Tasks: validação e implantação ────────────────────────────────────────
    ('TSK-08', BOTH, 'Task', 'Executar testes de carga e resiliência',
     'Validar o volume acordado e o comportamento em falha antes da homologação com o parceiro.',
     ['A simulação atende ao SLA no volume de pico acordado (SPK-06).',
      'A análise processa o volume esperado sem acúmulo na fila.',
      'Cenários de falha validados: PDEC indisponível, parceiro fora do ar no callback e reinício dos serviços.',
      'Resultados registrados; gargalos corrigidos ou aceitos pelo negócio.']),
    ('TSK-09', BOTH, 'Task', 'Homologar o fluxo ponta a ponta com o parceiro',
     'Janela proposta de homologação: 04 a 08/01/2027.',
     ['Fluxo simulação → análise → callback executado com o parceiro, com mTLS nas duas direções.',
      'Cenários de correlação inválida, reenvio idempotente e caso sem decisão automática validados.',
      'Massa de cenários da REF validada com o negócio.',
      'Aceite do negócio e do parceiro registrado.']),
    ('TSK-10', BOTH, 'Task', 'Preparar a implantação em produção',
     'Data-alvo da Entrega 1: 11/01/2027.',
     ['Runbook de operação e de reprocessamento de callbacks publicado.',
      'Plano de implantação e rollback aprovado, com janela definida.',
      'Credenciais e certificados de produção do parceiro configurados e validados por smoke test.',
      'Monitoramento e alertas ativos em produção, com responsáveis de plantão definidos.']),
]

ids = [i[0] for i in ITEMS]
assert len(ids) == len(set(ids)), 'IDs duplicados'
assert all(i[1] in (FT1, FT2, BOTH) and i[2] in TYPE_FILL for i in ITEMS)

FONT = 'Arial'
thin = Side(style='thin', color=LINE)
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
TOP = Alignment(wrap_text=True, vertical='top')


def bullets(lines):
    return '\n'.join(f'• {line}' for line in lines)


def row_height(values_widths, base=12.75, pad=6):
    """Estima a altura da linha com quebra de texto (openpyxl não ajusta sozinho)."""
    lines = 1
    for value, width in values_widths:
        cpl = max(width * 1.05, 1)
        lines = max(lines, sum(max(1, ceil(len(part) / cpl)) for part in str(value).split('\n')))
    return lines * base + pad


def header(ws, row, labels):
    for col, value in enumerate(labels, 1):
        cell = ws.cell(row, col, value)
        cell.font = Font(name=FONT, size=10, bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor=NAVY)
        cell.alignment = Alignment(wrap_text=True, vertical='center')
        cell.border = BORDER
    ws.row_dimensions[row].height = 22


def title(ws, text, subtitle_lines):
    ws['A1'] = text
    ws['A1'].font = Font(name=FONT, size=15, bold=True, color=NAVY)
    ws.row_dimensions[1].height = 26
    for i, (value, bold, color) in enumerate(subtitle_lines, 2):
        ws.cell(i, 1, value).font = Font(name=FONT, size=10, bold=bold, color=color)


wb = Workbook()

# ── Aba Backlog ───────────────────────────────────────────────────────────────
ws = wb.active
ws.title = 'Backlog'
ws.sheet_view.showGridLines = False
title(ws, 'Backlog simplificado — Entrega 1 · data-alvo 11/01/2027', [
    ('EP-01 · FT-01 API de simulação · FT-02 API de análise de crédito assíncrona', True, BLUE),
    ('Spike = descoberta ou definição · Task = provisionamento, validação e implantação · '
     'Story = muda o comportamento em produção · Desenho de arquitetura: na aba Features.', False, MUTED),
    (f'Fora da Entrega 1: {OUT_OF_SCOPE}', False, MUTED),
])
COLS = ['ID', 'Feature', 'Tipo', 'Título', 'Contexto', 'Critérios de aceite']
WIDTHS = [9, 15, 9, 44, 58, 92]
HEAD = 6
header(ws, HEAD, COLS)
for col, w in enumerate(WIDTHS, 1):
    ws.column_dimensions[chr(64 + col)].width = w

for r, (iid, feature, kind, name, context, criteria) in enumerate(ITEMS, HEAD + 1):
    values = [iid, feature, kind, name, context, bullets(criteria)]
    for col, value in enumerate(values, 1):
        cell = ws.cell(r, col, value)
        cell.font = Font(name=FONT, size=10, color=INK, bold=col in (1, 4))
        cell.alignment = TOP
        cell.border = BORDER
        cell.fill = PatternFill('solid', fgColor=TYPE_FILL[kind] if col == 3 else (ZEBRA if r % 2 else 'FFFFFF'))
    ws.row_dimensions[r].height = row_height(zip(values[3:], WIDTHS[3:]))

LAST = HEAD + len(ITEMS)
ws.auto_filter.ref = f'A{HEAD}:F{LAST}'
ws.freeze_panes = f'B{HEAD + 1}'
dv = DataValidation(type='list', formula1='"Spike,Task,Story"', allow_blank=False)
ws.add_data_validation(dv)
dv.add(f'C{HEAD + 1}:C{LAST}')
dv_ft = DataValidation(type='list', formula1=f'"{FT1},{FT2},{BOTH}"', allow_blank=False)
ws.add_data_validation(dv_ft)
dv_ft.add(f'B{HEAD + 1}:B{LAST}')
ws.page_setup.orientation = 'landscape'
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.print_title_rows = f'{HEAD}:{HEAD}'

# ── Aba Features ──────────────────────────────────────────────────────────────
fs = wb.create_sheet('Features')
fs.sheet_view.showGridLines = False
title(fs, 'Features da Entrega 1 — desenho de arquitetura e critérios de aceite', [
    ('O desenho de arquitetura é parte da feature e deve estar aprovado até 24/11/2026.', True, BLUE),
    (f'Fora da Entrega 1: {OUT_OF_SCOPE}', False, MUTED),
])
F_COLS = ['ID', 'Feature', 'Contexto', 'Desenho de arquitetura', 'Critérios de aceite da feature']
F_WIDTHS = [9, 26, 52, 70, 56]
F_HEAD = 5
header(fs, F_HEAD, F_COLS)
for col, w in enumerate(F_WIDTHS, 1):
    fs.column_dimensions[chr(64 + col)].width = w
for r, (fid, name, context, design, criteria) in enumerate(FEATURES, F_HEAD + 1):
    values = [fid, name, context, bullets(design), bullets(criteria)]
    for col, value in enumerate(values, 1):
        cell = fs.cell(r, col, value)
        cell.font = Font(name=FONT, size=10, color=INK, bold=col in (1, 2))
        cell.alignment = TOP
        cell.border = BORDER
    fs.row_dimensions[r].height = row_height(zip(values[2:], F_WIDTHS[2:]))

# Contagem por tipo e feature: fórmulas sobre a aba Backlog.
S0 = F_HEAD + len(FEATURES) + 2
fs.cell(S0, 1, 'Itens por tipo').font = Font(name=FONT, size=11, bold=True, color=BLUE)
header(fs, S0 + 1, ['Tipo', FT1, FT2, BOTH, 'Total'])
rng_type = f'Backlog!$C${HEAD + 1}:$C${LAST}'
rng_feat = f'Backlog!$B${HEAD + 1}:$B${LAST}'
feat_cols = {'B': FT1, 'C': FT2, 'D': BOTH}
for i, kind in enumerate(['Spike', 'Task', 'Story']):
    r = S0 + 2 + i
    fs.cell(r, 1, kind)
    for col, ft in feat_cols.items():
        fs[f'{col}{r}'] = f'=COUNTIFS({rng_type},$A{r},{rng_feat},{col}${S0 + 1})'
    fs[f'E{r}'] = f'=SUM(B{r}:D{r})'
TOT = S0 + 5
fs.cell(TOT, 1, 'Total')
for col in 'BCDE':
    fs[f'{col}{TOT}'] = f'=SUM({col}{S0 + 2}:{col}{S0 + 4})'
for row in fs.iter_rows(min_row=S0 + 2, max_row=TOT, max_col=5):
    for cell in row:
        cell.font = Font(name=FONT, size=10, color=INK, bold=cell.row == TOT or cell.column == 1)
        cell.border = BORDER
        cell.alignment = Alignment(horizontal='left' if cell.column == 1 else 'center')
fs.cell(TOT + 1, 1, 'Contagens calculadas a partir das colunas Tipo e Feature da aba Backlog.').font = \
    Font(name=FONT, size=9, color=MUTED)

wb.calculation.fullCalcOnLoad = True
wb.save(OUT)

# CSV da aba Backlog: UTF-8 com BOM e ponto e vírgula, para abrir direto no Excel em pt-BR.
# Critérios de aceite ficam numa célula só, um por linha, entre aspas.
CSV_OUT = OUT.with_suffix('.csv')
with CSV_OUT.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(COLS)
    for iid, feature, kind, name, context, criteria in ITEMS:
        writer.writerow([iid, feature, kind, name, context, bullets(criteria)])
with CSV_OUT.open(encoding='utf-8-sig', newline='') as f:
    csv_rows = list(csv.reader(f, delimiter=';'))
assert csv_rows[0] == COLS and len(csv_rows) == len(ITEMS) + 1
assert all(len(row) == len(COLS) for row in csv_rows)
assert [row[5] for row in csv_rows[1:]] == [bullets(i[5]) for i in ITEMS]

# ── Verificações ──────────────────────────────────────────────────────────────
check = load_workbook(OUT)
bk = check['Backlog']
assert [c.value for c in bk[HEAD]] == COLS
rows = list(bk.iter_rows(min_row=HEAD + 1, max_row=LAST, values_only=True))
assert len(rows) == len(ITEMS) and all(all(v for v in row) for row in rows)
assert bk.cell(LAST + 1, 1).value is None
expected = {(k, f): sum(1 for i in ITEMS if i[2] == k and i[1] == f) for k in TYPE_FILL for f in feat_cols.values()}
ft = check['Features']
for i, kind in enumerate(['Spike', 'Task', 'Story']):
    r = S0 + 2 + i
    assert ft.cell(r, 1).value == kind
    for col, f in feat_cols.items():
        assert ft[f'{col}{S0 + 1}'].value == f and kind in TYPE_FILL
        assert ft[f'{col}{r}'].value == f'=COUNTIFS({rng_type},$A{r},{rng_feat},{col}${S0 + 1})'
counts = {k: sum(1 for i in ITEMS if i[2] == k) for k in TYPE_FILL}
print('OK:', OUT)
print('OK:', CSV_OUT)
print('Itens:', len(ITEMS), counts)
print('Esperado nas contagens:', {f'{k}/{f}': n for (k, f), n in expected.items()})
