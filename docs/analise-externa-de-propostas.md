# Análise externa de propostas de crédito

## Objetivo e escopo

Comparar o fluxo atual e duas propostas de integração. O objeto analisado é a proposta de crédito, exceto na vista 3, em que o objeto é a solicitação de análise de crédito FIDC, sem proposta. No cenário final, um sistema externo ao domínio de crédito persiste e gerencia a proposta; a análise de crédito recebe a solicitação e devolve o resultado por eventos Kafka. Esse sistema é distinto do provedor de análise manual externa, que recebe apenas os dados necessários à sua avaliação.

A PDEC executa elegibilidade, simulação e decisão na proposta, calculando PDD, score e rating. Quando não decide, a análise segue para uma pessoa da mesa de crédito. No legado, o PTA apresenta a proposta e registra a decisão no Sybase; o PowerApps organiza as filas.

A PDEC tem deploy em Kubernetes (K8s) no GCP em todos os cenários. Em elegibilidade e simulação, os consumidores integram diretamente com a PDEC. Alguns times usam consumidores legados que acessam a PDEC pelo GCRE, on-premises. Na etapa de proposta legada, **o EJB inicia a chamada à PDEC**, que devolve o resultado. No cenário supermodernizado, a entrada e a conclusão da análise usam eventos, mas o serviço de análise acessa a PDEC de forma síncrona. As representações repetidas de PDEC, Kafka e serviço de análise são referências aos mesmos componentes, separadas por etapa.

## Desenhos e aplicativo

Abra [o editor](../visualizador.html) no navegador ou execute `abrir-desenhos.bat` na raiz. Funciona offline, sem instalação. Permite criar, mover e editar caixas, textos e ligações, identificar atores e bancos de dados, configurar linhas pontilhadas para comunicação assíncrona, desfazer alterações e exportar SVG ou PDF.

**Salvar projeto** exporta um JSON com os quatro cenários; **Abrir projeto** recupera esse arquivo com todos os elementos editáveis. O rascunho é salvo no navegador quando o armazenamento local está disponível. Exporte o JSON para manter uma cópia permanente. O arquivo [projeto inicial](../modelos/arquitetura-credito.json) também pode ser aberto no editor.

**Restaurar desenho inicial** restaura somente o cenário aberto para o modelo distribuído com esta versão do editor. Os outros cenários são preservados. A operação atualiza o rascunho local e pode ser revertida com **Desfazer**; arquivos JSON já exportados não são alterados.

Esta revisão abre o novo cenário final sem substituir o rascunho da versão anterior. Se houver um rascunho anterior neste navegador, o botão **Exportar rascunho anterior** permite recuperá-lo em JSON.

| Vista | Arquivo |
| --- | --- |
| AS IS | [Desenho atual](../diagramas/as-is.svg) |
| Proposta mantendo EJB | [Desenho com EJB](../diagramas/proposta-com-ejb.svg) |
| Nova mesa simplificada FIDC na PCRE-JULG \| Argos | [Esteira modernizada e nova mesa](../diagramas/proposta-nova-mesa.svg) |
| Supermodernizado: proposta externa e análise por eventos | [Desenho GCP / MySQL cloud](../diagramas/proposta-modernizada-gcp.svg) |

São vistas lógicas de componentes e fluxos, não modelos ArchiMate formais. Linhas pontilhadas indicam fluxos assíncronos. Os projetos editáveis usam JSON; SVG é o formato de exportação. `modelos/gerar_diagramas.py` gera os modelos iniciais e o aplicativo, com Python e Node.js. O editor não depende dessas ferramentas para funcionar. Atualização: 2026-10-23.

## Vista 1 — AS IS

A esteira legada é Java, com EJB em JBoss, on-premises. **O canal solicita a captura da proposta, e essa captura é executada dentro do EJB.** O EJB persiste a proposta no Sybase, solicita a decisão à PDEC, enriquece a proposta e altera seu status. O PTA acessa diretamente esse banco, apresentando a proposta derivada à mesa de crédito.

A análise manual é executada por uma pessoa e concluída posteriormente. A mesa aprova ou mantém a proposta recusada; o PTA registra a decisão e o novo status. O PowerApps auxilia na gestão de filas. Esta vista não inclui a integração externa proposta.

