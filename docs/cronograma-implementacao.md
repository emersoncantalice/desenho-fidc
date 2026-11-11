# Cronograma de implementação dos cenários

Backlog e cronograma de implementação das propostas descritas em [Análise externa de propostas de crédito](analise-externa-de-propostas.md). A vista 1 (AS IS) é o estado atual e não tem itens de implementação. Atualização: 2026-11-10.

## Premissas

- **Início:** dia útil 1 do Mês 1. Cada cenário é planejado de forma independente, a partir do Mês 1, para permitir a comparação entre eles.
- **Tamanhos:** simples = 3 dias úteis, média = 5 e complexa = 10. A mesma escala vale para stories, spikes e tasks; o spike é um timebox. Duas atividades têm duração fixa: desenho de arquitetura, com 10 dias úteis, e provisionamento de recursos, com 4 dias úteis por item.
- **Desenho de arquitetura:** a frente de arquitetura desenha a solução nos dias úteis 1 a 10, em paralelo aos spikes, e incorpora as conclusões deles. Nenhuma story ou task começa antes do fim desse desenho. Se o desenho tiver de esperar o fim dos spikes, cada cenário atrasa cerca de 10 dias úteis.
- **Provisionamento:** ambientes no GCP e CI/CD, MySQL cloud, tópicos e ACLs do Kafka, terminação mTLS com certificados e a homologação integrada do legado. O modelo de dados fica no desenho de arquitetura e nas stories.
- **Calendário:** mês = 4 semanas = 20 dias úteis. O cronograma usa `M1·S1` para Mês 1, Semana 1, e `du` para dia útil. Ajuste feriados e férias ao converter para datas.
- **Frentes:** cada frente executa um item por vez; frentes diferentes trabalham em paralelo. A duração de um item inclui desenvolvimento, revisão e testes da própria entrega.
- **Sequência:** um item começa quando suas dependências terminam e a frente está livre. O cálculo prioriza, em cada passo, o item que pode começar mais cedo.
- **Pendências:** as pendências da análise que bloqueiam o desenvolvimento viraram spikes. Um spike que terminar sem decisão desloca os itens que dependem dele.
- **Tipos:** *Story* entrega comportamento verificável; *Spike* produz uma decisão ou um mapeamento; *Task* cobre desenho de arquitetura, provisionamento, migração, testes transversais e implantação.

## Resumo comparativo

| Cenário | Stories | Spikes | Tasks | Esforço (dias úteis) | Frentes | Go-live | Desativação do legado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Vista 2 — Proposta mantendo o EJB | 13 | 4 | 8 | 131 | 4 | M3·S2 (du 49) | — |
| Vista 3 — Mesa simplificada FIDC na PCRE-JULG \| Argos | 15 | 5 | 10 | 145 | 4 | M4·S1 (du 63) | — |
| Vista 4 — Supermodernizado: proposta externa e análise por eventos | 19 | 7 | 14 | 235 | 6 | M4·S2 (du 69) | M4·S4 (du 79) |

O esforço é a soma dos dias úteis de todos os itens. O prazo depende das frentes em paralelo e das dependências entre os itens.

## Vista 2 — Proposta mantendo o EJB

Alternativa de transição, não recomendada como alvo. O risco concentra-se no mapeamento do legado (E2-01): se o mapeamento revelar mais pontos de publicação e consumo na MQ, a frente de dados e encaminhamento atrasa e o go-live acompanha esse atraso.

**Frentes**

| Sigla | Frente |
| --- | --- |
| ARQ | Arquitetura (desenho da solução) |
| EJB | Legado EJB (captura, PDEC, contrato com o canal) |
| DAD | Sybase, MQ, encaminhamento e segurança do canal |
| PTA | PTA, PowerApps e qualidade |

**Marcos**

| Marco | Fim |
| --- | --- |
| Desenho de arquitetura concluído | M1·S2 (du 10) |
| Spikes concluídos (definições para desenvolver) | M1·S2 (du 10) |
| Teste ponta a ponta concluído | M3·S2 (du 46) |
| Go-live | M3·S2 (du 49) |

