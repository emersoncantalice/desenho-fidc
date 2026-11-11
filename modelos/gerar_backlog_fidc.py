"""Gera o planejamento dedicado FIDC + documentos sem alterar o cronograma geral."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def read_rows(path, prefix):
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.startswith('| ' + prefix + '-'):
            continue
        cells = [s.strip().replace('\\|', '|') for s in re.split(r'(?<!\\)\|', line)[1:-1]]
        ident, typ, title, team, size, deps = cells[:6]
        rows.append(dict(id=ident, type=typ, title=title, team=team, size=size,
                         duration=int(re.search(r'\((\d+)\)', size)[1]),
                         deps=[] if deps == '—' else deps.split(', ')))
    return rows

def schedule(items):
    pending = items.copy()
    done, free = {}, {}
    while pending:
        ready = [x for x in pending if all(d in done for d in x['deps'])]
        if not ready:
            raise ValueError('Dependência ausente ou circular')
        def start(x):
            return max([free.get(x['team'], 0)] + [done[d]['end'] for d in x['deps']]) + 1
        item = min(ready, key=lambda x: (start(x), x['id']))
        item['start'] = start(item)
        item['end'] = item['start'] + item['duration'] - 1
        free[item['team']] = item['end']
        done[item['id']] = item
        pending.remove(item)
    for item in items:
        assert item['end'] - item['start'] + 1 == item['duration']
        assert all(done[d]['end'] < item['start'] for d in item['deps'])
    for team in free:
        seq = sorted((x for x in items if x['team'] == team), key=lambda x:x['start'])
        assert all(a['end'] < b['start'] for a,b in zip(seq,seq[1:]))
    return items

def week(day):
    return f'M{(day-1)//20+1}·S{((day-1)%20)//5+1}'

base = read_rows(ROOT/'docs/cronograma-implementacao.md', 'F3')
assert len(base) == 30

raw = [
('Spike','Definir documentos exigidos, motivo, prazo, expiração e reanálise','EST',5,[]),
('Spike','Definir bucket privado, região, retenção, limites e validação de arquivos','INT',5,[]),
('Spike','Definir contratos de pendência, callback e correlação por protocolo e versão','EST',3,['D3-01','F3-02']),
('Task','Desenhar a extensão documental: estados, eventos, upload e responsabilidades','ARQ',10,[]),
('Task','Provisionar bucket privado, acessos, notificações e quarentena','INT',4,['D3-02','D3-04','F3-07']),
('Story','Analista pendencia a solicitação com motivo, documentos e prazo','MESA',5,['D3-01','D3-03','D3-04','F3-23']),
('Story','Esteira registra a pendência e notifica o parceiro, que avisa o cliente','INT',5,['D3-06','F3-18','F3-29']),
('Story','Autorizar o cliente e emitir URL temporária por documento da pendência','INT',5,['D3-03','D3-05','D3-06']),
('Story','Cliente consulta a pendência e envia os documentos pelo canal ao bucket','INT',5,['D3-07','D3-08']),
('Story','Validar arquivos recebidos e isolar conteúdo inválido antes da liberação','EST',10,['D3-05','D3-08','F3-08']),
('Story','Consolidar documentos válidos e publicar conclusão com outbox e idempotência','EST',5,['D3-10']),
('Story','Retomar a análise uma única vez, somente para a versão ativa da pendência','EST',5,['D3-11','F3-27']),
('Story','Analista consulta documentos por acesso autorizado e histórico auditável','MESA',3,['D3-10','F3-25']),
('Story','Cliente corrige arquivo rejeitado ou upload expirado preservando o histórico','INT',3,['D3-09','D3-10']),
('Task','Homologar pendência, upload parcial, acesso indevido, falhas e reanálise','MESA',5,['D3-12','D3-13','D3-14','F3-15']),
('Task','Implantar FIDC com documentos, métricas, alertas, runbook e rollback','INT',3,['D3-15','F3-12','F3-14']),
]
extra = []
for i,(typ,title,team,duration,deps) in enumerate(raw,1):
    size = 'Arquitetura' if i == 4 else 'Provisionamento' if i == 5 else {3:'Simples',5:'Média',10:'Complexa'}[duration]
    extra.append(dict(id=f'D3-{i:02}',type=typ,title=title,team=team,duration=duration,size=f'{size} ({duration})',deps=deps))
base = schedule(base)
for x in extra:
    x['prerequisites'] = [d for d in x['deps'] if d.startswith('F3-')]
    x['deps'] = [d for d in x['deps'] if d.startswith('D3-')]
extra = schedule(extra)
items = base + extra
assert sum(x['duration'] for x in base) == 145
assert sum(x['duration'] for x in extra) == 81
out = dict(title='Mesa FIDC + pendência documental',date='11/11/2026',
           effort=226,items=items,
           groups=[dict(name='Base FIDC',prefix='F3',effort=145,finish=max(x['end'] for x in base)),dict(name='Pendência documental',prefix='D3',effort=81,finish=max(x['end'] for x in extra))])
(ROOT/'modelos/backlog-fidc-documentos.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')

sys.dont_write_bytecode = True
from planejar_equipes_fidc import generate
generate(out)
