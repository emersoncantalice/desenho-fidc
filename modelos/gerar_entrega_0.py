"""Gera a vista da Entrega 1 sem substituir os cenários completos."""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def node(ident, x, y, w, h, title, detail, kind='component', change=''):
    return dict(id=ident, x=x, y=y, w=w, h=h, title=title,
                detail=detail, kind=kind, change=change)


def edge(ident, source, target, label, source_side='right', target_side='left', asynchronous=False):
    return dict(id=ident, source=source, target=target, label=label,
                sourceSide=source_side, targetSide=target_side, async_=asynchronous, via=None)


model = dict(name='Entrega 1 — Simulação e análise automática', width=1800, height=1540,
             nodes=[
    node('heading', 40, 20, 1720, 85, 'ENTREGA 1 | 11/01/2027',
         'Simulação síncrona + análise de crédito assíncrona + correlação', 'heading'),
    node('sync', 40, 130, 1720, 290, '01 | SIMULAÇÃO SÍNCRONA',
         'A simulação é salva na base; resultado e identificador são devolvidos na mesma chamada.', 'group'),
    node('partner', 70, 230, 340, 130, 'Parceiro',
         'Solicita a simulação\nRecebe resultado + idSimulacao\nNomes dos campos a contratar'),
    node('simulation', 580, 230, 450, 130, 'API de simulação',
         'Valida a entrada e aplica as regras\nSalva dados e resultado da simulação\nRetorna resultado + idSimulacao', change='new'),
    node('rules', 1350, 230, 370, 130, 'PDEC | Simulação',
         'Regras de simulação\nREF até 20/11/2026\nIntegração a detalhar no contrato'),
    node('async', 40, 460, 1720, 660, '02 | ANÁLISE DE CRÉDITO ASSÍNCRONA',
         'Aceite inicial com protocolo; processamento e resultado posteriores. Sem API de status e sem mesa.', 'group'),
    node('requester', 70, 570, 340, 140, 'Parceiro | Solicitação',
         'Envia idSimulacao já persistido\nSolicita a análise de crédito\nRecebe protocolo de aceite\nNão aguarda a decisão de crédito'),
    node('analysis', 580, 570, 450, 140, 'API / esteira de análise',
         'Recebe idSimulacao e consulta a base\nVincula análise à simulação persistida\nPersiste o aceite e agenda a análise\nProcessamento assíncrono; sem mesa', change='new'),
    node('pdec', 1350, 570, 370, 140, 'PDEC | Análise automática',
         'Execução após o aceite\nREF até 20/11/2026\nCasos sem decisão: definir na REF\nChamada interna conforme contrato'),
    node('callback', 70, 900, 340, 150, 'Retorno ao parceiro',
         'Resultado posterior e correlacionado\nCallback com mTLS é a proposta\nConfirmar mecanismo até 20/11\nPrever retentativas e recuperação'),
    node('db', 580, 900, 450, 150, 'Persistência da esteira | MySQL',
         'Simulação: dados, resultado e identificador\nAnálise vinculada pelo idSimulacao\nEstados, decisões e tentativas de retorno', 'database', 'new'),
    node('excluded', 1350, 900, 370, 150, 'ENTREGAS POSTERIORES',
         'Entrega 2: API de status\nMesa mínima, fila e decisão manual\nEntrega 3: pendências e arquivos\nDatas a definir', 'note', 'legacy'),
    node('milestones', 40, 1170, 550, 230, 'MARCOS E PREMISSAS',
         '16/11/2026: início dos trabalhos preliminares\n20/11/2026: contratos e REF definidos\n11/01/2027: Entrega 1\n\nPrazo depende de definições e capacidade.\nPreparação técnica em paralelo aos contratos.', 'note'),
    node('tradeoffs', 625, 1170, 1135, 230, 'REALOCAR PESSOAS PARA O DESENVOLVIMENTO',
         'Vitor | Modernização da esteira automática: redução de 2 devs para 1 dev.\nGustavo | Migração da tela PTA → PCRE-JULG: novo prazo em 15/02/2027.\n                 Renegociar com a Serasa a desativação da API String (pendente).\nAine | Migração de bureaux desacelera; Neurotech passa integralmente para 2027.\n\nAlocação nominal e dedicação na Entrega 1 ainda precisam ser confirmadas.\n15/02/2027 é o prazo da migração da tela, não da segunda entrega FIDC.', 'note'),
    node('legend', 40, 1450, 1720, 65, '',
         'Azul: entrega a implementar. Cinza: escopo posterior. IDs ilustrativos, sujeitos ao contrato.\nPontilhado: resultado posterior ao aceite; o transporte do callback pode ser uma chamada HTTP síncrona.', 'text'),
], edges=[
    edge('simulate', 'partner', 'simulation', 'Solicitação / resultado'),
    edge('simulate_rules', 'simulation', 'rules', 'Regras / resultado'),
    edge('accept', 'requester', 'analysis', 'Solicitação / aceite'),
    edge('decide', 'analysis', 'pdec', 'Decisão automática'),
    edge('save_simulation', 'simulation', 'db', 'Salva simulação', 'bottom', 'right'),
    edge('persist', 'analysis', 'db', 'Salva vínculo', 'bottom', 'top'),
    edge('load_simulation', 'db', 'analysis', 'Simulação salva', 'top', 'bottom'),
    edge('notify', 'analysis', 'callback', 'Resultado correlacionado', 'left', 'top', True),
])

if __name__ == '__main__':
    path = ROOT / 'modelos/entrega-0-nova-mesa.json'
    path.write_text(json.dumps(model, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    subprocess.run(['node', '-e',
                    "const fs=require('fs'); const {render}=require('./modelos/renderizador.js');"
                    "fs.writeFileSync(process.argv[2],render(JSON.parse(fs.readFileSync(process.argv[1],'utf8'))));",
                    str(path), str(ROOT / 'diagramas/entrega-0-nova-mesa.svg')], cwd=ROOT, check=True)
