# Arquitetura ArchiMate

Projeto para organizar modelos e diagramas de arquitetura utilizando a notação ArchiMate.

## Estrutura

A [versão 3 do one-page executivo](output/pdf/one-page-executivo-entrega-1-v3.pdf) remodela a apresentação com entregáveis na faixa lateral, marcos em cronograma linear, janelas propostas e destaques para mTLS, modelagem com AD e trade-offs.

O [backlog completo separado por entrega](outputs/nova-mesa-20261112/backlog-projeto-por-entrega.xlsx) reúne um épico, cinco features e 55 atividades (28 stories, 10 spikes e 17 tasks), com resumo e abas próprias para as Entregas 1, 2 e 3.

A [versão 2 do one-page executivo](output/pdf/one-page-executivo-entrega-1-v2.pdf) apresenta o cronograma linear, os entregáveis das duas APIs e a ausência de análise manual na Entrega 1, com premissas e trade-offs em blocos visuais.

O [one-page executivo da Entrega 1](output/pdf/one-page-executivo-entrega-1.pdf) apresenta cronograma, premissas e trade-offs, incluindo a arquitetura definida até **24/11/2026** e a entrega em **11/01/2027**.

A [estrutura total da nova mesa FIDC](docs/estrutura-projeto-nova-mesa.md) organiza **um épico e 5 features em três entregas**: **1 — duas APIs; 2 — API de status e análise julgamental mínima; 3 — pendências documentais e troca de arquivos**. Materiais: [one-page da Entrega 1](output/pdf/one-page-entrega-1-nova-mesa.pdf) e [Excel com o backlog completo](outputs/nova-mesa-20261112/backlog-completo-nova-mesa.xlsx).

O recorte da **Entrega 1 da nova mesa FIDC** está em [escopo, backlog e trade-offs](docs/entrega-0-nova-mesa.md), com [diagrama próprio](diagramas/entrega-0-nova-mesa.svg): trabalhos preliminares em **16/11/2026**, contratos e REF até **20/11/2026** e entrega das APIs de simulação, análise automática e correlação em **11/01/2027**. API de status e mesa julgamental ficam para a segunda entrega. Para regenerar essa vista isoladamente, execute `python modelos/gerar_entrega_0.py`.

- `modelos/`: arquivos editáveis dos modelos de arquitetura.
- `diagramas/`: exportações dos diagramas, como SVG, PNG e PDF.
- `docs/`: contexto, requisitos e decisões de arquitetura.
- `referencias/`: materiais de apoio e convenções adotadas.
- `templates/`: roteiros reutilizáveis para documentar arquiteturas.

## Como começar

O botão **Restaurar desenho inicial** recupera o modelo original do cenário aberto e mantém os demais cenários. A restauração pode ser revertida com **Desfazer**. O editor e as exportações usam azul, branco, cinza e preto.

O botão com ícone de **expandir**, ao lado de **Ajustar**, coloca o editor em tela cheia. O ícone muda para **recolher** enquanto estiver ativo. Clique novamente ou pressione **Esc** para sair; as ferramentas de edição continuam disponíveis.

As ligações usam portas separadas nas caixas e roteamento automático que procura evitar sobreposição e passagem por componentes. Rótulos verticais acompanham a direção do trecho. Cruzamentos têm um pequeno intervalo branco para distinguir linhas que não se conectam. O cálculo é refeito ao mover elementos, inclusive em projetos já salvos.

No desenho, **Ctrl+C** copia o elemento selecionado, **Ctrl+V** cola uma cópia e **Ctrl+Z** desfaz a última alteração do cenário. Caixas e textos podem ser copiados entre cenários; ligações são coladas no cenário de origem, mantendo os componentes conectados. A cópia fica na memória do editor durante a sessão. Nos campos de texto, os atalhos continuam sendo os do navegador.

Para editar os quatro cenários de análise de propostas, abra **`abrir-desenhos.bat`** ou **`visualizador.html`** no navegador. O editor funciona offline e permite criar textos, caixas e ligações, mover elementos, detalhar tecnologias e marcar fluxos assíncronos com linha pontilhada. Use **Salvar projeto** para baixar o JSON editável e **Abrir projeto** para continuar a edição. Também oferece zoom, desfazer, exportação SVG e impressão PDF. O projeto inicial está em `modelos/arquitetura-credito.json`; as exportações estão em `diagramas/`.

1. Copie `templates/arquitetura.md` para `docs/` com o nome da arquitetura.
2. Registre objetivo, escopo, interessados e questões que os diagramas devem responder.
3. Crie o modelo em uma ferramenta com suporte a ArchiMate e salve o arquivo editável em `modelos/`.
4. Exporte as vistas relevantes para `diagramas/`.
5. Documente as decisões e mantenha as exportações alinhadas ao modelo.

## Convenções

- Use nomes de arquivos em minúsculas, sem acentos e separados por hífen.
- Mantenha o modelo editável como fonte dos diagramas exportados.
- Identifique a versão de ArchiMate e a ferramenta utilizadas na documentação de cada arquitetura.
- Utilize elementos e relacionamentos válidos da versão de ArchiMate escolhida.
- Não inclua credenciais ou informações sensíveis nos modelos.

Este projeto começa como um repositório de artefatos de arquitetura, sem aplicação ou modelo de domínio predefinido.
