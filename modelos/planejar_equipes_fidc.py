"""Planejamento por perfil e capacidade, com rastreabilidade do backlog original."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import json

ROOT = Path(__file__).resolve().parents[1]
LEAD_ALLOCATION = 0.20

# O esforço original é repartido, não duplicado. BE prepara a API antes da UI.
SPLITS = {
    'F3-22': [('B', 'Backend', 3, 'Consumir derivações e expor API de fila e dados da mesa'),
              ('F', 'Frontend', 2, 'Exibir a fila única FIDC na PCRE-JULG')],
    'F3-24': [('B', 'Backend', 3, 'API de decisão manual e publicação no Kafka'),
              ('F', 'Frontend', 2, 'Tela para registrar a decisão manual')],
    'F3-25': [('B', 'Backend', 2, 'Autorizar os perfis do analista nas APIs'),
              ('F', 'Frontend', 1, 'Aplicar permissões na interface da mesa')],
    'F3-15': [('Q', 'QA', 2, 'Homologação da base FIDC com o negócio'),
              ('B', 'Backend', 1, 'Implantar a base FIDC após homologação')],
    'D3-06': [('B', 'Backend', 3, 'API de pendência: motivo, documentos, prazo e estado'),
              ('F', 'Frontend', 2, 'Tela para o analista pendenciar a solicitação')],
    'D3-13': [('B', 'Backend', 1, 'API autorizada para leitura e auditoria de documentos'),
              ('F', 'Frontend', 2, 'Tela de documentos e histórico para o analista')],
}
ROLES = {'F3-06': 'Arquiteto', 'D3-04': 'Arquiteto',
         'F3-04': 'Frontend', 'F3-23': 'Frontend',
         'D3-09': 'Frontend', 'D3-14': 'Frontend',
         'F3-12': 'QA', 'F3-13': 'QA', 'D3-15': 'QA'}

def week(day):
    return f'M{(day-1)//20+1}·S{((day-1)%20)//5+1}'

def expand(items):
    last = {x['id']: x['id'] + SPLITS[x['id']][-1][0] if x['id'] in SPLITS else x['id'] for x in items}
    result = []
    for src in items:
        parts = SPLITS.get(src['id'], [('', ROLES.get(src['id'], 'Backend'), src['duration'], src['title'])])
        assert sum(p[2] for p in parts) == src['duration']
        previous = None
        for suffix, role, duration, title in parts:
            ident = src['id'] + suffix
            result.append(dict(id=ident, origin=src['id'], type=src['type'], role=role,
                               duration=duration, title=title,
                               deps=[previous] if previous else [last[d] for d in src['deps']],
                               prerequisites=src.get('prerequisites', [])))
            previous = ident
    # Os testes finais abrangem também o controle de acesso do canal.
    if 'F3-12' in last:
        for x in result:
            if x['id'] == 'F3-13':
                x['deps'] = sorted(set(x['deps'] + [last['F3-10']]))
    return result

def schedule(items, developers):
    items = deepcopy(items)
    capacity = {'Backend': developers - 1, 'Frontend': 1, 'Arquiteto': 1, 'QA': 1}
    free = {role: [0] * n for role, n in capacity.items()}
    by_id = {x['id']: x for x in items}
    successors = {x['id']: [] for x in items}
    for x in items:
        for dep in x['deps']:
            assert dep in by_id, dep
            successors[dep].append(x['id'])
    ranks, visiting = {}, set()
    def rank(ident):
        if ident in visiting:
            raise ValueError('Dependências circulares')
        if ident not in ranks:
            visiting.add(ident)
            ranks[ident] = by_id[ident]['duration'] + max([rank(s) for s in successors[ident]] or [0])
            visiting.remove(ident)
        return ranks[ident]
    for x in items:
        rank(x['id'])
    pending, done = items.copy(), {}
    while pending:
        ready = [x for x in pending if all(d in done for d in x['deps'])]
        if not ready:
            raise ValueError('Nenhuma atividade disponível')
        def slot(x):
            employee = min(range(len(free[x['role']])), key=lambda n: (free[x['role']][n], n))
            start = max([free[x['role']][employee]] + [done[d]['end'] for d in x['deps']]) + 1
            return start, employee
        task = min(ready, key=lambda x: (slot(x)[0], -ranks[x['id']], x['id']))
        task['start'], employee = slot(task)
        task['end'] = task['start'] + task['duration'] - 1
        task['resource'] = f"{task['role']} {employee + 1}"
        free[task['role']][employee] = task['end']
        done[task['id']] = task
        pending.remove(task)
    finish = max(x['end'] for x in items)
    effort = Counter()
    for x in items:
        effort[x['role']] += x['duration']
        assert all(done[d]['end'] < x['start'] for d in x['deps'])
        assert x['end'] - x['start'] + 1 == x['duration']
    for resource in {x['resource'] for x in items}:
        rows = sorted((x for x in items if x['resource'] == resource), key=lambda x:x['start'])
        assert all(a['end'] < b['start'] for a,b in zip(rows, rows[1:])), resource
    return dict(developers=developers, backend=developers-1, frontend=1,
                people=developers+3, capacity={**capacity, 'ITLead':1},
                finish=finish, milestone=week(finish), effort=dict(effort),
                delivery_effort=sum(effort.values()),
                lead_effort=round(finish*LEAD_ALLOCATION, 1),
                lead_allocation=LEAD_ALLOCATION, items=items,
                management=dict(id='GESTAO', title='Planejar, acompanhar riscos, dependências e entregas',
                                role='ITLead', resource='ITLead 1', start=1, end=finish))

def generate(source):
    result = dict(date='11/11/2026', groups=[])
    for group in source['groups']:
        original = [x for x in source['items'] if x['id'].startswith(group['prefix'])]
        tasks = expand(original)
        slug = 'fidc' if group['prefix'] == 'F3' else 'pendencia-documental'
        plans = [schedule(tasks, n) for n in [2,3,4]]
        assert all(p['delivery_effort'] == group['effort'] for p in plans)
        result['groups'].append(dict(name=group['name'], prefix=group['prefix'], slug=slug,
                                     original_count=len(original), plans=plans))
    (ROOT/'modelos/cronogramas-equipes-fidc.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    lines = ['# Cronogramas por perfil — Mesa FIDC e documentos', '',
             'Comparação de capacidade com **2, 3 e 4 desenvolvedores**, aplicada separadamente à base FIDC e à extensão de pendência documental. Atualização: 2026-11-11.', '',
             '![Comparativo das equipes](../diagramas/comparativo-equipes-fidc.png)', '',
             '## Equipes e premissas', '',
             '| Desenvolvedores | Backend | Frontend | Arquiteto | ITLead | QA | Pessoas envolvidas |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    for n in [2,3,4]:
        lines.append(f'| {n} | {n-1} | 1 | 1 | 1 | 1 | {n+3} |')
    lines += ['', '**Desenvolvedores significa Backend + Frontend.** Arquiteto, ITLead e QA são profissionais adicionais. Foi mantido um Frontend e ampliado o Backend porque o backlog concentra APIs, estados, eventos, integrações e validação documental. É uma composição proposta para comparação, não uma equipe já confirmada.', '',
              '| Perfil | Responsabilidade | Disponibilidade usada no cálculo |',
              '| --- | --- | --- |',
              '| Arquiteto | Desenho da solução, componentes, contratos e responsabilidades | 1 profissional nos 10 dias úteis do desenho; consultas posteriores sob demanda, sem esforço adicional estimado |',
              '| Backend | Serviços, APIs, persistência, eventos, autorização, validação e implantação | Cada desenvolvedor executa uma atividade por vez, durante todo o cenário |',
              '| Frontend | Telas da mesa, experiência do cliente, upload e consumo das APIs | 1 desenvolvedor; uma atividade por vez |',
              '| ITLead | Planejamento, gestão, dependências, riscos e acompanhamento das entregas | 1 profissional com reserva estimada de 20% ao longo de todo o cenário; não executa desenvolvimento |',
              '| QA | Carga, resiliência, testes integrados e homologação | 1 profissional disponível nas janelas indicadas; uma atividade por vez |', '',
              '- M1 é o início relativo de cada cenário. Mês = 20 dias úteis; semana = 5 dias úteis. Datas de início, férias e feriados ainda não foram informados.',
              '- O cenário documental pressupõe a base FIDC pronta. Seus pré-requisitos F3 ficam registrados nas tabelas. As duas linhas do tempo não representam execução simultânea pelas mesmas pessoas.',
              '- O esforço das entregas foi preservado: 145 dias úteis na base e 81 na extensão. Atividades mistas foram divididas entre Backend e Frontend, com o mesmo esforço total. Os sufixos B, F e Q identificam essas partes; as divisões são estimativas de planejamento.',
              '- QA assume os testes transversais e a homologação. Testes unitários, revisão e correções da própria entrega permanecem no esforço do desenvolvedor; não foi criada uma etapa QA adicional para cada story.',
              '- A barra de ITLead cobre todo o período, com dedicação de 20%; sua extensão visual não significa dedicação integral. O esforço de gestão é mostrado separadamente e não está nos 145/81 dias originais.',
              '- Provisionamento e operação técnica são atribuídos ao Backend neste modelo de cinco perfis, pressupondo acesso e capacidade para infraestrutura. Esperas por uma equipe de plataforma ou pelo parceiro não estão estimadas.',
              '- As APIs precedem as telas correspondentes. Cada profissional tem agenda própria; não há sobreposição de atividades na mesma pessoa. A escolha prioriza o início possível e, em empate, o maior caminho restante de dependências. O resultado não é uma promessa de prazo mínimo.',
              '- Mais desenvolvedores não dividem automaticamente o prazo: dependências, um Frontend e um QA podem limitar o ganho. Comparações assumem igual produtividade, sem prazo adicional de onboarding.', '',
              '## Comparação de prazos', '',
              '| Cenário | Devs | Composição | Prazo (du) | Implantação | Esforço das entregas (du) | Gestão ITLead (du equivalentes) |',
              '| --- | --- | --- | --- | --- | --- | --- |']
    for group in result['groups']:
        for p in group['plans']:
            lines.append(f"| {group['name']} | {p['developers']} | {p['backend']} Backend + 1 Frontend | {p['finish']} | {p['milestone']} | {p['delivery_effort']} | {p['lead_effort']:.1f} |")
    lines += ['', 'Os totais de pessoas não representam dedicação integral de todos durante todo o período. A carga de cada perfil aparece nas tabelas abaixo. Estes cenários substituem, para comparação de equipes, os prazos anteriores calculados por frentes de trabalho.', '']
    for group in result['groups']:
        lines += [f"## {group['name']}", '', f"![Comparação no tempo — {group['name']}](../diagramas/cronograma-{group['slug']}.png)", '']
        for p in group['plans']:
            n=p['developers']
            lines += [f'### {n} desenvolvedores — {p["backend"]} Backend + 1 Frontend', '',
                      f"[Abrir Gantt com todas as atividades e perfis](../diagramas/cronograma-{group['slug']}-{n}-devs.png)", '',
                      'Carga das entregas por perfil: ' + '; '.join(f'{k}: {v} du' for k,v in p['effort'].items()) + f". Gestão adicional: {p['lead_effort']:.1f} du equivalentes.", '',
                      '| ID | Atividade | Perfil / responsável | Duração (du) | Início (du) | Fim (du) | Depende de | Pré-requisito da base |',
                      '| --- | --- | --- | --- | --- | --- | --- | --- |']
            for x in p['items']:
                title=x['title'].replace('|','\\|')
                lines.append(f"| {x['id']} | {title} | {x['resource']} | {x['duration']} | {x['start']} | {x['end']} | {', '.join(x['deps']) or '—'} | {', '.join(x['prerequisites']) or '—'} |")
            lines += [f"| GESTAO | Gestão de riscos, dependências e entregas — 20% de dedicação | ITLead 1 | {p['lead_effort']:.1f} equivalentes | 1 | {p['finish']} | Transversal | — |", '']
    lines += ['## Fluxo documental e limites do cenário', '',
              'Analista pendencia a solicitação na PCRE-JULG → esteira registra motivo, documentos e prazo → parceiro avisa o cliente → canal autenticado obtém autorização temporária → cliente envia ao bucket privado → serviço valida e consolida documentos → esteira retoma a análise na fila única.', '',
              'A proposta comercial continua no parceiro. A pendência é vinculada ao protocolo FIDC. Envio parcial ou inválido mantém a pendência; apenas todos os documentos obrigatórios válidos permitem a retomada, uma única vez por versão ativa. Acesso aos documentos é autorizado e auditado. Eventos duplicados ou antigos não reabrem análises encerradas. Upload não aprova a solicitação nem libera pagamento.', '',
              'O callback entre parceiro e esteira mantém mTLS; o cliente usa o canal autenticado e não recebe credenciais do bucket. Regras de expiração, retenção, tipos de arquivo e nova execução da PDEC dependem dos spikes. O tempo de espera do cliente por documentos é operacional e não integra o prazo de desenvolvimento.', '',
              '## Fontes e reprodução', '',
              '- [Arquitetura da mesa FIDC](../diagramas/proposta-nova-mesa.svg)',
              '- [Backlog original e cronograma geral](cronograma-implementacao.md)',
              '- [Dados dos seis cenários de equipe](../modelos/cronogramas-equipes-fidc.json)', '',
              'Gerar: `python modelos/gerar_backlog_fidc.py` e `powershell -File modelos/renderizar_equipes_fidc.ps1`. O gerador valida conservação de esforço, dependências, durações e ausência de conflito por profissional.']
    (ROOT/'docs/cronograma-fidc-documentos.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({g['name']:{str(p['developers']):p['finish'] for p in g['plans']} for g in result['groups']},ensure_ascii=False))
    return result

if __name__ == '__main__':
    generate(json.loads((ROOT/'modelos/backlog-fidc-documentos.json').read_text(encoding='utf-8')))