**Cronograma por semana** (█ = semana com o item em andamento)

```text
               M1   M2   M3
E2-01 SPK DAD  ██··│····│··  │
E2-02 SPK EJB  █···│····│··  │
E2-04 SPK PTA  █···│····│··  │
E2-05 TSK ARQ  ██··│····│··  │
E2-03 SPK EJB  ·█··│····│··  │
E2-06 TSK PTA  ··█·│····│··  │
E2-07 TSK DAD  ··█·│····│··  │
E2-13 STR EJB  ··█·│····│··  │
E2-08 TSK DAD  ··██│····│··  │
E2-09 TSK PTA  ··██│█···│··  │
E2-23 STR EJB  ···█│····│··  │
E2-17 STR DAD  ···█│██··│··  │
E2-14 STR EJB  ····│█···│··  │
E2-19 STR PTA  ····│██··│··  │
E2-15 STR EJB  ····│·█··│··  │
E2-18 STR DAD  ····│·██·│··  │
E2-16 STR EJB  ····│·██·│··  │
E2-20 STR PTA  ····│··██│··  │
E2-22 STR EJB  ····│··██│█·  │
E2-24 STR DAD  ····│··██│··  │
E2-21 STR PTA  ····│···█│··  │
E2-25 STR DAD  ····│···█│··  │
E2-11 TSK DAD  ····│···█│█·  │
E2-10 TSK PTA  ····│····│██  │
E2-12 TSK PTA  ····│····│·█  │
```

**Backlog**

