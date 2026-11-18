# Navegação inicial do SIAT

## Integração com o painel — 10/11/2026

Inicialização do operador: `Iniciar atendimento.cmd` usa o modo navegador real.
O painel monitora as abas existentes de SIAT e WhatsApp, inclusive em janelas
diferentes do navegador conectado. Não abre sites nem navegador ao iniciar e
não exige abrir os sistemas por links do painel. Os logins continuam manuais.
O verificador local identifica o navegador pela aba do painel e acessa seus controles pelo Windows, sem extensão. SIAT e WhatsApp devem estar nesse navegador; outras janelas do mesmo processo são aceitas.
Na consulta, traz o SIAT para frente; o operador aguarda sem usar mouse ou teclado.
Testes fictícios
permanecem separados da operação e não substituem a validação dos experimentos reais.

O worker de `atendimento/fluxo.py` usa `NavegadorDesktop` no modo navegador.
`recuperar_com_motor` compartilha a política de recuperação com o adaptador
Playwright e `consultar_com_recuperacao`, sem repetir os menus quando o
formulário está aberto. Os avisos aparecem no painel durante o login manual e a
consulta. A verificação de sessão também roda enquanto o worker está ocioso.

### Preparação de nova consulta — 12/11/2026

Depois de ativar a aba, `MotorDesktop.preparar_consulta` chama o comando Windows
`preparar_consulta` antes de `recuperar_com_motor`. Se o campo Inf. Adicionais estiver
visível, procura o controle clicável `close`/`Close`/`Fechar` nos ancestrais dessa
janela. Atualização: o span do X não funcionou no SIAT do operador. O novo alvo
é exclusivamente o botão **Fechar**, `id`/`name="frmVisualizar:j_idt98"`, cujo
`onclick` chama `dlgCadNotificacao.hide()` e AJAX PrimeFaces. Invoca o botão normal;
não executa o JavaScript fornecido nem chama AJAX diretamente.

Quando o ID é exportado pelo Windows, exige correspondência exata e nome Fechar.
Se não for exportado, exige botão Fechar único no contêiner do campo de retenção.
IDs divergentes são recusados. O X do cabeçalho é ignorado, inclusive quando ambos
os controles estiverem presentes. Não usa coordenadas de screenshot.

A busca não alcança o documento inteiro nem um ancestral que contenha Consultar.
Exige um único botão e confirma o desaparecimento dos detalhes e o retorno do
formulário. Não usa o link Sair. Sem detalhes, nenhuma ação de fechamento ocorre.
Login continua manual e recuperação de resultado vazio permanece na rotina existente.
Falha ou ambiguidade interrompe antes de preencher o próximo rastreio.
Observação de status e Novo atendimento não fecham detalhes: só o início de outra consulta.

O teste `tests.siat_desktop_dialog_check` passou com SIAT fictício, helper restrito
ao PID de teste, X presente, botão Fechar externo, duplicidade e pesquisa posterior.
Compilação e 16 testes do adaptador também passaram nesta troca de alvo. Não acessou
SIAT real; o botão Fechar ainda precisa ser confirmado pelo operador no sistema real.

Após publicar um resultado, inclusive retenção sem orientação, o worker pede retorno
à aba `Painel • MVP` capturada antes da ativação do SIAT. O helper verifica origem
local (`http://127.0.0.1:8000/` ou `http://localhost:8000/`, incluindo `/painel/`)
e identidade da aba. Se o Chrome omitir o esquema, interpreta endereço do painel
como HTTP. Reconhece também o título acrescido de informações de memória.
Quando o objeto acessível mudar, exige painel único na mesma janela de origem;
sem captura inicial, aceita apenas um painel único. Não cria abas nem janelas.
Só retorna se o SIAT continuar selecionado e em primeiro plano. Login manual e
consultas em andamento não acionam retorno. Erro de foco mantém o resultado.

