# Estrutura do projeto — Nova mesa FIDC

**Épico EP-01 — Disponibilizar a jornada de simulação e análise de crédito FIDC, da decisão automática à análise julgamental e ao tratamento de pendências documentais.**

Atualização: 12/11/2026. Todas as features abaixo pertencem ao mesmo épico. A organização é incremental: a Entrega 2 amplia as APIs da Entrega 1 com consulta de status e análise julgamental mínima; a Entrega 3 acrescenta pendências e troca de arquivos.

O recorte anteriormente chamado de **Entrega 0 passa a ser a Entrega 1**. Os caminhos dos arquivos anteriores foram preservados para manter os links existentes. A arquitetura de referência é [proposta-nova-mesa.json](../modelos/proposta-nova-mesa.json); esta tabela consolida seu recorte de APIs e a extensão documental do [backlog FIDC + documentos](../modelos/backlog-fidc-documentos.json).

## Entregas

| Entrega | Resultado esperado | Data-alvo | Limite de escopo |
| --- | --- | --- | --- |
| **1 — APIs** | Simulação síncrona, análise automática assíncrona e correlação entre ambas | **11/01/2027** | Sem API de status, mesa julgamental ou pendência documental |
| **2 — Status e análise julgamental mínima** | Consulta de andamento e operação mínima de análise manual na PCRE-JULG | A definir | Fila única FIDC, sem gestão avançada de filas e sem pendenciar ou trocar arquivos |
| **3 — Pendências e troca de arquivos** | Solicitação, envio, validação e consulta de documentos, com retomada da análise | A definir | Extensão da jornada de análise, sem geração de proposta, formalização ou pagamento |

## Features do épico EP-01

O projeto foi consolidado em **5 features**. A Entrega 1 possui apenas **API de simulação** e **API de análise de crédito assíncrona**. Correlação, retorno, segurança e confiabilidade são atividades dessas features.

| Entrega | ID | Feature | Escopo |
| --- | --- | --- | --- |
| 1 | FT-01 | API de simulação | Simulação síncrona, resultado na mesma chamada e identificador para correlação. |
| 1 | FT-02 | API de análise de crédito assíncrona | Aceite com protocolo, decisão automática, correlação com simulação e retorno posterior ao parceiro. |
| 2 | FT-03 | API de status | Consulta autorizada do andamento e resultado da análise, com correlação. |
| 2 | FT-04 | Análise julgamental mínima | Derivação, fila única FIDC na PCRE-JULG, consulta, decisão manual e consolidação do resultado. |
| 3 | FT-05 | Pendência documental e troca de arquivos | Pendenciar, notificar, enviar, validar, corrigir e consultar arquivos; concluir a pendência e retomar a análise. |

O [Excel do backlog completo](../outputs/nova-mesa-20261112/backlog-completo-nova-mesa.xlsx) contém **55 atividades únicas**: 27 na Entrega 1, 12 na Entrega 2 e 16 na Entrega 3. Inclui critérios de aceite, dependências, origem e campos editáveis de status, responsável e esforço.

Atividades compartilhadas indicam as duas features atendidas e aparecem uma única vez. Os identificadores F3 e D3 preservam a rastreabilidade dos 46 itens anteriores; os novos itens complementam o recorte. As dependências foram adaptadas às entregas. Esforço e alocação permanecem a definir.

O [one-page da Entrega 1](../output/pdf/one-page-entrega-1-nova-mesa.pdf) resume escopo, marcos, premissas e trade-offs. O [backlog em JSON](../modelos/backlog-entregas-nova-mesa.json) mantém a estrutura consolidada.

As referências E1 no material anterior são agrupamentos do recorte, não atividades adicionais para somar ao Excel.

## Trabalho técnico e validação por entrega

Contratos, arquitetura, infraestrutura, homologação e implantação são atividades de suporte às features do mesmo épico, não novos épicos.

| Entrega | Atividades necessárias | Referências |
| --- | --- | --- |
| 1 | Trabalhos preliminares; contratos e REF; desenho técnico, GCP, MySQL, acessos e CI/CD; testes integrados, carga e resiliência; runbook, implantação e rollback | E1-00 a E1-03, E1-09, E1-10; adaptar F3-01, F3-02, F3-05 a F3-08 e F3-12 a F3-15 |
| 2 | Contrato da API de status e regras da análise manual; extensão PCRE-JULG, eventos e permissões; homologação da derivação até o retorno da decisão; operação e implantação | F3-04, F3-09; replanejar testes e operação F3-12 a F3-15 para as novas features |
| 3 | Regras e contratos documentais; arquitetura de estados e arquivos; armazenamento privado, acessos, retenção e quarentena; homologação de envio parcial, falhas e reanálise; implantação e rollback | D3-01 a D3-05, D3-15, D3-16 |

## Marcos e dependências

| Marco | Data / condição |
| --- | --- |
| Início dos trabalhos preliminares da equipe | **16/11/2026** |
| Definição dos contratos e REF de simulação e análise automática da Entrega 1 | **Até 20/11/2026** |
| Definição da arquitetura da Entrega 1 | **Até 24/11/2026** |
| Entrega 1 | **11/01/2027**, condicionada às definições e à capacidade realocada |
| Entrega 2 | Após a base das APIs; prazo a definir |
| Entrega 3 | Depende da mesa mínima e da base de integração; prazo a definir |

Na Entrega 1, a REF deve definir o tratamento dos casos sem decisão automática, pois a mesa ainda não estará disponível. Na Entrega 2, a análise julgamental mínima cobre receber, consultar e decidir; a ação de pendenciar e os fluxos de documentos entram na Entrega 3. Na Entrega 3, envio de arquivo não equivale a aprovação: a análise só é retomada quando os documentos obrigatórios da versão ativa estiverem válidos.

Os [trade-offs e a dependência da Serasa](entrega-0-nova-mesa.md#trade-offs-para-realocação) permanecem aplicáveis. **15/02/2027 é o prazo da migração da tela PTA → PCRE-JULG**, não uma data atribuída às Entregas 2 ou 3. As estimativas antigas do cenário completo precisam ser revistas para esta divisão; esta tabela não redefine o prazo das demais frentes.
