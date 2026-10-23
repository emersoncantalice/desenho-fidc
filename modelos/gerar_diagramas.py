"""Fonte dos quatro cenários e geração do editor local (biblioteca padrão)."""
from pathlib import Path
import json
import subprocess
ROOT = Path(__file__).resolve().parents[1]

def node(id, x, y, title, detail='', w=270, h=94, kind='component'):
    return dict(id=id,x=x,y=y,w=w,h=h,title=title,detail=detail,kind=kind)
def link(id,a,b,label='',sa='right',ta='left',async_=False,via=None):
    return dict(id=id,source=a,target=b,label=label,sourceSide=sa,targetSide=ta,async_=async_,via=via)
def model(i):
    if i == 1:
        return ejb_proposal_model()
    if i == 2:
        return new_desk_model()
    if i == 3:
        return supermodern_model()
    modern=i==2
    m=dict(name=['AS IS','Proposta com EJB','Proposta modernizada'][i],width=1700,height=1340,nodes=[],edges=[])
    n=m['nodes'];e=m['edges']
    n.extend([
      node('heading',40,25,'ANÁLISE DE CRÉDITO',m['name']+'  /  Arquitetura de aplicações  /  22.10.2026',w=1600,h=80,kind='heading'),
      node('stage1',40,125,'01   ELEGIBILIDADE E SIMULAÇÃO','Fluxos de acesso à PDEC — comuns aos três cenários',w=1620,h=320,kind='group'),
      node('channels',70,200,'Canais / consumidores','Integração direta com a PDEC'),
      node('legacy',70,330,'Consumidores legados','Times que utilizam o GCRE'),
      node('gcre',520,330,'GCRE','On-premises | Integração legada'),
      node('pdec1',1170,200,'PDEC','GCP / Kubernetes (K8s)\nElegibilidade e simulação',w=430,h=110),
      node('stage2',40,475,'02   CAPTURA E ANÁLISE DA PROPOSTA','O canal solicita a captura dentro do EJB; o EJB solicita a decisão à PDEC.',w=1620,h=225,kind='group'),
      node('origin',70,555,'Canal','Solicitante da captura'),
      node('proposal',520,555,'EJB de crédito','Captura e persistência da proposta\nOn-premises | Java / EJB / JBoss',w=360),
      node('pdec2',1170,555,'PDEC','GCP / Kubernetes (K8s)\nPDD, score e rating',w=430),
      node('ops',40,1070,'04   PERSISTÊNCIA E OPERAÇÃO' if i else '03   PERSISTÊNCIA E OPERAÇÃO','PTA mantém o acesso ao Sybase durante a transição.',w=1620,h=210,kind='group'),
      node('db',520,1150,'Sybase','Proposta, resultados e status',w=300,kind='database'),
      node('pta',970,1150,'PTA','Leitura e registro da decisão'),
      node('human',1390,1150,'Mesa de crédito','Analista interno\nPowerApps: gestão das filas',w=240,kind='actor'),
      node('legend',40,1300,'','Linha contínua: chamada / dados     ·     Linha pontilhada: fluxo assíncrono     ·     PDEC repetida por etapa: mesmo serviço',w=1620,h=30,kind='text')
    ])
    e.extend([
      link('direct','channels','pdec1','Elegibilidade / simulação'),
      link('old','legacy','gcre','Requisição'),
      link('oldpdec','gcre','pdec1','Via GCRE','right','bottom'),
      link('entry','origin','proposal','Solicita captura'),
      link('decision','proposal','pdec2','Solicita decisão','right','left'),
      link('return','pdec2','proposal','Resultado da chamada','bottom','bottom',via=680),
      link('dbpta','db','pta','Consulta / gravação'),
      link('analysis','pta','human','Análise / decisão','right','left',True)
    ])
    if i:
      n.extend([
        node('integration',40,730,'03   ANÁLISE EXTERNA','Execução humana; solicitação e conclusão assíncronas.',w=1620,h=310,kind='group'),
        node('adapter',970,820,'Adaptador de provedores','GCP' if modern else 'Contrato e correlação\nHospedagem a definir'),
        node('external',1390,820,'Provedor externo','Interface de integração\nProtocolo a definir',w=240),
        node('externalhuman',1390,950,'Analista externo','Execução manual',w=240,h=70,kind='actor')
      ])
      if modern:
        n.append(node('kafka',520,820,'Confluent Kafka','Solicitações e resultados\nHospedagem a confirmar',w=360))
        e.extend([link('request','proposal','kafka','Publica / consome eventos','bottom','top',True),link('consume','kafka','adapter','Solicitação','right','left',True),link('publish','adapter','kafka','Resultado','bottom','bottom',True,via=970)])
      else:
        e.extend([link('request','proposal','adapter','Solicitação','bottom','left',True),link('result','adapter','proposal','Resultado posterior','bottom','left',True,via=1010)])
      e.extend([link('send','adapter','external','Solicitação','right','left',True),link('receive','external','adapter','Resultado','bottom','bottom',True,via=940),link('person','external','externalhuman','Análise humana','right','right',True,via=1645)])
    else:
      n.extend([node('notes',970,790,'OPERAÇÃO ATUAL','EJB solicita a decisão à PDEC.\nSem decisão automática: derivação à mesa.\nNão inclui o provedor externo.',w=620,h=150,kind='note')])
    if modern:
      n.append(node('persistence',70,920,'Adaptador de persistência','GCP | Acesso ao Sybase',w=300))
      e.extend([link('persist','proposal','persistence','Persistência','left','top',via=400),link('write','persistence','db','Grava proposta e resultados','bottom','left')])
    else:
      e.append(link('persist','proposal','db','Persistência da proposta','left','left',via=400))
    if i == 0:
      m['height']=1650
      next(item for item in n if item['id']=='legend')['y']=1600
      n.extend([
        node('downstream',40,1310,'04   STATUS, FORMALIZAÇÃO E PAGAMENTO','A fila MQ informa alterações de status; propostas aprovadas seguem para formalização e pagamento.',w=1620,h=250,kind='group'),
        node('statusnotification',70,1420,'Notificação de status','Status alterado da proposta\nComponente emissor a identificar',w=300,h=110),
        node('mq',520,1420,'Fila MQ','Mensagens de alteração\ndo status da proposta',w=300,h=110),
        node('formalization',970,1420,'Formalização','Recebe propostas aprovadas\nFluxo atual do legado',w=270,h=110),
        node('payment',1390,1420,'Pagamento','Continuidade após\na formalização',w=240,h=110)
      ])
      e.extend([
        link('notifystatus','statusnotification','mq','Status alterado','right','left',True),
        link('approvedformalization','mq','formalization','Aprovadas','right','left',True),
        link('formalizationpayment','formalization','payment','Prossegue')
      ])
    return m