| ID | Tipo | Item | Frente | Tamanho | Depende de | Dias úteis | Início | Fim |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E2-01 | Spike | Mapear regras de status e a publicação/consumo da MQ que encaminham à formalização e ao pagamento | DAD | Complexa (10) | — | 1–10 | M1·S1 | M1·S2 |
| E2-02 | Spike | Mapear tabelas e campos compartilhados no Sybase, concorrência e ownership de status | EJB | Média (5) | — | 1–5 | M1·S1 | M1·S1 |
| E2-03 | Spike | Avaliar o mecanismo de retorno ao canal externo: callback, eventos ou consulta de andamento | EJB | Média (5) | — | 6–10 | M1·S2 | M1·S2 |
| E2-04 | Spike | Levantar a suíte de regressão e os cenários críticos (aprovação automática/manual, reprocessamento) | PTA | Simples (3) | — | 1–3 | M1·S1 | M1·S1 |
| E2-05 | Task | Desenho de arquitetura da solução: componentes, integrações, dados, segurança e implantação | ARQ | Arquitetura (10) | — | 1–10 | M1·S1 | M1·S2 |
| E2-06 | Task | Provisionar a homologação integrada: JBoss, Sybase, MQ e acesso à PDEC no GCP | PTA | Provisionamento (4) | E2-05 | 11–14 | M1·S3 | M1·S3 |
| E2-07 | Task | Definir código de status, transições e ponto de validação do bloqueio (registro de decisão) | DAD | Simples (3) | E2-01, E2-02, E2-05 | 11–13 | M1·S3 | M1·S3 |
| E2-08 | Task | Alterar o Sybase: origem da proposta e novos status | DAD | Simples (3) | E2-07 | 14–16 | M1·S3 | M1·S4 |
| E2-09 | Task | Automatizar a regressão do fluxo interno: aprovação automática/manual e MQ | PTA | Complexa (10) | E2-04, E2-06 | 15–24 | M1·S3 | M2·S1 |
| E2-10 | Task | Teste integrado ponta a ponta com o canal externo | PTA | Média (5) | E2-09, E2-18, E2-20, E2-21, E2-22, E2-23, E2-24 | 42–46 | M3·S1 | M3·S2 |
| E2-11 | Task | Plano de implantação e rollback; atualizar desenhos e documentação | DAD | Simples (3) | E2-17 | 40–42 | M2·S4 | M3·S1 |
| E2-12 | Task | Homologação com o negócio e go-live | PTA | Simples (3) | E2-10, E2-11, E2-25 | 47–49 | M3·S2 | M3·S2 |
| E2-13 | Story | Canal externo solicita a captura ao EJB, com identificação de origem | EJB | Média (5) | E2-02, E2-05 | 11–15 | M1·S3 | M1·S3 |
| E2-14 | Story | Persistir a proposta externa com origem e status no Sybase | EJB | Média (5) | E2-08, E2-13 | 21–25 | M2·S1 | M2·S1 |
| E2-15 | Story | Aplicar a decisão da PDEC e enriquecer a proposta externa | EJB | Simples (3) | E2-14 | 26–28 | M2·S2 | M2·S2 |
| E2-16 | Story | Registrar a proposta externa derivada como em análise manual | EJB | Simples (3) | E2-07, E2-15 | 29–31 | M2·S2 | M2·S3 |
| E2-17 | Story | Bloquear o encaminhamento de propostas externas à formalização e ao pagamento | DAD | Complexa (10) | E2-08 | 17–26 | M1·S4 | M2·S2 |
| E2-18 | Story | Reprocessar mensagens da MQ sem liberar propostas externas | DAD | Média (5) | E2-17 | 27–31 | M2·S2 | M2·S3 |
| E2-19 | Story | PTA exibe a origem externa e o andamento da proposta | PTA | Média (5) | E2-08 | 25–29 | M2·S1 | M2·S2 |
| E2-20 | Story | PTA registra a decisão manual da proposta externa | PTA | Média (5) | E2-16, E2-19 | 32–36 | M2·S3 | M2·S4 |
| E2-21 | Story | PowerApps inclui as propostas externas nas filas da mesa | PTA | Simples (3) | E2-16 | 37–39 | M2·S4 | M2·S4 |
| E2-22 | Story | Disponibilizar status e resultado correlacionados ao canal externo (contrato assíncrono) | EJB | Complexa (10) | E2-03, E2-16 | 32–41 | M2·S3 | M3·S1 |
| E2-23 | Story | Tornar idempotente a solicitação de captura do canal externo | EJB | Média (5) | E2-13 | 16–20 | M1·S4 | M1·S4 |
| E2-24 | Story | Autenticar e autorizar o canal externo | DAD | Média (5) | E2-13 | 32–36 | M2·S3 | M2·S4 |
| E2-25 | Story | Auditar e monitorar as propostas de origem externa | DAD | Simples (3) | E2-14 | 37–39 | M2·S4 | M2·S4 |

## Vista 3 — Mesa simplificada FIDC na PCRE-JULG | Argos

Cenário novo, sem dependência do EJB, do Sybase ou do PTA. O caminho crítico passa pela esteira: contratos, entrada com protocolo, PDEC, derivação com outbox e consolidação da decisão manual. A frente de integração assume o callback ao parceiro e a auditoria para aliviar a esteira.

**Frentes**

| Sigla | Frente |
| --- | --- |
| ARQ | Arquitetura (desenho da solução) |
| EST | Esteira de análise (API, estados, PDEC, Kafka) |
| MESA | Mesa simplificada na PCRE-JULG \| Argos |
| INT | Plataforma, segurança e callback ao parceiro |

**Marcos**

| Marco | Fim |
| --- | --- |
| Desenho de arquitetura concluído | M1·S2 (du 10) |
| Spikes concluídos (definições para desenvolver) | M1·S2 (du 10) |
| Teste ponta a ponta concluído | M3·S4 (du 60) |
| Go-live | M4·S1 (du 63) |

**Cronograma por semana** (█ = semana com o item em andamento)