**Uma fila MQ informa as alterações de status da proposta. Propostas aprovadas seguem para formalização e, na sequência, pagamento.** Esse encaminhamento faz parte do fluxo atual do legado. O desenho representa a notificação e o caminho das aprovadas; o componente que publica na MQ e os consumidores envolvidos ainda precisam ser identificados.

## Vista 2 — Proposta mantendo o EJB

**Alternativa de transição, não recomendada como arquitetura alvo.** Mantém o acoplamento a Java/EJB/JBoss, ao Sybase e ao acesso direto do PTA à base. As mudanças de contrato e status exigem evolução e testes de regressão no legado; a integração externa não elimina essa dependência. O alvo continua sendo a separação da captura e da análise, com comunicação por eventos.

**Limitação adicional: legado de manutenção extremamente complexa.** Impedir que uma proposta externa aprovada siga para formalização e pagamento exige ajustar uma esteira existente de difícil manutenção. No AS IS, a mudança de status é informada pela fila MQ e as propostas aprovadas prosseguem nesse fluxo. A complexidade está em localizar e alterar as regras de status e os pontos relevantes de publicação e consumo de mensagens, preservando o comportamento das propostas internas. Isso aumenta o esforço e o risco de regressão; o ponto exato de bloqueio ainda depende do mapeamento do legado. A validação deve abranger aprovação automática e manual, reprocessamento de mensagens e continuidade do fluxo interno.

O desenho distingue o escopo de desenvolvimento, como classificação proposta para revisão:

- **Azul:** novo contrato de retorno assíncrono ao canal e nova regra de bloqueio à formalização e ao pagamento. São entregas funcionais; não representam, por si só, serviços independentes.
- **Azul claro:** adaptações no EJB, no Sybase (origem/status) e no PTA (exibição e registro do fluxo).
- **Cinza:** componentes legados mantidos, como GCRE e consumidores legados.
- **Branco:** componentes existentes ou referências de contexto.

No editor, o campo **Escopo / cor** permite alterar essa classificação. A cor é preservada ao salvar o projeto, copiar elementos e exportar SVG.

Mantém a esteira Java/EJB no JBoss on-premises e o Sybase. **Os canais interno e externo solicitam a captura ao mesmo EJB**, que captura e persiste a proposta e chama a PDEC no Kubernetes do GCP. Na etapa de proposta, os canais interno e externo ficam em seções próprias, ambas fora da estrutura de crédito. O canal interno mantém seu fluxo existente; a captura, a persistência e a análise permanecem na estrutura de crédito. A origem interna ou externa acompanha a proposta no Sybase.

**A análise manual é interna**, executada por uma pessoa da mesa de crédito usando o PTA; o PowerApps organiza as filas. Quando há derivação, a proposta é registrada como em análise manual. O PTA consulta a proposta e registra a decisão no Sybase. Nesta proposta com EJB, o participante externo é o canal, não um provedor de análise humana.

**Para o canal externo, o fluxo de análise manual é assíncrono**: o status e o resultado são disponibilizados posteriormente, sem manter a requisição aberta durante o trabalho humano. O EJB consulta o estado persistido e expõe o retorno correlacionado à proposta. Callback, eventos ou consulta de andamento são alternativas ainda não decididas para esse cenário; não se presume Kafka nesta integração legada.

**A proposta de origem externa deve ser marcada com origem/status que impeça o encaminhamento à formalização e ao pagamento interno.** O desenho apresenta a regra “NÃO ENCAMINHAR AO PAGAMENTO INTERNO” e explicita o bloqueio também à formalização, com código de status a definir. A marcação deve ser persistida no Sybase e respeitada pelo encaminhamento associado às mensagens de status da MQ. O fluxo externo termina no retorno ao canal: a conclusão ou aprovação da análise não implica liberar formalização ou pagamento interno. O canal interno mantém suas regras existentes de encaminhamento; esse bloqueio específico não se aplica à sua origem.

O estado de andamento da análise e a restrição à formalização e ao pagamento são informações distintas, mesmo que a implementação use um status composto. Definir o código, as transições e o ponto de validação do bloqueio. A existência de qualquer exceção ou liberação dependerá de uma regra explicitamente definida.