def ejb_proposal_model():
    base=model(0)
    shared={'heading','stage1','channels','legacy','gcre','pdec1'}
    m=dict(name='Proposta com EJB',width=1700,height=2050,
           nodes=[n for n in base['nodes'] if n['id'] in shared],
           edges=[e for e in base['edges'] if e['id'] in {'direct','old','oldpdec'}])
    n=m['nodes'];e=m['edges']
    n[0]['detail']='Proposta com EJB  /  Alternativa de transição — não é o alvo recomendado  /  22.10.2026'
    n.extend([
      node('internalboundary',40,475,'CANAL INTERNO','Fora da estrutura de crédito',w=340,h=240,kind='group'),
      node('externalboundary',40,745,'CANAL EXTERNO','Fora da estrutura de crédito',w=340,h=880,kind='group'),
      node('creditboundary',440,475,'02   PROPOSTA · ESTRUTURA DE CRÉDITO','Captura no EJB, persistência, análise e controle de encaminhamento',w=1220,h=1150,kind='group'),
      node('origin',70,580,'Canal externo','Solicita a captura\nRecebe o retorno posteriormente',w=280,h=100),
      node('proposal',520,580,'EJB de crédito','Captura e persistência da proposta\nOn-premises | Java / EJB / JBoss',w=360,h=100),
      node('pdec2',1170,580,'PDEC','GCP / Kubernetes (K8s)\nPDD, score e rating',w=430,h=100),
      node('db',520,850,'Sybase','Proposta, origem interna / externa e status\nPersistência on-premises',w=360,h=110,kind='database'),
      node('pta',1030,850,'PTA','Proposta derivada\nConsulta e registra decisão',w=260,h=110),
      node('human',1390,850,'Mesa de crédito','Analista interno\nPowerApps: gestão das filas',w=240,h=110,kind='actor'),
      node('channelcontract',70,850,'Novo contrato assíncrono','Status em análise manual\nResultado após conclusão\nMecanismo de retorno a definir',w=280,h=130,kind='note'),
      node('statusrule',520,1150,'Controle de encaminhamento','Proposta de canal externo\nNÃO ENCAMINHAR AO PAGAMENTO INTERNO\nBloquear também a formalização\nCódigo do status a definir',w=460,h=140),
      node('payment',1170,1150,'Formalização / pagamento','Origem externa: não encaminhar.\nCanal interno mantém seu fluxo\nexistente via MQ.',w=430,h=140,kind='note'),
      node('manualnote',520,1320,'','Análise manual realizada dentro do crédito. O canal externo não aguarda uma chamada aberta durante a análise humana.',w=1100,h=35,kind='text'),
      node('legacyrisk',40,1410,'LIMITAÇÕES DA ALTERNATIVA COM EJB','Mantém dependência de Java/EJB/JBoss, Sybase e acesso direto do PTA à base.\nLegado de manutenção extremamente complexa: ajustes têm alto esforço e risco de regressão.\nNo AS IS, a fila MQ informa alterações de status; propostas aprovadas seguem para formalização e pagamento.\nPara propostas externas, é necessário impedir esse encaminhamento sem afetar o fluxo interno existente.\nExige mapear e ajustar regras de status, publicação e consumo MQ; os pontos de bloqueio ainda precisam ser definidos.\nA validação deve cobrir aprovação automática/manual e reprocessamento de mensagens, além dos contratos legados.\nUso como transição. O alvo permanece a separação da captura e da análise, com comunicação por eventos.',w=1620,h=215,kind='note'),
      node('legendnew',40,1650,'AZUL · A DESENVOLVER','Novo contrato / nova regra funcional.\nNão implica um novo serviço independente.',w=500,h=95),
      node('legendadapt',600,1650,'AZUL CLARO · A ADAPTAR','Componentes existentes que precisam\nde mudanças para suportar esta proposta.',w=500,h=95),
      node('legendlegacy',1160,1650,'CINZA · LEGADO MANTIDO','Branco: componente existente / referência.\nClassificação de escopo proposta para revisão.',w=500,h=95),
      node('legend',40,1770,'','Pontilhado: interação assíncrona / retorno posterior. Contínuo: chamada / persistência. Origem externa: sem formalização / pagamento.',w=1620,h=30,kind='text')
    ])
    e.extend([
      link('entry','origin','proposal','Solicita captura'),
      link('decision','proposal','pdec2','Solicita decisão'),
      link('return','pdec2','proposal','Resultado automático','bottom','bottom',via=730),
      link('returnchannel','proposal','origin','Status / resultado posterior','bottom','bottom',True,via=790),
      link('persist','proposal','db','Grava proposta e status','bottom','top'),
      link('dbpta','db','pta','Proposta / status'),
      link('manualrequest','pta','human','Abre análise'),
      link('manualresult','human','pta','Decisão manual','bottom','bottom',True,via=1030),
      link('savemanual','pta','db','Persiste decisão','bottom','bottom',via=1070),
      link('readstatus','db','proposal','Lê status / resultado','left','left',via=475),
      link('enforcestatus','db','statusrule','Origem externa: bloqueio','bottom','top')
    ])
    # Reserva espaço para os canais em seções próprias, fora da estrutura de crédito.
    for item in n:
        if item['id'] not in shared and item['kind'] != 'group':
            item['y'] += 240
    for item in e:
        if item.get('via') is not None and item['id'] != 'readstatus':
            item['via'] += 240
    n.append(node('internalchannel',70,580,'Canal interno','Solicita captura da proposta\nFluxo interno existente',w=280,h=100))
    e.append(link('internalentry','internalchannel','proposal','Solicita captura','right','top'))
    for item in n:
        if item['id'] in {'channelcontract','statusrule','legendnew'}:
            item['change']='new'
        elif item['id'] in {'proposal','db','pta','legendadapt'}:
            item['change']='adapt'
        elif item['id'] in {'legacy','gcre','legendlegacy'}:
            item['change']='legacy'
        elif item['kind'] in {'component','actor','database','note'}:
            item['change']='existing'
    return m