```text
               M1   M2   M3   M4
F3-01 SPK INT  █···│····│····│·   │
F3-02 SPK EST  █···│····│····│·   │
F3-04 SPK MESA █···│····│····│·   │
F3-06 TSK ARQ  ██··│····│····│·   │
F3-03 SPK INT  ·█··│····│····│·   │
F3-05 SPK EST  ·█··│····│····│·   │
F3-07 TSK INT  ··█·│····│····│·   │
F3-08 TSK INT  ··██│····│····│·   │
F3-16 STR EST  ··██│····│····│·   │
F3-09 TSK INT  ···█│█···│····│·   │
F3-17 STR EST  ···█│█···│····│·   │
F3-10 TSK INT  ····│██··│····│·   │
F3-18 STR EST  ····│██··│····│·   │
F3-22 STR MESA ····│██··│····│·   │
F3-11 TSK INT  ····│·█··│····│·   │
F3-19 STR EST  ····│·██·│····│·   │
F3-23 STR MESA ····│·██·│····│·   │
F3-30 STR INT  ····│·██·│····│·   │
F3-20 STR EST  ····│··██│█···│·   │
F3-24 STR MESA ····│··██│····│·   │
F3-28 STR INT  ····│··██│█···│·   │
F3-25 STR MESA ····│···█│····│·   │
F3-21 STR EST  ····│····│██··│·   │
F3-29 STR INT  ····│····│██··│·   │
F3-14 TSK INT  ····│····│·█··│·   │
F3-26 STR EST  ····│····│·██·│·   │
F3-27 STR EST  ····│····│··█·│·   │
F3-12 TSK INT  ····│····│···█│·   │
F3-13 TSK MESA ····│····│···█│·   │
F3-15 TSK MESA ····│····│····│█   │
```

**Backlog**