## Vista 3 — Mesa simplificada FIDC na PCRE-JULG | Argos

**Nesta vista, o objeto é a solicitação de análise de crédito FIDC, não a proposta.** O parceiro envia a solicitação à esteira modernizada de análise no GCP, que pede a decisão à PDEC, executada no Kubernetes do GCP. Nenhuma proposta é criada ou gravada, e o Building Block de Propostas não participa do fluxo.

**A própria esteira de análise persiste a solicitação e a análise** no MySQL cloud: dados recebidos, estado, resultado, protocolo e controle do retorno ao parceiro. Ao concluir a análise, a esteira devolve o resultado diretamente ao parceiro.

Quando necessária a análise humana, a solicitação segue para a **mesa simplificada dentro da PCRE-JULG | Argos**. Essa mesa exibe **somente as solicitações de análise de crédito FIDC derivadas pela esteira**. A mesa possui **uma única fila de solicitações FIDC, sem gestão de filas**; não prevê múltiplas filas ou ferramentas de administração de filas.

**A solicitação FIDC encerra seu fluxo na análise de crédito, inclusive quando aprovada.** A conclusão registra o resultado e o devolve ao parceiro; não há proposta, formalização ou pagamento. Encerrar o fluxo não significa excluir a solicitação persistida ou seu histórico.

Esse caminho não passa pelo EJB, não consulta nem grava no Sybase e não depende do PTA legado. A mesa na PCRE-JULG | Argos registra a decisão pela integração de serviço, sem acesso direto às bases. Confluent Kafka permanece como a proposta de integração interna para derivação e decisão manual; essa mensageria não representa gestão de filas da mesa. Os contratos da solicitação, a identificação de FIDC, as APIs e os eventos ainda precisam ser definidos.

As peças a desenvolver ou implantar estão em azul: a esteira de análise, seu MySQL cloud, a mesa simplificada dentro da PCRE-JULG | Argos e a opção de integração por API e callback. PDEC e Confluent Kafka são reutilizados, com as integrações necessárias à esteira.

### Opção de integração com o parceiro por API e callback

O desenho inclui uma opção para a entrada e a saída externas por **chamadas síncronas de API, com requisição e resposta**. A integração interna por eventos pode ser mantida. O parceiro envia a solicitação e aguarda o protocolo de aceite na resposta. Após a análise, a esteira faz uma nova chamada síncrona à API do parceiro, enviando a conclusão e aguardando a confirmação de recebimento.

**O acesso entre o parceiro e a esteira exige mTLS nas duas chamadas.** Na entrada, o parceiro apresenta seu certificado de cliente à API da esteira. No retorno, a API do parceiro exige mTLS e a esteira apresenta seu certificado. Uma chamada sem certificado válido é recusada antes de qualquer processamento.

1. O parceiro chama de forma síncrona a API de entrada da esteira com os dados da solicitação de análise de crédito FIDC e uma chave de idempotência, aguardando a resposta dessa chamada.
2. Após validar e persistir a solicitação no MySQL, a esteira devolve um **protocolo único de aceite** e o estado inicial. Esse retorno confirma o recebimento, sem aguardar a decisão automática ou a análise humana. Repetir a mesma solicitação com a mesma chave deve recuperar o mesmo protocolo.
3. A esteira executa a análise na PDEC e registra o andamento no MySQL, associado ao protocolo. Quando há derivação, a solicitação segue para a fila única da mesa simplificada na PCRE-JULG | Argos.
4. Ao finalizar a análise automática ou manual, a esteira persiste o resultado e registra de forma confiável a notificação pendente. Em seguida, **chama de forma síncrona a API do parceiro**, previamente cadastrada, com o protocolo, o identificador da solicitação, o identificador da notificação e o resultado final, aguardando sua resposta.
5. O parceiro confirma o recebimento na resposta da própria chamada. A esteira aguarda essa resposta até o timeout definido no contrato. A entrega deve tolerar tentativas repetidas: o parceiro trata notificações duplicadas de forma idempotente, e a esteira registra as tentativas e reapresenta falhas conforme uma política a definir. Uma falha no callback não reinicia a análise nem altera sua decisão.