def new_desk_model():
    # O objeto é a solicitação de análise de crédito: sem proposta e sem Building Block de Propostas.
    m=dict(name='Nova mesa — solicitações FIDC',width=1700,height=1560,nodes=[],edges=[])
    n=m['nodes'];e=m['edges']
    n.extend([
      node('heading',40,25,'ANÁLISE DE CRÉDITO','Nova mesa simplificada na PCRE-JULG | Argos / Solicitações de análise de crédito FIDC, sem proposta',w=1620,h=80,kind='heading'),
      node('outside',40,130,'PARCEIRO','Opção: entrada por API e callback, com mTLS',w=340,h=1130,kind='group'),
      node('inside',440,130,'ANÁLISE DE CRÉDITO · NOVA MESA FIDC','Esteira no GCP com persistência própria, integrada à PDEC e à mesa simplificada na PCRE-JULG | Argos.',w=1220,h=1130,kind='group'),
      node('channel',70,250,'Parceiro','Solicita análise de crédito FIDC\nRecebe protocolo de aceite\nCertificado de cliente (mTLS)',w=280,h=110),
      node('credit',520,250,'Esteira de análise','GCP | Recebe a solicitação de análise\nPersiste a análise e retorna ao parceiro\nAPI síncrona: aceite com protocolo',w=360,h=130),
      node('pdec',1170,250,'PDEC','GCP / Kubernetes (K8s)\nAnálise automática',w=430,h=110),
      node('mysql',520,530,'MySQL cloud','Base da esteira de análise\nSolicitação, estado e resultado da análise\nProtocolo e controle do retorno ao parceiro',w=360,h=130,kind='database'),
      node('kafka',1030,530,'Confluent Kafka','Solicitações e decisões de análise\nIntegração proposta por eventos',w=300,h=110),
      node('newdesk',1030,850,'PCRE-JULG | Argos · Mesa FIDC','Mesa simplificada\nFila única de solicitações FIDC\nDerivadas pela esteira de análise',w=300,h=130),
      node('human',1390,850,'Analista interno','Analisa solicitações FIDC\nRegistra a decisão',w=240,h=110,kind='actor'),
      node('deskaccess',1030,1090,'ESCOPO DA MESA SIMPLIFICADA','Exibe apenas solicitações de análise de crédito FIDC derivadas pela esteira.\nFila única, sem gestão de filas.\nSem propostas: o Building Block de Propostas não participa.',w=600,h=130,kind='note'),
      node('channelapi',70,530,'API do parceiro','Recebe resultado final\nProtocolo + ID da solicitação\nResponde à chamada síncrona\nExige mTLS',w=280,h=130),
      node('contract',70,850,'OPÇÃO API + CALLBACK','Entrada síncrona: protocolo\nApós conclusão: API do parceiro\nChamada síncrona com resposta\nCorrelação pelo protocolo\nmTLS nas duas chamadas',w=280,h=165),
      node('scope',40,1300,'ESCOPO DA TERCEIRA VISÃO','O objeto é a solicitação de análise de crédito FIDC, não a proposta. O Building Block de Propostas não participa deste fluxo.\nA própria esteira de análise persiste a solicitação e a análise no MySQL e, ao concluir, retorna o resultado ao parceiro.\nA mesa simplificada fica dentro da PCRE-JULG | Argos e exibe apenas solicitações FIDC derivadas, em fila única, sem gestão de filas.\nNenhum acesso ao Sybase, EJB ou PTA legado. O fluxo encerra na análise de crédito: não gera proposta, formalização ou pagamento.\nOpção de integração externa: entrada síncrona com protocolo; após a análise, chamada síncrona à API do parceiro. As duas chamadas exigem mTLS.',w=1620,h=165,kind='note'),
      node('legend',40,1500,'','Azul: a desenvolver / implantar. Branco: referência. Pontilhado: eventos / análise humana. Contínuo: API síncrona / resposta / persistência.',w=1620,h=40,kind='text')
    ])
    # A ordem das ligações define a posição das portas em cada lado das caixas.
    e.extend([
      link('entry','channel','credit','Solicitação (mTLS)'),
      link('returnchannel','credit','channel','Protocolo de aceite','left','right'),
      link('notifychannel','credit','channelapi','Resultado (mTLS)','left','right'),
      link('callbackresponse','channelapi','credit','Confirma recebimento','right','left'),
      link('decision','credit','pdec','Solicita decisão'),
      link('persist','credit','mysql','Persiste solicitação e análise','bottom','top'),
      link('result','pdec','credit','Resultado / derivação','bottom','bottom',via=420),
      link('derive','credit','kafka','Deriva análise manual','bottom','top',True,via=490),
      link('manualrequest','kafka','newdesk','Solicitações FIDC','bottom','top',True),
      link('manualresult','newdesk','kafka','Decisão manual','left','left',True,via=970),
      link('consolidate','kafka','credit','Consome decisão','bottom','right',True,via=730),
      link('humanrequest','newdesk','human','Análise'),
      link('humanresult','human','newdesk','Registra decisão','bottom','bottom',True,via=1030)
    ])
    for item in n:
        if item['id'] in {'credit','mysql','newdesk','contract'}:
            item['change']='new'
    return m