A conexão normal pertence a `atendimento/desktop.py` e `native/`.
O helper é iniciado oculto, observa abas em janelas distintas e recebe comandos
por stdin, com prazo; na leitura final retorna somente a descrição do campo de retenção,
sem persistir dados do caso. Travamento do
helper encerra somente o subprocesso criado pelo MVP, sem encerrar o navegador.
Não preenche credenciais. Os adaptadores de extensão e CDP ficam fora do fluxo padrão.

A operação confirma o domínio pela barra de endereços e exige aba/janela corretas.
O rastreio segue ao campo do SIAT, sem banco ou logs. A atualização da consulta
exige mudança da identidade acessível do botão Consultar após a pesquisa; se essa
mudança não ocorrer, retorna demora, sem interpretar marcador de vazio antigo.
Os controles acessíveis e menus precisam ser confirmados no SIAT real.

`resultado.py` define o contrato da situação e classifica a descrição completa de
retenção por palavras-chave. O adaptador Windows lê `frmVisualizar:j_idt68`,
fornecido pelo autor em 11/11/2026. A implementação exige validação real dos
controles acessíveis e do carregamento dos detalhes. O segundo tipo de resultado
e a liberação continuam sem mapeamento. O antigo leitor Playwright não foi alterado.

O painel não escolhe orientação para resultado inconclusivo ou motivo desconhecido.
Se o resultado vazio persistir após a renovação da sessão, informa que a situação
da encomenda não pôde ser confirmada. Não declara ausência de pendência ou liberação.

Foi acrescentada uma verificação cooperativa de cancelamento e prazo às rotinas
existentes. Novo atendimento invalida o resultado antigo; enquanto uma ação do
navegador ainda está terminando, a próxima consulta permanece bloqueada.

Validação de ponta a ponta: `tests/operador_browser_check.py`, ligando HTTP, worker,
rotinas SIAT, catálogo temporário e colagem em página WhatsApp fictícia.
Os testes anteriores de navegação e recuperação continuam em `tests/siat_browser_check.py`.
Isso não comprova consulta real de contribuinte. Veja [README.md](README.md) para executar.

## Verificação real e aviso de login — 07/11/2026

A extensão do navegador permitiu executar o percurso no Brave. Na primeira
tentativa, Consultar Notificação redirecionou para a tela de login. Após novo
login manual do autor, o mesmo percurso abriu o formulário de consulta.
Depois, foi realizada uma consulta com texto fictício, sem abrir registro de contribuinte.
O formulário foi substituído por AJAX e exibiu **Nenhuma Notificação encontrada!**.
Essa execução foi pela extensão, não pelo processo Python do projeto.

## Recuperação de resultado vazio e acompanhamento da sessão

Segundo o operador, a mensagem de nenhuma notificação pode ocorrer mesmo com
rastreio correto. Ela não será usada para afirmar que a encomenda não tem registro.
O fluxo está em `src/apps/siat/recuperacao.py`, função `consultar_com_recuperacao`:

1. Verificar a tela atual. Se estiver no login, avisar e aguardar o operador.
2. Consultar; esperar a substituição do formulário `frmConsultar` observada no
   teste fictício. A mensagem vazia que já estava na tela não basta.
3. Se a nova resposta estiver vazia, clicar no link **Sair** e confirmar o login.
4. Avisar: **Faça login novamente no SIAT pelo navegador. A consulta será repetida após o login.**
5. Verificar a tela a cada 500 ms por até cinco minutos (prazo configurável).
   Reconhecer página inicial ou formulário com o link Sair; não basta mudar a URL.
6. Após o login, voltar à consulta se necessário e repetir o mesmo rastreio.
7. Se continuar vazio, pedir conferência manual. Há no máximo uma recuperação
   por chamada, para evitar um ciclo de saída e login.

`sessao.py` também oferece `monitorar_sessao`, que publica mudanças entre login,
início, consulta e tela desconhecida, inclusive durante a ociosidade. Deve rodar
no worker dono da página Playwright; não acessar a mesma Page em threads concorrentes.
Durante a consulta, o fluxo verifica a sessão entre as etapas e nas falhas.