O protocolo de aceite e a conclusão pertencem a chamadas distintas. A requisição inicial termina com o protocolo; a análise ocorre entre essa resposta e a chamada de conclusão. **No desenho, a entrada, a chamada à API do parceiro e suas respostas usam linhas contínuas**, indicando comunicação síncrona. A confirmação técnica do parceiro registra o recebimento do resultado. A solicitação continua encerrada na análise, sem gerar proposta, formalização ou pagamento.

Esta é uma opção de integração, com endpoints, contratos, prazos e política de retentativas ainda a definir. A autenticação usa mTLS; ainda falta definir a autoridade certificadora, a emissão, a rotação e a revogação dos certificados e a vinculação do certificado ao parceiro cadastrado. O controle técnico de entrega do callback é separado da fila única de trabalho da mesa.

## Vista 4 — Supermodernizado: somente componentes modernos

Esta é a arquitetura alvo integralmente moderna. O desenho não inclui EJB, JBoss, GCRE, Sybase, PTA legado ou PowerApps. Os canais acessam diretamente a PDEC; captura, análise, integração por eventos, persistência e nova mesa compõem o caminho moderno. A análise manual é executada por pessoas da nova mesa interna, sem provedor de análise manual no fluxo desta vista.

**A persistência da proposta sai do EJB de crédito**, junto com a captura, e passa ao componente separado de captura de propostas. O domínio de crédito deixa de gravar a proposta e recebe o evento **Proposta persistida** para iniciar a análise. Seu MySQL cloud armazena o estado e os resultados da análise, vinculados à proposta mantida pelo componente de captura.

A captura sai do EJB e se torna um **componente separado de captura de propostas**, externo ao domínio de análise de crédito. O canal solicita a captura a esse componente, responsável pela persistência e pelo ciclo de vida da proposta. Depois de persistir com sucesso, ele publica o evento **Proposta persistida** no Confluent Kafka, que inicia o fluxo de análise de crédito. O domínio de crédito opera no GCP, processa a análise com comunicação por eventos e usa **MySQL cloud no lugar do Sybase** para seus dados internos. Não há EJB nem persistência interna autoritativa da proposta nesse cenário.

Fluxo proposto:

1. O canal solicita a captura ao componente separado, que persiste a proposta em armazenamento sob sua responsabilidade, cuja tecnologia ainda não foi informada.
2. Após a persistência bem-sucedida, o componente publica **Proposta persistida** no Confluent Kafka, correlacionado à proposta. Trata-se de um evento que registra um fato já ocorrido; o nome técnico do tópico e o schema ainda serão definidos.
3. O serviço de análise de crédito consome o evento, registra o andamento no MySQL cloud e coordena as etapas de processamento por eventos.
4. O serviço de análise de crédito chama **diretamente e de forma síncrona a PDEC**, no Kubernetes do GCP, e aguarda sua resposta. Essa chamada e seu retorno são desenhados com linhas contínuas, sem passagem pelo Kafka. O protocolo e o contrato técnico ainda precisam ser definidos.
5. Quando necessária, a proposta é derivada por eventos à nova mesa interna; a conclusão da análise humana retorna ao mesmo fluxo de eventos.
6. O serviço consolida o resultado da análise no MySQL cloud e publica a conclusão no Kafka.
7. O sistema externo consome a conclusão e atualiza a proposta sob sua responsabilidade.

O MySQL mantém estado, indicadores e resultados da análise, vinculados à proposta externa. Eventuais snapshots dos dados recebidos para análise não tornam o domínio de crédito responsável pela proposta. Uma nova mesa, com interface e serviço próprios no GCP, substitui o caminho manual legado. Os detalhes de implementação da interface e da gestão de filas ainda precisam ser definidos.

A hospedagem do Confluent Kafka e o produto gerenciado do MySQL cloud ainda não foram especificados; não se presume Cloud SQL ou outro produto. O componente de captura troca eventos com o domínio de crédito. A nova mesa interna participa desse fluxo, sem acesso direto às bases. Linhas pontilhadas representam comunicação assíncrona; persistência local nos bancos permanece em linha contínua.