def supermodern_model():
    base=model(0)
    shared={'heading','stage1','channels','pdec1'}
    m=dict(name='Supermodernizado — análise por eventos',width=1700,height=1850,
           nodes=[n for n in base['nodes'] if n['id'] in shared],
           edges=[e for e in base['edges'] if e['id']=='direct'])
    n=m['nodes'];e=m['edges']
    n[0]['detail']='Supermodernizado  /  Proposta externa e análise por eventos  /  22.10.2026'
    n.extend([
      node('ownership',40,475,'02   CAPTURA SEPARADA → PROPOSTA PERSISTIDA → ANÁLISE','O canal solicita a captura; o componente persiste a proposta e só então publica o evento no Kafka.',w=1620,h=560,kind='group'),
      node('externalproposal',70,575,'Captura de propostas','Captura e persistência extraídas\ndo EJB de crédito',w=320,h=105),
      node('proposalstore',70,770,'Persistência da proposta','Sob responsabilidade da captura\nTecnologia não informada',w=320,h=100,kind='database'),
      node('kafka',550,575,'Confluent Kafka','Proposta persistida / resultado\nHospedagem a confirmar',w=300,h=105),
      node('credit',1110,575,'Serviço de análise de crédito','GCP | Consome e publica eventos\nOrquestra e registra a análise',w=460,h=105),
      node('mysql',1110,770,'MySQL cloud','Estado, indicadores e resultados da análise\nServiço gerenciado / versão a definir',w=460,h=100,kind='database'),
      node('processing',40,935,'03   ANÁLISE AUTOMÁTICA · CHAMADA SÍNCRONA','O serviço de análise chama diretamente a PDEC e aguarda o resultado. Não há Kafka nesta chamada.',w=1620,h=470,kind='group'),
      node('creditprocessing',70,1030,'Serviço de análise de crédito','GCP | Mesmo serviço da etapa 02\nCliente síncrono da PDEC',w=320,h=105),
      node('pdec2',550,1030,'PDEC','GCP / Kubernetes (K8s)\nPDD, score e rating',w=300,h=105),
      node('adapter',970,1240,'Adaptador de provedores','GCP | Eventos e correlação\nContrato externo a definir',w=300,h=105),
      node('external',1390,1240,'Análise externa','Provedor / analista humano\nExecução assíncrona',w=240,h=105,kind='actor'),
      node('humanstage',40,1435,'04   ANÁLISE MANUAL INTERNA','Interface da mesa integrada ao fluxo de eventos; evolução do PTA e do PowerApps a definir.',w=1620,h=215,kind='group'),
      node('kafkamanual',70,1520,'Confluent Kafka','Derivação / decisão manual',w=320),
      node('pta',550,1520,'Interface da mesa','Evolução do PTA a definir\nIntegração com eventos',w=300),
      node('human',1110,1520,'Mesa de crédito','Analista interno\nGestão das filas a definir',w=460,kind='actor'),
      node('legend',40,1680,'','Pontilhado: comunicação assíncrona por eventos / análise humana. Contínuo: acesso direto / persistência. PDEC, Kafka e análise repetidos: mesmos serviços.',w=1620,h=30,kind='text')
    ])
    e.extend([
      link('saveproposal','externalproposal','proposalstore','Persiste','bottom','top'),
      link('requestcredit','externalproposal','kafka','Proposta persistida','right','left',True),
      link('consumecredit','kafka','credit','Evento inicia análise / resultados','right','left',True),
      link('creditevents','credit','kafka','Publica processamento / resultado','bottom','bottom',True,via=730),
      link('notifyexternal','kafka','externalproposal','Resultado da análise','top','top',True,via=550),
      link('saveanalysis','credit','mysql','Persiste análise','bottom','top'),
      link('decision','creditprocessing','pdec2','Chamada síncrona','right','left'),
      link('decisionresult','pdec2','creditprocessing','Resultado síncrono','bottom','bottom',via=1180),
      link('externalrequest','kafkaprocess','adapter','Solicita análise externa','bottom','left',True),
      link('externalresult','adapter','kafkaprocess','Publica resultado externo','bottom','left',True,via=1380),
      link('send','adapter','external','Solicitação','right','left',True),
      link('receive','external','adapter','Resultado posterior','bottom','bottom',True,via=1380),
      link('manualrequest','kafkamanual','pta','Derivação','right','left',True),
      link('manualresult','pta','kafkamanual','Decisão manual','bottom','bottom',True,via=1630),
      link('manual','pta','human','Análise / decisão','right','left',True)
    ])
    # Reserva uma linha para o canal sem comprimir os fluxos de captura e análise.
    for item in n:
        if item['id'] not in shared and item['id'] != 'ownership':
            item['y'] += 130
    for item in e:
        if item.get('via') is not None:
            item['via'] += 130
    n.append(node('capturechannel',70,555,'Canal','Solicita captura da proposta',w=320,h=80))
    e.append(link('captureentry','capturechannel','externalproposal','Solicita captura','bottom','top'))
    # Alvo integralmente moderno: acesso direto e nova mesa, sem coexistência legada.
    removed={'adapter','external'}
    n[:]=[item for item in n if item['id'] not in removed]
    e[:]=[item for item in e if item['source'] not in removed and item['target'] not in removed]
    for item in n:
        if item['id']=='stage1':
            item['detail']='Canais acessam diretamente a PDEC no Kubernetes do GCP.'
        elif item['id']=='externalproposal':
            item['detail']='Componente independente\nCaptura e persistência da proposta'
        elif item['id']=='humanstage':
            item['detail']='Nova mesa interna, com interface e serviço próprios integrados aos eventos.'
        elif item['id']=='pta':
            item['id']='newdesk';item['title']='Nova mesa de crédito';item['detail']='GCP | Interface e serviço próprios\nFila e decisão manual por eventos'
        elif item['id']=='human':
            item['detail']='Analista interno\nGestão de filas na nova mesa'
        if item['id'] in {'externalproposal','credit','creditprocessing','mysql','newdesk'}:
            item['change']='new'
        elif item['id']=='pdec2':
            item['change']='existing'
    for item in e:
        if item['source']=='pta': item['source']='newdesk'
        if item['target']=='pta': item['target']='newdesk'
    n.append(node('modernrule',970,1370,'CONTROLE DA PROPOSTA EXTERNA','A análise não encaminha a proposta ao pagamento interno.\nStatus e resultado retornam ao responsável pela proposta.\nAzul: novo desenvolvimento. Branco: componente existente.',w=660,h=115,kind='note'))
    return m

