# Arquitetura ArchiMate

Projeto para organizar modelos e diagramas de arquitetura utilizando a notação ArchiMate.

## Estrutura

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