## Decisões e cuidados

| Tema | Diretriz |
| --- | --- |
| Infraestrutura legada | Java/EJB em JBoss, on-premises. |
| PDEC | Kubernetes (K8s) no GCP, em todos os cenários. |
| Acesso legado à PDEC | GCRE on-premises para os consumidores legados que o utilizam. |
| Etapa de proposta | Legado: EJB chama PDEC. Alvo final: sistema externo solicita análise por Kafka; processamento e conclusão por eventos. |
| Captura da proposta | Solicitada pelo canal. No legado, fica dentro do EJB; no alvo, é um componente separado que publica Proposta persistida após gravar a proposta. |
| Infraestrutura modernizada | Serviços no GCP; runtime dos demais serviços e região ainda a definir. |
| Mensageria modernizada | Confluent Kafka para entrada, processamento e conclusão da análise de crédito. |
| Análise manual | Pessoa da mesa interna; terceira e quarta visões usam nova mesa, com conclusão assíncrona para o canal. |
| Objeto de análise | A proposta existente, com correlação da solicitação e do resultado. Na visão 3, a solicitação de análise de crédito FIDC, sem proposta. |
| Acesso externo | Canal / captura / parceiro participa do contrato de integração. Nenhum acesso direto às bases internas. Na visão 3, entrada e retorno ao parceiro exigem mTLS. |
| Persistência da proposta | Componente separado de captura na visão 4; EJB de crédito / Sybase nos cenários legados. A visão 3 não tem proposta nem usa o Building Block de Propostas. |
| Persistência da análise | MySQL cloud no cenário final, substituindo o Sybase interno. Na visão 3, a própria esteira persiste a solicitação e a análise no MySQL cloud. |
| Mesa de crédito | PTA nas visões legadas; mesa simplificada dentro da PCRE-JULG \| Argos na visão 3; nova mesa com interface e serviço próprios na visão 4. |
| Escopo da mesa FIDC | Na visão 3, fila única, sem gestão de filas; somente solicitações FIDC derivadas pela esteira. |
| Encerramento da solicitação FIDC | Na visão 3, encerra na análise de crédito, inclusive quando aprovada; o resultado volta ao parceiro, sem proposta, formalização ou pagamento. |

Separar timeout de entrega técnica e prazo da análise humana. Definir idempotência, retentativas, fila de falhas, reprocessamento, auditoria e publicação confiável após persistência (por exemplo, outbox). Resultados duplicados ou tardios não podem sobrescrever uma decisão finalizada sem regra explícita.

Definir estados para solicitação pendente, concluída, indisponível e reprocessada. Falha técnica não equivale a recusa de crédito. Aplicar autenticação, autorização e proteção dos dados em trânsito nas interfaces.

## Pendências

- Definir provedores, tipos de análise, contrato e se a análise externa é obrigatória ou seletiva.
- Definir runtime dos demais serviços (Kubernetes da PDEC já confirmado), região no GCP, hospedagem do Confluent Kafka e produto/versão do MySQL cloud. Não assumir GKE, Cloud SQL ou versões de Java/JBoss sem confirmação.
- Definir contratos dos eventos: identificadores da proposta e da solicitação, versão dos dados, payload mínimo, chave de particionamento, ordenação, idempotência e resultado correlacionado. Definir publicação confiável após persistir a proposta externa e a análise interna.
- Definir mecanismo de retorno externo e prazos para análise humana, expiração e resultados tardios.
- Definir dados permitidos, base legal, retenção, região de processamento e requisitos contratuais com segurança, privacidade, jurídico e negócio.
- Definir o significado de “manter recusada” e a precedência entre resultado automático, externo e decisão manual.
- Nos cenários legados, confirmar tabelas e campos compartilhados no Sybase, concorrência e ownership de status. No alvo, planejar a migração dos dados internos de análise para MySQL e a desativação das dependências do Sybase.
- Confirmar se o PTA será preservado no longo prazo ou substituído por uma interface desacoplada.
- Definir a migração e a reconciliação entre a proposta sob gestão externa e o histórico interno de análise, preservando rastreabilidade.