O código de rastreio fica somente no argumento em memória e no campo do SIAT;
estas rotinas não o gravam em banco, arquivos ou logs. Não leem nem preenchem senhas.
O callback `avisar` entrega textos genéricos à futura interface do operador.
O painel Django agora recebe esses avisos e usa o monitor por meio do worker.
Testes locais com páginas fictícias validam o fluxo; a execução Python no SIAT real
permanece pendente.

```python
from apps.siat.recuperacao import consultar_com_recuperacao

# page será fornecida pela integração do navegador.
# exibir_aviso será fornecido pela interface do operador.
resultado = consultar_com_recuperacao(page, codigo, exibir_aviso)
```

O resultado sem a mensagem vazia apenas permite prosseguir para a futura leitura
da notificação; não classifica motivo de retenção nem confirma liberação.

## Rotinas individuais preservadas

A automação agora interrompe o fluxo ao detectar a rota de login observada,
antes das ações, após a entrada pelo menu e após o clique de pesquisa:

> O SIAT está na tela de login. Entre novamente no navegador e tente continuar.
> A automação foi interrompida.

Para formulário ausente ou ambíguo, orienta abrir Consultar Notificação e fazer
login se o SIAT solicitar. Não presume que toda tela diferente significa sessão
expirada. O aviso é uma exceção específica para a futura interface exibir;
o painel exibe o aviso recebido pelo worker. Nenhuma senha é coletada.

O retorno da navegação Python passa a exigir o formulário visível, em vez de
considerar somente o término do clique. Testes locais cobrem a rota de login e
redirecionamento após o menu, com todas as requisições interceptadas no teste.
Os detalhes abaixo conservam as hipóteses que ainda faltam validar no Python.

## Processos separados

1. **Entrada na área de consulta:** após o login manual, executar o caminho
   abaixo somente quando for necessário chegar à área principal de trabalho.
   Se a tela de consulta já estiver aberta, aproveitar essa tela.
2. **Consulta de cada encomenda:** usar a área já aberta para informar o rastreio
   e consultar o resultado. Para o próximo atendimento, preparar os campos para
   uma nova consulta sem refazer o caminho pelos menus. Preenchimento e clique
   programados a partir do terceiro print; leitura do resultado ainda pendente.

A entrada pelos menus não faz parte do ciclo de cada rastreio. Ela permanece
isolada em `navegacao.py`; preenchimento e pesquisa ficam em `consulta.py`,
verificação dos controles em `estado.py`. A recuperação fica em `recuperacao.py`
e a observação de sessão em `sessao.py`; o adaptador do atendimento fornece a Page a `service.py`.
O retorno à área de consulta só será necessário se o operador sair dela ou se
o estado observado exigir nova entrada. Se a sessão expirar, aguardar novo login manual.

O fluxo de recuperação reconhece a tela atual antes de decidir navegar.
Não usar apenas um indicador “já entrou” em memória: a página pode mudar ou a
sessão pode expirar. Há uma verificação inicial dos controles do formulário,
ainda sem validação pelo processo Python na página real. A rota de login é
reconhecida; telas diferentes de início, consulta e login interrompem o fluxo.

## Primeiro processo: entrada

Mapeamento de 07/11/2026, conforme os dois prints e a instrução do autor:

1. Trânsito.
2. Notificação Correios.
3. Consultar Notificação.

Apesar do círculo sobre “Emitir Notificação” no segundo print, a instrução do
autor é consultar. A rotina não contém ação de emissão.

Implementação: `src/apps/siat/navegacao.py`, função
`abrir_consulta_notificacao(page, timeout_ms=5000)`. Recebe uma `Page` do
Playwright já aberta no SIAT e autenticada manualmente. Não se conecta sozinha
ao Brave aberto, não copia perfis e não salva credenciais ou capturas.

```python
from apps.siat.navegacao import abrir_consulta_notificacao

# page: página autenticada, fornecida pela futura integração do navegador.
abrir_consulta_notificacao(page)
```

