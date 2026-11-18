# MVP de atendimento — Posto Fiscal dos Correios

Protótipo do TCC de Pedro Augusto da Silva Figueiredo. O painel roda no próprio
computador e apoia a consulta de encomendas e a seleção de orientações para o
contribuinte. No WhatsApp, a **colagem é automática e o envio é manual**.

## Preparar o ambiente

Você precisa de **Windows 10 ou 11**, **Windows PowerShell** e **Python 3.12**.
No GitHub, escolha **Code → Download ZIP**, extraia o arquivo e abra o PowerShell
na pasta que contém `manage.py`. Se tiver o Git instalado, também pode clonar o repositório.

Rode uma vez, com acesso à internet:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\preparar.ps1
```

O script instala as dependências e o Chromium para a simulação, cria a configuração
local e prepara o catálogo de orientações. Para preparar somente o modo normal,
adicione `-SemNavegador` ao comando.

## Modo simulação — demonstração para a orientadora

Rode no PowerShell, na pasta do projeto:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\iniciar.ps1 -Modo simulacao
```

1. Abra o [painel local](http://127.0.0.1:8000/painel/) no navegador. A simulação abre
   uma janela Chromium com as páginas fictícias do SIAT e do WhatsApp. Use somente os
   códigos de teste abaixo. A demonstração dispensa contas institucionais.
2. Digite `TESTE-COM` e clique em **Consultar**. A situação será **Retida**, o motivo
   será **Comercialização** e a mensagem aparecerá identificada como simulação.
3. Para demonstrar a colagem, clique em **Colar no WhatsApp**. Durante os oito segundos
   de contagem, vá até o WhatsApp fictício e clique no campo vazio da mensagem. Ao final,
   o sistema cola a orientação. Para testar outro código, clique em **Novo atendimento**.

| Código fictício | Cenário |
| --- | --- |
| `TESTE-COM` | Comercialização com mensagem fictícia curta para captura |
| `TESTE-SIM`, `TESTE-DIF`, `TESTE-NF`, `TESTE-IRF` | SIMEI, e-commerce/DIFAL, sem nota fiscal e irregularidades fiscais |
| `TESTE-LOGIN` | Resultado vazio, saída e novo login; a consulta seguinte é confirmada |
| `TESTE-VAZIO` | Resultado vazio mesmo após o novo login |
| `TESTE-DESCONHECIDO` | Retenção confirmada com motivo não mapeado |
| `TESTE-LIBERADA` | Situação fictícia liberada, sem texto correspondente no catálogo |
| `TESTE-CONEXAO`, `TESTE-DEMORA` | Falha de conexão e demora simuladas |

Para `TESTE-LOGIN` e `TESTE-VAZIO`, clique em **Concluir login fictício** na aba do SIAT
quando o painel pedir novo login. Use `Ctrl+C` no PowerShell para encerrar o servidor
e a janela fictícia antes de trocar de modo.

## Modo normal — atendimento com os sistemas reais

1. Rode o comando abaixo ou execute `Iniciar atendimento.cmd` com dois cliques.
2. Abra o [painel local](http://127.0.0.1:8000/painel/), uma aba do SIAT Web e uma aba
   do WhatsApp Web no mesmo navegador. As abas podem ficar em janelas diferentes.
   Entre manualmente nos sistemas com os acessos institucionais autorizados.
3. Digite o código de rastreio no painel e clique em **Consultar**. Aguarde o resultado
   sem usar o mouse ou o teclado enquanto o sistema opera a interface do SIAT.
4. Confira a orientação. Se for utilizá-la, clique em **Colar no WhatsApp** e, durante
   a contagem, abra a conversa certa e clique no campo vazio. Depois da colagem,
   confira o destinatário e a mensagem e pressione **Enter** para enviar.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\iniciar.ps1 -Modo navegador
```

Se o SIAT pedir novo login, entre pelo navegador e aguarde a retomada da consulta.
Mantenha a janela desbloqueada e use o mesmo usuário do Windows para o servidor e
o navegador. Para trocar de modo, encerre o servidor atual com `Ctrl+C`.

## Conexão ao navegador de atendimento

O modo `navegador` usa **o verificador local do Windows**, integrado ao programa.
O operador abre o painel, SIAT e WhatsApp no navegador que escolheu e inicia o programa pelo atalho.
Não precisa de extensão, modo desenvolvedor, porta CDP ou perfil separado.
O detector identifica o processo pela aba visível do painel e seu endereço local;
não filtra marcas ou nomes de executáveis. Procura as abas nas janelas desse processo,
sem misturar sites abertos em outro navegador. Na primeira identificação, mantenha
o painel visível. Se o painel fechar, o vínculo é descartado.
A automação depende de controles acessíveis por UI Automation no Windows 10/11 e
Windows PowerShell 5.1/.NET Framework. Detectar o navegador não comprova compatibilidade
de todos os seus controles: quando não consegue identificá-los, pede conferência.
Não é necessário instalar outro pacote Python nem baixar outro navegador para operar.

Deixe uma aba de cada sistema, inclusive em janelas diferentes. O monitor não ativa
abas enquanto o operador trabalha. Ao clicar **Consultar**, o painel avisa para
aguardar sem usar mouse ou teclado e o programa traz o SIAT para frente. Se o Windows
recusar o foco ou a tela mudar, o programa interrompe com orientação de conferência.
O computador deve estar desbloqueado; os programas devem rodar no mesmo usuário,
sem iniciar o navegador como administrador. O login continua manual.

O script inicia somente o servidor e seu componente local, oculto, de acessibilidade.
Abra [o painel](http://127.0.0.1:8000/). Os adaptadores anteriores de extensão e CDP
permanecem como código de desenvolvimento; não são usados pela inicialização normal.

**Limite atual:** consulta, recuperação, lupa e leitura de `Inf. Adicionais` estão
ligadas ao painel no adaptador Windows. O campo fornecido pelo autor identifica o
motivo da retenção; campo vazio ou inacessível permanece inconclusivo. O segundo
tipo de resultado e a liberação ainda não foram mapeados. A compatibilidade real
da lupa, do campo acessível e do carregamento AJAX precisa ser validada.

Em 11/11/2026 foi acrescentado o acionamento da lupa antes dessa conferência:
exige uma resposta atualizada e uma única linha com o rastreio na tabela, buscando
o botão `ui-button` na coluna `Opções`. A identidade acessível é uma hipótese
baseada no HTML fornecido: `frmConsultar:dTableNotificacao:<índice>:j_idt47`,
nome `ui-button`. O botão abre `dlgVisualizar` e atualiza `frmVisualizar`.
O ID, quando exposto pelo Chrome, é conferido com índice variável.
O acionamento não comprova o carregamento dos detalhes.
O teste nativo ampliado desta etapa não foi executado porque a autorização foi recusada.

O leitor busca `frmVisualizar:j_idt68` ou, quando o Chrome não exporta o ID,
um campo com vínculo acessível explícito ao rótulo `Inf. Adicionais:`. Exige campo
único, visível e somente leitura. Preserva o texto completo, limitado aos 250 caracteres
do campo. Palavras-chave selecionam as cinco categorias sem exigir igualdade do texto.
Descrição desconhecida, ambígua ou orientação ausente mantém a retenção visível,
sem inventar mensagem. Os dados do caso permanecem em memória, sem gravação no catálogo.

A colagem usa o campo editável que o operador focalizou, com nome acessível
"Digite uma mensagem"/"Type a message"/"Mensagem", dentro do documento WhatsApp.
Confirma a aba selecionada, a janela ativa e o domínio antes de inserir texto.
Recusa campo ocupado. Usa área de transferência temporária e Ctrl+V, sem Enter.
Solicita exclusão do histórico/sincronização de clipboard do Windows e limpa a
cópia se ela não tiver sido substituída por outra. O conteúdo anteriormente copiado
é substituído. O controle real do WhatsApp ainda precisa de validação institucional.
A leitura acessível do Chrome pode omitir parágrafos vazios; a confirmação compara
as linhas de texto e links. O operador confere também a formatação visual antes de enviar.

A colagem recebe a mensagem integral selecionada do catálogo, incluindo os links;
não usa o código de rastreio como texto a enviar. No clique, o navegador copia
exatamente o valor da caixa de mensagem para a área de transferência; somente depois
de confirmar a cópia solicita a contagem de oito segundos ao servidor. A cópia não
altera links, emojis ou parágrafos. Se ela falhar, não inicia a colagem e mostra o erro
junto ao botão. O operador abre a conversa e clica no campo, sem precisar usar Ctrl+V.
Ao final da contagem, o helper Windows confere o campo e cola automaticamente a mesma
mensagem. Aceita foco em um descendente do
campo de mensagem reconhecido. O rótulo pode começar com `Digite uma mensagem` ou
`Type a message` e conter um complemento separado por espaço ou dois-pontos;
o complemento não é registrado. Exige controle editável, no documento WhatsApp,
com foco e vazio. Envia Ctrl+V uma única vez e aguarda até três segundos
pela atualização do conteúdo antes de limpar a cópia temporária. Falhas anteriores
à inserção explicam campo não reconhecido, conteúdo já existente, tecla de atalho
pressionada ou clipboard ocupado e permitem nova tentativa pelo operador. Depois
do atalho, resultado incerto bloqueia repetição automática. A validação local cobre
o texto do banco até o transporte e preservação da mensagem nos erros; confirmar
o campo e a colagem na instalação real do WhatsApp ainda é necessário.

Em 12/11/2026, `tests.whatsapp_desktop_browser_check` validou a cadeia completa
em Chromium temporário: botão do painel, cópia da mensagem do catálogo, oito segundos,
campo WhatsApp fictício com `<p class="selectable-text copyable-text">`, colagem via
helper Windows, preservação integral do texto e links, um evento paste e zero Enter.
O helper ficou restrito ao PID de teste; não houve acesso a conversas reais nem ao SIAT.

Diagnóstico de 11/11/2026: o painel registrou `campo_sem_foco` com campo não
reconhecido. A inspeção técnica autorizada confirmou um controle Edit focado,
editável, com ValuePattern/TextPattern e rótulo começando em `Digite uma mensagem`
com complemento. A comparação exata foi substituída pelo prefixo delimitado.
`native/diagnosticar-campo.ps1` retorna somente prefixos fixos, tipos e padrões,
sem valores, nomes de contatos ou conteúdo de conversas. Não ativa abas nem cola.
`native/desktop.ps1 -VerificarCompilacao` testa também os rótulos positivos e
negativos sem acessar o navegador. O diagnóstico não realizou colagem real.

A leitura do catálogo respeita a última versão. Explicações ainda em rascunho ficam
visíveis para conferência, com aviso. A colagem manualmente solicitada é permitida
para texto disponível e vigente, mesmo em rascunho; envio continua manual.
Não promovemos textos a revisados nem reescrevemos mensagens. Sem nota fiscal não
recebe automaticamente a orientação de nota avulsa.

Quando uma categoria possui alternativas, a etapa 2 exibe o seletor **Mensagem 1,
Mensagem 2…**. Para sem nota fiscal, a primeira orienta obter e enviar a nota do
fornecedor; a segunda usa a última versão de `SAC-PEDIDO-NFA` já cadastrada.
O texto da segunda não é anexado automaticamente ao da primeira. A seleção troca
a mensagem completa, a versão e o aviso; o botão do WhatsApp copia e cola somente
a mensagem selecionada. Durante consulta ou contagem, a seleção fica bloqueada.
Tentativas de colagem são controladas por opção, sem permitir reenvio acidental
ao alternar de volta. Novo atendimento limpa opções, seleção e tentativas.

Ao concluir uma consulta, o worker publica o resultado e retorna à aba local
`Painel • MVP` de onde ela foi iniciada. Guarda a referência antes de ativar o SIAT;
se o foco já tiver mudado, aceita somente um painel único. Reconhece `/` e `/painel/`,
o endereço HTTP local sem esquema na barra do Chrome e o sufixo de memória no título.
Se o objeto acessível da aba mudar, aceita apenas um painel único na janela de origem.
Não abre abas. O retorno exige que o
SIAT ainda esteja em primeiro plano, para não interromper outra atividade do operador.
Falha de retorno preserva o resultado e orienta voltar ao painel manualmente.
Se o operador já voltou ao painel por conta própria, confirma sem trocar o foco.
Ao exibir um resultado concluído, a página posiciona e focaliza o título da etapa
2 depois de desenhar a mensagem, mesmo se o foco inicial estiver na barra de abas.
Só marca o atendimento como posicionado após conferir que o título está no viewport.
A rolagem ocorre uma vez por atendimento; o polling não interfere na leitura manual.
`tests.painel_resultado_browser_check` validou esse comportamento sem foco inicial,
com mensagem longa, rolagem manual posterior e um segundo atendimento.
`tests.retorno_painel_browser_check` passou em navegador temporário com as duas rotas,
título acrescido de memória e janelas separadas. A ativação de SIAT e retorno foram
executados pelo helper nativo restrito ao PID de teste; não consultou registros reais.
Ao iniciar outra consulta, o programa ativa o SIAT e fecha a janela de informações
anterior pelo botão **Fechar** (`frmVisualizar:j_idt98`), se ela estiver aberta.
Só depois segue para a consulta e recuperação
de sessão já existentes. O monitor e o botão Novo atendimento não fecham janelas;
o fechamento ocorre ao clicar em Consultar. Não usa Sair nem encerra a sessão para isso.
O motivo de bloqueio da colagem aparece junto ao botão (operação em andamento,
WhatsApp indisponível, orientação ausente ou fora da vigência, tentativa já realizada).

## O que está validado e o que falta

| Etapa | Validação atual | Limite real |
| --- | --- | --- |
| Painel, consulta única, andamento e Novo atendimento | Testes de servidor e navegador local | Uso individual, um processo |
| Seleção de rastreio, consulta, detecção de login e recuperação | Política compartilhada entre Playwright e Windows; teste nativo com páginas fictícias | Confirmar controles acessíveis e menus no SIAT real |
| Interpretação da situação e motivo | Classificação por palavras-chave, descrição integral e ausência de orientação testadas; leitor Windows compilado | Validar lupa, acesso ao campo Inf. Adicionais e atualização AJAX no navegador; mapear segundo resultado/liberação |
| Seleção e apresentação do catálogo | SQLite temporário nos testes; versão mais recente e links preservados | Revisão das explicações ainda pendente |
| Contagem e colagem sem Enter | Painel → worker → campo fictício; conteúdo integral e zero Enter verificados | Confirmar seletor e comportamento no WhatsApp institucional |
| Disponibilidade dos sistemas | UI Automation do Windows; estados separados; observação sem ativar abas | Árvore acessível do Chrome; título localizado não comprova autenticação |
| Envio/entrega da mensagem | Fora da automação | Operador confere e envia manualmente |

`tests.siat_desktop_dialog_check` validou no Windows, em navegador temporário:
detalhes abertos permanecem durante observação; preparação usa apenas seu botão Fechar;
uma segunda preparação com janela fechada não clica; a próxima consulta funciona;
botões duplicados impedem ação e o link Sair nunca é usado. O X do cabeçalho é
ignorado. O botão foi baseado no HTML completo enviado pelo autor; falta confirmar
essa etapa no SIAT real.

Não houve consulta de contribuinte, colagem em conversa real ou envio de mensagem
nessa validação. Simulação não é avaliação de desempenho real do atendimento.

## Implementação e dados

- `src/apps/atendimento/fluxo.py`: atendimento em memória, fila única, tokens de ação,
  cancelamento, prazo e descarte. Atualização da página acompanha a operação atual.
- `src/apps/atendimento/desktop.py`: adaptador Windows e transporte em memória.
- `native/Desktop.cs` e `native/desktop.ps1`: verificação e ações por UI Automation.
- `extensao/`, `ponte.py` e `extensao.py`: alternativa anterior preservada, fora do fluxo padrão.
- `navegador.py`: adaptador Playwright preservado para testes e desenvolvimento.
- `simulacao.py`: páginas fictícias e cenários, isolados da integração real.
- `src/apps/siat/`: consulta, sessão e recuperação existentes; `resultado.py` mantém
  o contrato de confirmação e o limite explícito do leitor real.
- `src/apps/catalogo/service.py`: leitura das versões atuais em thread separada do
  Playwright; não grava atendimentos nem muda revisões.
- `src/apps/whatsapp/colagem.py`: apenas insere texto no campo vazio e focado.
- `src/static/painel.js`: interface, polling e ações protegidas por CSRF.

Rastreio e resultado ficam em memória, fora de banco, logs, URLs e armazenamento
local do navegador do painel. Novo atendimento invalida o caso anterior imediatamente;
a consulta seguinte aguarda o worker anterior encerrar. Sem contato do painel por
15 minutos, os dados temporários são descartados. Reiniciar o servidor também limpa
o caso. Isso não apaga rastreios no SIAT ou mensagens já coladas no WhatsApp.

A espera por login é manual, até cinco minutos; há limite global de seis minutos
verificado entre etapas e durante a espera. Uma chamada de navegador já em curso
termina pelo timeout da etapa antes de liberar o próximo atendimento. O monitor
observa abas a cada três segundos, sem guardar senhas ou exportar conversas.

Execute somente um processo em loopback, sem autoreload, como no script fornecido.
Não usar vários workers WSGI: o bloqueio é por processo. Não habilitar DEBUG com dados reais.
Sem novas dependências; Python, Django, Playwright, SQLite e Ruff já existentes.

## Verificação

Validação desta troca: 51 testes de base passaram. Os 23 testes anteriores de
navegador passaram e o teste nativo Windows também passou após os ajustes.
`tests/desktop_browser_check.py` cria um Chromium temporário, restringe o helper
ao PID desse navegador e intercepta todas as páginas. Verifica janelas separadas,
ativação do SIAT, preenchimento, atualização da consulta, saída/login manual,
colagem de texto multilinha com link, zero Enter, recusa de campo ocupado e
detecção do fechamento do WhatsApp. Isso não confirma o DOM/acessibilidade dos
sites institucionais nem a execução em uma máquina Windows 10 de produção.

```powershell
.\scripts\verificar.ps1
.\scripts\verificar.ps1 -ComNavegador
```

O segundo comando inclui integração local entre painel, worker, recuperação, catálogo
e colagem. Capturas geradas pelos testes em `.local/validacao` contêm somente dados
fictícios. Não há capturas, traces, vídeos ou logs de páginas reais na aplicação.

Detalhes de escopo: [REQUISITOS.md](REQUISITOS.md), [SIAT.md](SIAT.md) e
[MENSAGENS.md](MENSAGENS.md).

Referências técnicas: [UI Automation nativa do Chrome](https://developer.chrome.com/blog/windows-uia-support-update),
[padrões de controles Windows](https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/ui-automation-control-patterns-for-clients)
e [formatos de histórico e sincronização de clipboard](https://learn.microsoft.com/en-gb/windows/desktop/dataxchg/clipboard-formats).