| ID | Tipo | Item | Frente | Tamanho | Depende de | Dias úteis | Início | Fim |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F3-01 | Spike | Definir runtime e região no GCP e o produto do MySQL cloud | INT | Média (5) | — | 1–5 | M1·S1 | M1·S1 |
| F3-02 | Spike | Definir contratos: API de entrada, identificação FIDC, API do parceiro e eventos | EST | Média (5) | — | 1–5 | M1·S1 | M1·S1 |
| F3-03 | Spike | Definir o mTLS: autoridade certificadora, emissão, rotação, revogação e vínculo ao parceiro | INT | Média (5) | — | 6–10 | M1·S2 | M1·S2 |
| F3-04 | Spike | Mapear os pontos de extensão da PCRE-JULG \| Argos para a mesa | MESA | Média (5) | — | 1–5 | M1·S1 | M1·S1 |
| F3-05 | Spike | Definir timeout, retentativas e tratamento de falhas do callback | EST | Simples (3) | F3-02 | 6–8 | M1·S2 | M1·S2 |
| F3-06 | Task | Desenho de arquitetura da solução: componentes, integrações, dados, segurança e implantação | ARQ | Arquitetura (10) | — | 1–10 | M1·S1 | M1·S2 |
| F3-07 | Task | Provisionar ambientes no GCP e pipeline de CI/CD da esteira | INT | Provisionamento (4) | F3-01, F3-06 | 11–14 | M1·S3 | M1·S3 |
| F3-08 | Task | Provisionar o MySQL cloud da esteira: instância, rede, usuários e backup | INT | Provisionamento (4) | F3-01, F3-06 | 15–18 | M1·S3 | M1·S4 |
| F3-09 | Task | Provisionar tópicos, schemas e ACLs no Confluent Kafka | INT | Provisionamento (4) | F3-02, F3-06 | 19–22 | M1·S4 | M2·S1 |
| F3-10 | Task | Provisionar a terminação mTLS na entrada e os certificados de homologação | INT | Provisionamento (4) | F3-03, F3-07 | 23–26 | M2·S1 | M2·S2 |
| F3-11 | Task | Observabilidade: logs, métricas, alertas e rastreio por protocolo | INT | Simples (3) | F3-07 | 27–29 | M2·S2 | M2·S2 |
| F3-12 | Task | Testes de carga e resiliência | INT | Média (5) | F3-27, F3-29 | 56–60 | M3·S4 | M3·S4 |
| F3-13 | Task | Teste ponta a ponta com o parceiro em homologação | MESA | Média (5) | F3-21, F3-25, F3-27, F3-29, F3-30 | 56–60 | M3·S4 | M3·S4 |
| F3-14 | Task | Plano de implantação, runbook e onboarding do parceiro | INT | Simples (3) | F3-11, F3-29 | 48–50 | M3·S2 | M3·S2 |
| F3-15 | Task | Homologação com o negócio e go-live | MESA | Simples (3) | F3-12, F3-13, F3-14 | 61–63 | M4·S1 | M4·S1 |
| F3-16 | Story | Receber a solicitação FIDC por API síncrona e validar o payload | EST | Média (5) | F3-02, F3-07 | 15–19 | M1·S3 | M1·S4 |
| F3-17 | Story | Persistir a solicitação e devolver o protocolo único de aceite | EST | Simples (3) | F3-08, F3-16 | 20–22 | M1·S4 | M2·S1 |
| F3-18 | Story | Controlar os estados: pendente, em análise, derivada, concluída, indisponível e reprocessada | EST | Média (5) | F3-17 | 23–27 | M2·S1 | M2·S2 |
| F3-19 | Story | Solicitar a decisão à PDEC e registrar o resultado automático | EST | Média (5) | F3-18 | 28–32 | M2·S2 | M2·S3 |
| F3-20 | Story | Publicar a derivação para a mesa no Kafka, com outbox | EST | Complexa (10) | F3-09, F3-19 | 33–42 | M2·S3 | M3·S1 |
| F3-21 | Story | Garantir idempotência: a mesma chave recupera o mesmo protocolo | EST | Média (5) | F3-17 | 43–47 | M3·S1 | M3·S2 |
| F3-22 | Story | Mesa consome as derivações e exibe a fila única FIDC | MESA | Média (5) | F3-04, F3-09 | 23–27 | M2·S1 | M2·S2 |
| F3-23 | Story | Mesa exibe os dados da solicitação e o resultado da PDEC | MESA | Média (5) | F3-22 | 28–32 | M2·S2 | M2·S3 |
| F3-24 | Story | Mesa registra a decisão manual e a publica no Kafka | MESA | Média (5) | F3-23 | 33–37 | M2·S3 | M2·S4 |
| F3-25 | Story | Controlar os perfis de acesso do analista na mesa | MESA | Simples (3) | F3-22 | 38–40 | M2·S4 | M2·S4 |
| F3-26 | Story | Esteira consome a decisão manual e consolida o resultado | EST | Média (5) | F3-20, F3-24 | 48–52 | M3·S2 | M3·S3 |
| F3-27 | Story | Impedir que resultado duplicado ou tardio sobrescreva decisão finalizada | EST | Simples (3) | F3-26 | 53–55 | M3·S3 | M3·S3 |
| F3-28 | Story | Notificar o resultado na API do parceiro, com mTLS | INT | Complexa (10) | F3-05, F3-10, F3-19 | 33–42 | M2·S3 | M3·S1 |
| F3-29 | Story | Registrar as tentativas e reprocessar as falhas do callback | INT | Média (5) | F3-28 | 43–47 | M3·S1 | M3·S2 |
| F3-30 | Story | Manter a trilha de auditoria da solicitação | INT | Simples (3) | F3-18 | 30–32 | M2·S2 | M2·S3 |

## Vista 4 — Supermodernizado: proposta externa e análise por eventos

Arquitetura alvo. É o cenário mais longo porque inclui a migração do histórico do Sybase, a convivência com o legado e a desativação de EJB, Sybase, PTA, PowerApps e GCRE. A desativação vem depois do go-live e não bloqueia a entrada em produção.

**Frentes**

| Sigla | Frente |
| --- | --- |
| ARQ | Arquitetura (desenho da solução) |
| CAPT | Captura de propostas |
| ANAL | Serviço de análise de crédito |
| MESA | Nova mesa de crédito (interface e serviço) |
| PLAT | Plataforma: GCP, Kafka, resiliência, observabilidade e testes |
| DAD | Dados, migração e desativação do legado |

**Marcos**