Os localizadores usam os textos exatos mostrados nos prints. Abrir os dois
menus por passagem do mouse é uma hipótese de implementação, ainda sem
validação no SIAT real. Não foram definidos seletores CSS, IDs ou URLs internas
sem evidência. Não há escolha automática da primeira opção em caso de duplicação.
Falhas interrompem a sequência com uma mensagem da etapa, sem conteúdo da página.

O retorno exige os controles do formulário visíveis após o clique. O terceiro
print mostra a tela de destino descrita a seguir. O painel aciona essas rotinas pelo worker.

## Segundo processo: pesquisar pelo rastreio

O terceiro print mostra o filtro **Cód. Rastreio**, um campo de texto ao lado,
o botão **Consultar** e a lista de notificações. Implementação:

```python
from apps.siat.consulta import pesquisar_rastreio

# Mesma página já aberta na área de consulta; código recebido no atendimento.
pesquisar_rastreio(page, codigo)
```

A rotina verifica se há um seletor, um campo de texto e um botão Consultar
visíveis e inequívocos. Seleciona **Cód. Rastreio**, substitui o conteúdo anterior
do campo e clica em **Consultar**. Não volta aos menus. Falhas interrompem a
execução sem repetição automática e sem incluir o rastreio na mensagem de erro.

Os papéis `combobox`, `textbox` e `button` e o rótulo da opção foram conferidos
na consulta fictícia pela extensão, assim como o ID do formulário e da tabela.
Ainda é necessário validar o fluxo completo pelo processo Python conectado ao SIAT.

A lista inicial exibe **Nenhuma notificação encontrada!**. Isso não comprova
uma pesquisa realizada: não interpretar essa mensagem nem linhas antigas após
o clique sem evidência de conclusão da nova pesquisa. A rotina não retorna
resultado fiscal. Um dos resultados foi descrito abaixo; a forma de aguardar
sua atualização é esperada pelo fluxo de recuperação descrito acima.
`service.consultar(identificador)` sem Page permanece indisponível; com Page,
reutiliza o fluxo de recuperação e encaminha para o leitor de resultado.
O leitor real responde com o limite explícito de mapeamento, sem simular sucesso.

## Terceiro processo: abrir a notificação encontrada

Mapeamento fornecido pelo autor por print com dados ocultados. Nenhum caso
real foi aberto pelo assistente nesta etapa, e a imagem não foi copiada para o projeto.

O autor informou duas possibilidades após pesquisar. Apenas a primeira foi
demonstrada: uma linha na tabela **Notificações**, identificada pelo autor como
o caso com carta de retenção. A linha apresenta as colunas Núm. Termo,
Cód. Rastreio, CPF/CNPJ, Nome, Data Emissão e Opções.

Para esse resultado, o próximo passo é clicar na **lupa verde da coluna Opções**
na linha correspondente ao rastreio pesquisado. Esse controle abre os detalhes
necessários para localizar o motivo de retenção, segundo o relato do autor.
Não confundir essa lupa com o botão **Consultar** ao lado do campo de pesquisa.

Antes desse clique, a implementação deverá confirmar a conclusão da pesquisa
atual e a correspondência da linha com o rastreio recebido. Não escolher a
primeira linha se houver múltiplas correspondências sem regra definida.
O motivo ainda não aparece neste print e não será deduzido dos dados da tabela.

Atualização em 11/11/2026: o autor forneceu a imagem da lupa e o trecho interno
`<span class="ui-button-text ui-c">ui-button</span>`. Esse span é genérico e não
identifica sozinho um botão. O caminho Windows agora inclui `AbrirDetalhes`,
chamado depois da consulta atualizada. Ele exige tabela acessível com cabeçalhos
`Cód. Rastreio` e `Opções`, uma única linha com o rastreio recebido e um único
botão habilitado com nome acessível `ui-button` na célula de opções dessa linha.
Não clica na primeira lupa da página nem em linhas duplicadas. A autorização de
clique pertence à aba e à pesquisa atual, expira em 30 segundos e é consumida
antes do acionamento. O rastreio fica somente em memória.