models=[model(i) for i in range(4)]
names=['as-is','proposta-com-ejb','proposta-nova-mesa','proposta-modernizada-gcp']
(ROOT/'modelos'/'arquitetura-credito.json').write_text(json.dumps(dict(format='arquitetura-credito',version=1,models=models),ensure_ascii=False,indent=2),encoding='utf-8')
for name,m in zip(names,models):
    (ROOT/'modelos'/f'{name}.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
template=(ROOT/'modelos'/'editor.html').read_text(encoding='utf-8')
template=template.replace('__RENDERER__',(ROOT/'modelos'/'roteamento.js').read_text(encoding='utf-8')+'\n'+(ROOT/'modelos'/'renderizador.js').read_text(encoding='utf-8')).replace('__APP__',(ROOT/'modelos'/'editor.js').read_text(encoding='utf-8'))
(ROOT/'visualizador.html').write_text(template.replace('__MODELS__',json.dumps(models,ensure_ascii=False)),encoding='utf-8')
for name in names:
    subprocess.run(['node','-e',"const fs=require('fs');const {render}=require('./modelos/renderizador.js');fs.writeFileSync(process.argv[2],render(JSON.parse(fs.readFileSync(process.argv[1],'utf8'))));",str(ROOT/'modelos'/f'{name}.json'),str(ROOT/'diagramas'/f'{name}.svg')],cwd=ROOT,check=True)
print('Gerados: editor e quatro modelos JSON editáveis.')