| Marco | Fim |
| --- | --- |
| Desenho de arquitetura concluído | M1·S2 (du 10) |
| Spikes concluídos (definições para desenvolver) | M1·S3 (du 13) |
| Teste ponta a ponta concluído | M4·S1 (du 64) |
| Go-live | M4·S2 (du 69) |
| Desativação do legado | M4·S4 (du 79) |

**Cronograma por semana** (█ = semana com o item em andamento)

```text
               M1   M2   M3   M4
M4-01 SPK PLAT █···│····│····│····│
M4-02 SPK ANAL ██··│····│····│····│
M4-03 SPK CAPT █···│····│····│····│
M4-04 SPK MESA █···│····│····│····│
M4-05 SPK DAD  ██··│····│····│····│
M4-08 TSK ARQ  ██··│····│····│····│
M4-07 SPK CAPT ·█··│····│····│····│
M4-06 SPK ANAL ··█·│····│····│····│
M4-09 TSK PLAT ··█·│····│····│····│
M4-11 TSK DAD  ··█·│····│····│····│
M4-10 TSK PLAT ··██│····│····│····│
M4-13 TSK DAD  ··██│█···│····│····│
M4-22 STR CAPT ··██│····│····│····│
M4-12 TSK PLAT ···█│█···│····│····│
M4-27 STR ANAL ···█│█···│····│····│
M4-32 STR MESA ···█│█···│····│····│
M4-23 STR CAPT ···█│█···│····│····│
M4-24 STR CAPT ····│███·│····│····│
M4-28 STR ANAL ····│███·│····│····│
M4-33 STR MESA ····│██··│····│····│
M4-34 STR MESA ····│·██·│····│····│
M4-14 TSK DAD  ····│··██│····│····│
M4-25 STR CAPT ····│··██│····│····│
M4-29 STR ANAL ····│··██│····│····│
M4-35 STR MESA ····│··██│····│····│
M4-18 TSK DAD  ····│···█│█···│····│
M4-26 STR CAPT ····│···█│█···│····│
M4-30 STR ANAL ····│···█│█···│····│
M4-36 STR MESA ····│···█│██··│····│
M4-15 TSK CAPT ····│····│██··│····│
M4-19 TSK DAD  ····│····│██··│····│
M4-31 STR ANAL ····│····│██··│····│
M4-39 STR PLAT ····│····│██··│····│
M4-38 STR ANAL ····│····│·██·│····│
M4-37 STR MESA ····│····│·██·│····│
M4-40 STR ANAL ····│····│··█·│····│
M4-16 TSK PLAT ····│····│··██│█···│
M4-17 TSK MESA ····│····│··██│█···│
M4-20 TSK MESA ····│····│····│██··│
M4-21 TSK DAD  ····│····│····│·███│
```

**Backlog**