O retorno do comando de detalhes confirma somente o acionamento. O comando
separado de leitura abaixo exige o campo; não se infere situação fiscal pelo clique.
O autor forneceu em seguida o botão completo:
`id`/`name` = `frmConsultar:dTableNotificacao:0:j_idt47`, `title` = `ui-button`,
`role` = `button`, `aria-disabled` = `false` e ícone `ui-icon-zoomin`.
O `onclick` executa `dlgVisualizar.show()` e uma requisição PrimeFaces com
`update:'frmVisualizar'`. Portanto abre uma janela de detalhes dentro do SIAT;
não é um link para navegar diretamente. O programa invoca o botão, sem executar
o JavaScript copiado ou chamar a requisição interna por fora da interface.

Quando o Chrome expõe `AutomationId`, o mapeamento confere o padrão
`frmConsultar:dTableNotificacao:<índice>:j_idt47`. O índice não fica fixo em zero:
a linha continua sendo localizada pelo rastreio. Se o ID não for exposto, exige
o botão único `ui-button` na célula de opções da linha já confirmada. Um ID
exposto diferente interrompe a ação. O sufixo gerado `j_idt47` pode mudar numa
atualização do SIAT, caso em que o mapeamento precisará ser conferido novamente.
Se o SIAT não expuser esses padrões acessíveis, o painel pede conferência manual.
O teste nativo foi ampliado para alvo na segunda linha, botão fora da tabela,
resultado antigo, repetição e duplicidade; sua execução nesta alteração foi
recusada na autorização. Não houve validação dessa etapa em navegador real.

### Campo final de retenção — 11/11/2026

HTML fornecido pelo autor: `input#frmVisualizar:j_idt68`, nome igual ao ID,
`type="text"`, `readonly="true"`, `maxlength="250"`, rótulo **Inf. Adicionais:**.
O exemplo enviado contém `SIMEI`. A rotina `LerRetencao` usa o ID via UI Automation;
se o navegador não exportar o ID, exige Name ou LabeledBy com o rótulo exato.
Não procura por coordenadas nem lê os valores dos outros campos para adivinhar o alvo.

A leitura exige autorização transitória da lupa da pesquisa atual, mesma aba e
rastreio, campo único visível e readonly. Descarta identidades de campos anteriores
expostos antes do clique e aguarda valor não vazio estável por 800 ms dentro do prazo.
Essa estabilidade não comprova, sozinha, o fim do AJAX: validar no SIAT a substituição
acessível de `frmVisualizar`, inclusive detalhes anteriormente abertos e rede lenta.
Se o ID/rótulo não estiver disponível, permanece inconclusivo e solicita conferência.

O texto original é exibido integralmente no motivo do painel. A classificação
normaliza acentos e caixa e procura nomes explícitos: comercialização, SIMEI,
sem/ausência de nota fiscal, DIFAL/e-commerce/comércio eletrônico e irregularidade
fiscal/situação fiscal irregular. Múltiplas categorias ou negação não escolhem mensagem.
Sem correspondência ou sem orientação cadastrada, exibe a retenção com aviso de
orientação indisponível, sem transformar o caso em falha de consulta.

Validação desta alteração: compilação do helper e 61 testes locais aprovados com dados
fictícios, incluindo descrição com palavras extras, desconhecida, ambígua, vazia e
catálogo ausente. O teste nativo de navegador foi preparado para a leitura após a lupa,
mas não foi executado nesta alteração. Nenhum registro real foi aberto.

Validação local: `scripts/verificar.ps1 -ComNavegador` inclui um menu fictício
com submenus por hover, opção vizinha de emissão, menu ausente e opção duplicada.
Inclui formulário fictício para duas pesquisas consecutivas, substituição do
código anterior, filtro ausente, campos ambíguos e código vazio ou com espaços.
Esses testes não demonstram compatibilidade com o DOM real nem sessão válida.
Nenhuma operação no SIAT real é executada pelos testes.

Referência técnica: [localizadores Playwright](https://playwright.dev/python/docs/locators).
Preenchimento e seleção: [ações Playwright](https://playwright.dev/python/docs/input).