| ID | Tipo | Item | Frente | Tamanho | Depende de | Dias úteis | Início | Fim |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M4-01 | Spike | Definir runtime e região no GCP, hospedagem do Confluent Kafka e produto do MySQL cloud | PLAT | Média (5) | — | 1–5 | M1·S1 | M1·S1 |
| M4-02 | Spike | Definir os eventos (proposta persistida, derivação, decisão, conclusão): chaves, ordenação, versão e idempotência | ANAL | Complexa (10) | — | 1–10 | M1·S1 | M1·S2 |
| M4-03 | Spike | Definir a tecnologia de persistência e o ciclo de vida da proposta na captura | CAPT | Média (5) | — | 1–5 | M1·S1 | M1·S1 |
| M4-04 | Spike | Levantar os requisitos de gestão de filas e a experiência da nova mesa | MESA | Média (5) | — | 1–5 | M1·S1 | M1·S1 |
| M4-05 | Spike | Definir a migração do Sybase, a convivência com o legado e a reconciliação | DAD | Complexa (10) | — | 1–10 | M1·S1 | M1·S2 |
| M4-06 | Spike | Definir a precedência entre resultado automático e decisão manual e o significado de “manter recusada” | ANAL | Simples (3) | — | 11–13 | M1·S3 | M1·S3 |
| M4-07 | Spike | Avaliar a migração dos consumidores legados do GCRE para o acesso direto à PDEC | CAPT | Simples (3) | — | 6–8 | M1·S2 | M1·S2 |
| M4-08 | Task | Desenho de arquitetura da solução: componentes, integrações, dados, segurança e implantação | ARQ | Arquitetura (10) | — | 1–10 | M1·S1 | M1·S2 |
| M4-09 | Task | Provisionar ambientes no GCP e pipelines de CI/CD | PLAT | Provisionamento (4) | M4-01, M4-08 | 11–14 | M1·S3 | M1·S3 |
| M4-10 | Task | Provisionar o Confluent Kafka: tópicos, schema registry e ACLs | PLAT | Provisionamento (4) | M4-01, M4-02, M4-08 | 15–18 | M1·S3 | M1·S4 |
| M4-11 | Task | Provisionar o MySQL cloud da análise: instância, rede, usuários e backup | DAD | Provisionamento (4) | M4-01, M4-08 | 11–14 | M1·S3 | M1·S3 |
| M4-12 | Task | Observabilidade: rastreio por correlação, métricas e alertas | PLAT | Média (5) | M4-09 | 19–23 | M1·S4 | M2·S1 |
| M4-13 | Task | Migrar o histórico de análise do Sybase para o MySQL (scripts e validação) | DAD | Complexa (10) | M4-05, M4-11 | 15–24 | M1·S3 | M2·S1 |
| M4-14 | Task | Reconciliar a proposta sob gestão externa com o histórico interno de análise | DAD | Média (5) | M4-13, M4-24 | 33–37 | M2·S3 | M2·S4 |
| M4-15 | Task | Apoiar a migração dos consumidores legados do GCRE para a PDEC | CAPT | Média (5) | M4-07, M4-26 | 43–47 | M3·S1 | M3·S2 |
| M4-16 | Task | Testes de carga, resiliência e reprocessamento de eventos | PLAT | Complexa (10) | M4-26, M4-39, M4-40 | 55–64 | M3·S3 | M4·S1 |
| M4-17 | Task | Teste ponta a ponta: canal, captura, análise, mesa e conclusão | MESA | Complexa (10) | M4-23, M4-26, M4-36, M4-37, M4-39, M4-40 | 55–64 | M3·S3 | M4·S1 |
| M4-18 | Task | Plano de cutover, convivência e rollback | DAD | Média (5) | M4-14 | 38–42 | M2·S4 | M3·S1 |
| M4-19 | Task | Ensaio da migração em homologação | DAD | Média (5) | M4-18 | 43–47 | M3·S1 | M3·S2 |
| M4-20 | Task | Homologação com o negócio e go-live | MESA | Média (5) | M4-12, M4-16, M4-17, M4-19 | 65–69 | M4·S1 | M4·S2 |
| M4-21 | Task | Desativar EJB, Sybase, PTA, PowerApps e GCRE (pós-go-live) | DAD | Complexa (10) | M4-15, M4-20 | 70–79 | M4·S2 | M4·S4 |
| M4-22 | Story | Canal solicita a captura da proposta ao novo componente | CAPT | Média (5) | M4-03, M4-09 | 15–19 | M1·S3 | M1·S4 |
| M4-23 | Story | Autenticar e autorizar os canais na captura | CAPT | Simples (3) | M4-22 | 20–22 | M1·S4 | M2·S1 |
| M4-24 | Story | Persistir a proposta e gerenciar o seu ciclo de vida | CAPT | Complexa (10) | M4-22 | 23–32 | M2·S1 | M2·S3 |
| M4-25 | Story | Publicar “Proposta persistida” no Kafka após gravar, com outbox | CAPT | Média (5) | M4-10, M4-24 | 33–37 | M2·S3 | M2·S4 |
| M4-26 | Story | Consumir a conclusão da análise e atualizar a proposta | CAPT | Média (5) | M4-25 | 38–42 | M2·S4 | M3·S1 |
| M4-27 | Story | Consumir “Proposta persistida” e registrar o andamento no MySQL de forma idempotente | ANAL | Média (5) | M4-02, M4-10, M4-11 | 19–23 | M1·S4 | M2·S1 |
| M4-28 | Story | Orquestrar as etapas da análise com máquina de estados | ANAL | Complexa (10) | M4-06, M4-27 | 24–33 | M2·S1 | M2·S3 |
| M4-29 | Story | Chamar a PDEC de forma síncrona e registrar PDD, score e rating | ANAL | Média (5) | M4-28 | 34–38 | M2·S3 | M2·S4 |
| M4-30 | Story | Publicar a conclusão da análise no Kafka, com outbox | ANAL | Média (5) | M4-29 | 39–43 | M2·S4 | M3·S1 |
| M4-31 | Story | Derivar a proposta para a nova mesa por evento | ANAL | Simples (3) | M4-29 | 44–46 | M3·S1 | M3·S2 |
| M4-32 | Story | Serviço da mesa consome as derivações e monta as filas | MESA | Média (5) | M4-04, M4-10 | 19–23 | M1·S4 | M2·S1 |
| M4-33 | Story | Interface lista as filas e as propostas do analista | MESA | Média (5) | M4-32 | 24–28 | M2·S1 | M2·S2 |
| M4-34 | Story | Interface de análise com os dados da proposta e o resultado da PDEC | MESA | Média (5) | M4-33 | 29–33 | M2·S2 | M2·S3 |
| M4-35 | Story | Registrar a decisão manual e publicar o evento | MESA | Média (5) | M4-34 | 34–38 | M2·S3 | M2·S4 |
| M4-36 | Story | Gestão de filas: atribuição, priorização e redistribuição | MESA | Complexa (10) | M4-32 | 39–48 | M2·S4 | M3·S2 |
| M4-37 | Story | Autenticar os analistas e controlar os perfis de acesso | MESA | Simples (3) | M4-33 | 49–51 | M3·S2 | M3·S3 |
| M4-38 | Story | Consumir a decisão manual e consolidar o resultado | ANAL | Média (5) | M4-31, M4-35 | 47–51 | M3·S2 | M3·S3 |
| M4-39 | Story | Tratar indisponibilidade técnica, reprocessamento e fila de falhas | PLAT | Média (5) | M4-30 | 44–48 | M3·S1 | M3·S2 |
| M4-40 | Story | Impedir que resultado duplicado ou tardio sobrescreva decisão finalizada | ANAL | Simples (3) | M4-38 | 52–54 | M3·S3 | M3·S3 |

## Riscos para o cronograma

| Risco | Cenários | Efeito |
| --- | --- | --- |
| Mapeamento do legado (status e MQ) revela mais pontos de bloqueio | Vista 2 | Atrasa o bloqueio à formalização e ao pagamento e a regressão. Pode exigir uma segunda rodada de mapeamento. |
| Runtime, região, hospedagem do Kafka ou produto do MySQL sem decisão no fim do spike | Vistas 3 e 4 | Bloqueia o provisionamento e todas as stories que dependem dele. |
| Contratos de eventos e APIs sem acordo entre os times | Vistas 3 e 4 | Atrasa a integração entre a esteira ou serviço de análise, a mesa e a captura. |
| Parceiro, canal externo ou time da PCRE-JULG \| Argos indisponível para integração | Vistas 2 e 3 | Desloca o teste ponta a ponta e o go-live. |
| Consumidores legados do GCRE sem prazo para migrar | Vista 4 | Adia a desativação do legado; não afeta o go-live. |

## Se as vistas 3 e 4 forem executadas juntas

Os spikes de runtime, região, Kafka e MySQL (F3-01 e M4-01), os contratos de eventos (F3-02 e M4-02), o provisionamento no GCP e a observabilidade podem ser compartilhados. Assim, as frentes de plataforma economizam parte do esforço, e a definição tomada na vista 3 já serve à vista 4.
