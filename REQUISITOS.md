# Requisitos e preparação do MVP

Atualização: 10/11/2026. Consolidação do escopo informado pelo autor e dos levantamentos lidos;
não representa aprovação institucional nem validação final de regras fiscais.
Os requisitos desejados são distintos da implementação presente.

## Fluxo do operador atualizado em 10/11/2026

A instrução atual substitui o planejamento anterior de envio automatizado:
**o MVP cola a orientação e o operador envia manualmente pelo WhatsApp.**
Não há seleção automática de conversa, leitura de destinatário ou tecla Enter automática.

Implementação presente:

- A inicialização abre somente o servidor web. O operador abre os sites quando
  desejar; o monitor acompanha abas já existentes, mesmo em janelas diferentes
  do navegador conectado. Não abrir sites nem impor a mesma janela.

- Uma tela local com situação observada dos dois sistemas, rastreio, andamento,
  resultado e mensagem completa. Avisos explicam o problema e a próxima ação.
- O verificador local usa a acessibilidade do Windows para identificar cada aba
  do Chrome, sem extensão ou CDP. Ao consultar, traz o SIAT para frente e orienta
  aguardar sem mouse/teclado. Observação passiva não altera o foco. Aba localizada
  não é apresentada como prova de login; o domínio é conferido antes das ações.
- Um worker coordena o componente Windows (ou as Pages Playwright nos testes). Consulta e colagem são serializadas;
  bloqueio no servidor e tokens descartáveis impedem concorrência e repetição por abas.
- Reutilização de `consulta.py`, `estado.py`, `sessao.py` e `recuperacao.py`.
  Ao iniciar uma nova pesquisa, usa Fechar (`frmVisualizar:j_idt98`) nos detalhes anteriores se
  estiverem abertos, confirma o retorno do formulário e prossegue. Não fecha detalhes
  durante monitoramento ou apenas ao limpar o atendimento, nem usa Sair para esse fim.
  Resultado vazio aciona uma saída, login manual e nova consulta; se continuar
  vazio, a situação fica **não confirmada**, nunca liberada ou sem pendência.
- Monitor observa as abas durante ociosidade e espera de login. Sem conexão,
  não afirma que o site está aberto ou autenticado. Telas desconhecidas pedem conferência.
- Leitura do catálogo usa a última versão, preserva os links e mostra revisão pendente.
  Categorias com alternativas mostram Mensagem 1, Mensagem 2… para escolha do operador.
  Em sem nota fiscal, a primeira é envio da nota do fornecedor e a segunda é o pedido
  de nota fiscal avulsa já cadastrado. Copiar/colar usa somente a mensagem selecionada.
  A escolha fica bloqueada durante operações; não grava dados do atendimento no banco.
  Rascunho não é promovido. Colagem exige orientação disponível e vigente, com
  conferência do operador; rascunhos mantêm aviso e não impedem a colagem manualmente
  solicitada. O envio continua exclusivamente manual, sem alteração da revisão no banco.
- Colagem: contagem de oito segundos, cancelamento e validação de campo vazio,
  visível e focado. O programa insere texto sem Enter. Uma falha incerta bloqueia
  repetição automática e orienta conferir o campo. A orientação permanece no painel.
- Novo atendimento limpa o caso e invalida ações antigas. Se há operação executando,
  a próxima aguarda seu término. Nenhum resultado tardio reaparece no novo caso.
- Consulta concluída retorna à aba local do painel que iniciou a operação, desde
  que o operador continue no SIAT. Falha de foco não apaga o resultado. O painel
  explica junto ao botão por que uma colagem estiver bloqueada.
- Dados somente em memória; encerramento/reinício ou 15 minutos sem contato do painel
  descartam o caso. A limpeza não apaga conteúdo já existente nos sistemas externos.
- Prazo global de seis minutos, verificado entre etapas e na espera de login;
  chamadas do navegador em curso encerram pelo timeout da etapa antes de liberar a fila.

O painel está ligado às rotinas Windows de consulta, lupa e leitura do campo
`Inf. Adicionais` (`frmVisualizar:j_idt68`, fornecido pelo autor). Exibe a descrição
completa e associa palavras-chave às categorias do catálogo. Sem correspondência,
com múltiplas categorias ou sem orientação disponível, mantém a retenção visível
e deixa a orientação manual. Campo vazio/inacessível permanece inconclusivo.
Rastreio e descrição não são gravados no banco ou em logs. Falta validar a lupa,
o campo acessível e a atualização AJAX no SIAT real; o segundo resultado/liberação
continua sem mapeamento. O campo de mensagem do WhatsApp também depende de validação real.

Os testes de ponta a ponta são fictícios, com requisições interceptadas, catálogo
temporário, login manual representado por botão e verificação de zero Enter.
Execução, cenários e limites atuais estão em [README.md](README.md).
As pendências de revisão e de validação real continuam abertas. As seções históricas
abaixo documentam a pesquisa, mas não reinstalam a regra antiga de envio automático.

## Objetivo e limites

Aplicação local para um servidor por vez, abrangendo as cinco categorias definidas pelo autor em
01/11/2026: comercialização, SIMEI, sem nota fiscal, e-commerce (DIFAL) e irregularidades fiscais.
A ordem de implementação
dos caminhos completos será definida após o mapeamento; o escopo deixou de ser uma única categoria.
O servidor informa o identificador, consulta as telas SIAT, recebe uma orientação revisada, confere
o destinatário e envia manualmente pelo WhatsApp Web após a colagem. O sistema apresenta o estado observado e exige
intervenção humana quando necessário. A pesquisa comparará duração, conclusão correta e falhas
das mesmas atividades com e sem apoio do sistema, sem pressupor ganho de tempo.

A orientação tem três partes: explicação geral da retenção, guia de abertura de protocolo no SAC
e guia de acompanhamento da solicitação. O contribuinte executa os passos no portal da SEFAZ.
As duas páginas indicadas pelo autor e o mapeamento parcial estão em
[ORIENTACAO_PORTAL.md](ORIENTACAO_PORTAL.md). Questões fiscais e de cálculo são tratadas pela SEFAZ;
o MVP não orienta qual tributo pagar ou qual documento fiscal emitir.

Fora do escopo: emissão de boletos, liberação de mercadorias, alteração de registros fiscais, decisões
tributárias, acesso direto ao banco SIAT, desenvolvimento/treinamento de IA, leitura automática de novas
conversas, automação do portal de atendimento e infraestrutura distribuída.
Correios permanece consulta manual, salvo necessidade demonstrada para a categoria escolhida.

## Cinco categorias: estudo legal inicial e decisões do autor

Pesquisa em 01/11/2026. E-commerce corresponde a DIFAL no atendimento do posto, conforme confirmação
do autor. SIMEI deve ser estudado quanto ao ICMS da operação, sem presumir pendência do DAS mensal.
Os nomes são categorias operacionais informadas pelo autor, não códigos oficiais já observados no SIAT.
Irregularidades fiscais foi acrescentada posteriormente pelo autor como a quinta categoria;
o estudo legal inicial abrangia as quatro primeiras. Sua explicação geral é provisória.

### Fontes e limites da verificação

Foram consultados a LC 87/1996 e a LC 123/2006 na Câmara, o texto original do Decreto estadual
21.866/2023 no Diário Oficial e informações oficiais dos Correios. O portal de legislação consolidada
da SEFAZ-PI retornou timeout. O texto original não comprova, sozinho, a redação vigente em novembro
de 2026: conferir alterações, efeitos temporais e aplicação ao posto antes de aprovar orientações.
Este estudo não estabelece alíquotas, multas, valores ou obrigação de pagamento para um caso concreto.

| Categoria | Base localizada | Entendimento de trabalho e ponto a confirmar |
| --- | --- | --- |
| Comercialização | LC 87/1996, art. 4º; RICMS-PI, Anexo VII, art. 81, alínea c, na publicação original | Habitualidade ou volume com intuito comercial podem caracterizar contribuinte. Confirmar se o rótulo do posto corresponde a destinatário não inscrito; não confundir automaticamente com antecipação parcial de empresa inscrita. |
| SIMEI | LC 123/2006, arts. 18-A e 13, § 1º, XIII; RICMS-PI, Anexo VII, art. 81, alínea b, na publicação original | O DAS não afasta todas as hipóteses de ICMS fora do regime unificado. A norma estadual citada contempla entrada destinada a MEI na cobrança por CVI; falta vincular o lançamento concreto e a regra vigente ao código SIAT. |
| Sem nota fiscal | RICMS-PI, art. 164, § 1º, I, alínea a, na publicação original; LC 87/1996, art. 11, I, b | Examinar falta ou irregularidade do documento exigível. Distinguir documento não localizado na consulta de ausência efetiva; conferir hipóteses legais de dispensa e documentação substitutiva aplicável. |
| E-commerce / DIFAL | LC 87/1996, art. 4º, § 2º, com alteração pela LC 190/2022; RICMS-PI, Anexo VII, art. 81, alínea d, na publicação original | No DIFAL a consumidor final não contribuinte, a regra geral atribui responsabilidade ao remetente. Conferir regime, operação, pagamento e motivo registrado; não atribuir automaticamente a dívida ao comprador. |
| Irregularidades fiscais | Categoria informada pelo autor; fundamento específico ainda não validado | Explicação geral de pendência fiscal relacionada à operação, sem atribuir responsável ou determinar sua natureza. Encaminhar ao SAC; mapear o código SIAT antes do uso real. |

O art. 81 citado está no regime de transportadoras conveniadas. Sua aplicação específica à operação
dos Correios e os procedimentos locais permanecem pendentes. As referências orientam a investigação;
o sistema não fará enquadramento tributário com base apenas nessas categorias.

Fontes consultadas:

- [LC 87/1996, texto atualizado na Câmara](https://www2.camara.leg.br/legin/fed/leicom/1996/leicomplementar-87-13-setembro-1996-370965-normaatualizada-pl.html).
- [LC 123/2006, texto atualizado na Câmara](https://www2.camara.leg.br/legin/fed/leicom/2006/leicomplementar-123-14-dezembro-2006-548099-normaatualizada-pl.html).
- [Decreto 21.866/2023, publicação original no DOE nº 47](https://www.diario.pi.gov.br/doe/files/diarios/anexo/5714d565-bd46-4f50-950d-7fa74dbdc549/DIARIO-OFICIAL-DO-ESTADO-DO-PIAUI-PUBLICACAO-N-47.pdf).
- [Portal oficial de legislação SEFAZ-PI, consolidação pendente de acesso](https://portaldalegislacao.sefaz.pi.gov.br/inicio).

### Documento fiscal e data da operação

Os Correios informaram adoção obrigatória da DC-e em 06/04/2026 para remessas que não exigem NF-e.
Em comunicado de 19/10/2026, anunciaram validação do CNPJ do remetente como contribuinte do ICMS
na emissão de DC-e a partir de **02/11/2026**, com bloqueio nas condições descritas no comunicado.
Como a mudança coincide com a preparação do piloto, conferir o documento exigível e a data de cada
cenário. Não transformar declaração de conteúdo em alternativa universal à nota fiscal.
Fontes: [aviso de abril](https://saladeimprensa.correios.com.br/arquivos/13666) e
[comunicado de outubro](https://www.correios.com.br/central-de-informacoes/boletim-aos-clientes/copy_of_comunicado-19-10-2026-carta-ajustes-nas-regras-fiscais-da-sefaz).

Também não redigir uma resposta universal de liberação condicionada ao pagamento. A Súmula 323 do STF
veda apreensão como meio coercitivo de cobrança de tributos; a situação concreta e a medida fiscal
competem à análise responsável, sem o MVP julgar sua legalidade ou determinar liberação.
[Referência oficial do STF](https://portal.stf.jus.br/jurisprudenciaRepercussao/verPronunciamento.asp?pronunciamento=5934091).

### Consequências para o desenvolvimento

- O levantamento em [REGULARIZACAO.md](REGULARIZACAO.md) é contexto jurídico histórico.
  A decisão posterior do autor limita o encaminhamento aos guias de abertura e acompanhamento
  manual no portal, conforme [ORIENTACAO_PORTAL.md](ORIENTACAO_PORTAL.md).
- O catálogo terá as cinco categorias; cada orientação deverá guardar fonte, dispositivo, data de revisão,
  vigência aplicável, responsável pela revisão e estado rascunho/revisado. Este levantamento permanece rascunho.
- Mensagens em [MENSAGENS.md](MENSAGENS.md), documento versão 0.16 de 05/11/2026,
  salvas no SQLite: COM-01 na versão 5 e SNF-01 na versão 8, DIF-01 e SIM-01 na versão 4 e IRF-01 na versão 3,
  com dezenove versões históricas.
  Migrações 0009–0013: primeira mensagem com motivo em linguagem simples; sem nota fiscal
  inclui contato com fornecedor, nota emitida até a postagem e envio pelo WhatsApp,
  sem pedir nota avulsa. Demais instruções em mensagem separada.
  Todas sem saudações.
  Guias atuais: abertura e acompanhamento v3; pedidos GERAL/COM/SIM/DIF v3;
  IRF v4 e NFA v5; envio da nota existente pelo WhatsApp v4. Há 31 registros, incluindo 22 históricos.
  GERAL/COM/SIM/DIF v3, IRF v4 e NFA v5 foram revisados textualmente pelo autor; demais guias permanecem
  em rascunho. A revisão textual não substitui análise fiscal nem autoriza envio automático.
  versões 1 dos guias comuns preservadas. Migrações 0007_fluxo_sac_correios e 0014_solicitacoes_irregularidade_nfa.
  A 0014 registra as duas versões completas de solicitação com o formato fornecido pelo autor.
  Fluxo descrito pelo autor e conferido com capturas; mensagens-base atualizadas em 02/11; fundamento e lacunas em ORIENTACAO_PORTAL.md.
  Ainda sem aprovação ou integração ao envio. SIMEI permanece provisória até o detalhamento previsto
  pelo autor para terça-feira, 03/11/2026.
- Comercialização terá explicação geral da categoria, conforme orientação do autor, sem exigir
  preenchimento de uma pendência específica na mensagem explicativa.
- Para cada categoria, mapear código/descrição real do SIAT, situação da mercadoria, tipo de pendência,
  estado de pagamento quando disponível e encaminhamento aprovado. Não inventar campos ou seletores.
- O sistema usará o motivo registrado pela fiscalização e a orientação correspondente. Não inferirá
  comercialização pela quantidade, SIMEI pelo CNPJ ou DIFAL apenas por compra pela internet.
- Categorias podem se sobrepor no mundo real. Dois motivos, código desconhecido ou informação insuficiente
  exigem análise humana; nenhuma prioridade automática entre categorias foi definida.
- SIMEI: validar a explicação geral com o autor; não interpretar a modalidade de cobrança.
- Sem nota fiscal: usar o motivo registrado; não decidir sobre dispensa ou emissão de documento.
- DIFAL: usar o motivo registrado; não avaliar responsável, pagamento, enquadramento ou cálculo.
- Irregularidades fiscais: usar somente quando a categoria estiver confirmada; não classificar
  resultados desconhecidos como irregularidades fiscais. Encaminhamento pelos mesmos guias do SAC.
- Avaliar cada categoria e subtipo separadamente, com as mesmas etapas no manual e no sistema. A ampliação
  exige revisar quantidade de casos, cobertura do piloto e viabilidade das metas de 09/11 e 13–17/11.

## Referências do levantamento

- Instruções atuais do autor: escopo, tecnologias, limites, pesquisa e prazo.
- `projeto/documentos do projeto/Arquitetura_MVP_SIAT_sem_cronograma.pdf`: arquitetura atual.
- Entrevista de levantamento: consultas, orientações repetidas e encaminhamento técnico.
- Documentos de identificação e validação de problemas: levantamento inicial; não presumir
  aprovação uniforme de todos os itens.
- `Instrucoes_teste_tempo_atendimento_manual.pdf`: marcos de medição já propostos.

Levantamentos em `D:/TCC/documento de pesquisa/documentos do posto fiscal/`.
Dados pessoais dos participantes não são reproduzidos. As regras exatas do SIAT não foram deduzidas
da entrevista. PDFs antigos e README anterior não prevalecem sobre o escopo atual.

## Requisitos funcionais e critérios de aceite

| ID | Requisito | Critério de aceite planejado | Estado em 01/11 |
| --- | --- | --- | --- |
| RF01 | Abrir diretamente o painel local | Acesso sem conta ou senha; sem administração de usuários; clientes remotos recusados | Implementado; login removido por decisão do autor |
| RF02 | Receber identificador das cinco categorias | Validar presença e formato confirmado no mapeamento; não inventar campos SIAT | Categorias definidas; identificadores e caminhos pendentes P01/P02 |
| RF03 | Consultar uma atividade por vez nas telas | Segundo pedido simultâneo recusado; tempo máximo respeitado; nenhum acesso ao banco fiscal | Pendente P02/P03 |
| RF04 | Distinguir resultados e falhas | Identificado, não localizado, ambíguo, desconhecido, erro, sessão expirada e timeout têm tratamentos distintos; erro/não localizado não significa ausência de pendência | Pendente P02 |
| RF05 | Manter catálogo separado | Orientação tem categoria, situação, versão, fonte legal, dispositivo, vigência e estado de revisão; alteração exige nova revisão | Modelo e cinco rascunhos persistidos; interface e fluxo de revisão pendentes P04 |
| RF06 | Preparar orientação correspondente | Resultado confirmado e texto disponível/vigente permitem colagem solicitada pelo operador; rascunhos mantêm aviso; envio manual | Implementado; revisão editorial permanece separada |
| RF07 | Exigir conferência da mensagem | Mensagem integral visível; operador confere destinatário na conversa escolhida | Implementado no painel; destinatário não é lido pelo programa |
| RF08 | Colar e deixar o envio manual | Contagem de oito segundos; campo vazio e focado; nunca pressionar Enter ou clicar em Enviar | Validado em página fictícia; confirmar campo real |
| RF09 | Prevenir colagem duplicada | Clique duplo, POST repetido e atualização não repetem a colagem; tentativa incerta bloqueia repetição | Implementado e testado localmente |
| RF10 | Informar estado observado | Consulta, login, contagem, texto colado, falha e incerto distintos; não afirmar envio, entrega ou leitura | Implementado; não há acompanhamento de envio |
| RF11 | Exigir análise humana | Desconhecido, ambíguo ou sem orientação impede colagem e indica próxima ação | Testado com dados fictícios; mapeamento real pendente |
| RF12 | Descartar dados temporários | Encerramento, expiração ou abandono invalidam operação e limpam dados; próximo atendimento não reutiliza dados anteriores | Pendente P06 |
| RF13 | Orientar abertura manual no SAC | Guia usa link oficial e passos observados; não preenche, anexa ou envia protocolo | Guia e modelos no banco; capturas de descrição, resposta automática e destino; tela final pendente |
| RF14 | Orientar acompanhamento manual | Guia informa link, protocolo e código de acesso; não consulta nem armazena dados do protocolo | Texto no banco; interface futura |

RF09 marca a tentativa antes de colar. Timeout ou exceção depois desse ponto deixam
colagem incerta, sem repetição automática. Antes de uma nova tentativa ou após reiniciar,
o operador deve conferir o campo da conversa. O programa não controla nem confirma o envio manual.

## Requisitos não funcionais

| ID | Requisito | Condição verificável |
| --- | --- | --- |
| RNF01 | Ambiente simples | Windows, Python 3.12, Django, SQLite, HTML/CSS e Playwright; sem Docker, Redis ou RQ |
| RNF02 | Uso individual e local | Loopback, um processo e um atendimento ativo no fluxo futuro, inclusive entre abas |
| RNF03 | Espera limitada | Timeout por navegação e por consulta completa; retornar controle após falha; confirmar encerramento antes de liberar outra operação |
| RNF04 | Minimização de dados | Identificadores, telefones e dados fiscais fora de banco, logs, URLs, capturas, traces e relatórios de exceção |
| RNF05 | Autenticação externa responsável | Não pedir senha em chat, copiar perfis pessoais ou contornar controles; sessão expirada interrompe a operação |
| RNF06 | Manutenção compreensível | Módulos pequenos, responsabilidades separadas, nomes claros e instruções reproduzíveis |
| RNF07 | Pesquisa auditável | Código de caso, condição, duração, correção e falhas; simulações identificadas e separadas |
| RNF08 | Segurança do painel | Restrição local, CSRF e token por ação de colagem; repetição de requisição não repete o efeito externo |

RNF01 e partes de RNF02/RNF08 estão na base. Os testes iniciais não demonstram atendimento integral
dos requisitos do fluxo futuro.

## Dados e sessões: plano a confirmar

- Persistência atual: sem modelos de contas ou sessões habilitados. Tabelas legadas da preparação anterior
  podem existir no banco local, sem uso e sem exclusão automática. Sem dados fiscais.
- Persistência atual do catálogo: cinco explicações na tabela `catalogo_orientacao`: COM-01 v5 e SNF-01 v8,
  DIF-01 e SIM-01 v4 e IRF-01 v3, com dezenove versões históricas; na tabela `catalogo_guiaportal`, dois guias comuns na versão 2
  e os demais guias conforme MENSAGENS.md: 31 registros, sendo nove atuais e 22 históricos.
  Pedido geral, variantes COM/SIM/DIF v3, IRF v4 e NFA v5 revisados textualmente pelo autor;
  demais guias e explicações em rascunho. Sem interface de edição ou revisão por enquanto.
- Persistência futura adicional: configurações não sensíveis; não inserir casos reais em orientações,
  nomes de objetos administrativos, mensagens de erro ou arquivos de teste.
- Atendimento futuro: memória temporária do processo, sem sessões Django. Armazenamento temporário,
  expiração e limpeza ainda serão implementados.
- Retenção: duração pendente (P06); considerar encerramento, reinício, queda do navegador, próximo
  atendimento e expiração. Não prometer eliminação forense de memória ou proteção contra coleta do SO.
- Perfis de navegador: próprios e distintos por integração, somente após autorização; retenção de cookies
  pendente. Não copiar sessões existentes nem ativar capturas, traces e vídeos em atendimentos reais.
- Avaliação: sem identificadores reais de mercadorias, nomes, CNPJ, telefone, mensagens integrais
  ou vínculos com identidades. Evitar campos livres.

## Proposta de avaliação a fechar até 03/11

Mesma categoria, mesmas etapas, condições comparáveis e critérios de correção definidos antes da coleta.
O manual pode usar o instrumento existente; ainda não foi desenvolvido coletor no sistema.

| Marco | Definição proposta |
| --- | --- |
| T0 | Início efetivo da verificação com dados necessários disponíveis; fila anterior excluída |
| T1 | Situação e eventual motivo identificados |
| T2 | Envio da última informação necessária; resposta parcial não encerra tarefa |
| T3 | Registro interno obrigatório concluído, ou NA quando não existir |
| TF | Última etapa necessária: maior entre T2 e T3, ou T2 quando não há registro |

No sistema, T2 exige observação do envio manual, comparável à condição manual.
Texto colado não é T2; resultado incerto mantém caso não confirmado/incompleto. Preservar tempo total (TF−T0),
pausas externas sem sobreposição e tempo de execução após pausas. Carregamento e lentidão permanecem
na duração. Casos incompletos não recebem conclusão fictícia.

Registro mínimo proposto: código de caso/operador, categoria/subtipo, condição manual ou sistema,
cenário real ou simulado, ordem, marcos, pausas, conclusão completo/incompleto/não observado,
correção sim/não/não verificável, código de falha e retrabalho. Documentar condições de rede,
equipamento e sessão por rodada, sem informações pessoais ou segredos.

Definir quantidade, elegibilidade, janela consecutiva de observação, distribuição da ordem manual/sistema
para reduzir aprendizagem, responsável pela conferência e gabarito revisado. Não misturar categorias ou
comparar etapa parcial com atendimento completo. Simulações testam programa e procedimento, sem comprovar
desempenho real. Não selecionar só casos rápidos nem excluir falhas silenciosamente. Considerar tempos,
correção, incompletude e limitações da amostra na conclusão.

## Decisões pendentes

Em 07/11/2026, o autor demonstrou o menu Trânsito → Notificação Correios →
Consultar Notificação. Esse trecho está programado como rotina isolada e testado
com menu fictício. P02 permanece aberto para validação no SIAT, tela de destino,
consulta por rastreio e seus resultados. Detalhes em [SIAT.md](SIAT.md).

Separar a entrada na área de consulta do processamento de cada encomenda.
Reutilizar a tela aberta entre rastreios, verificando o estado atual antes de
agir. Refazer os menus somente quando necessário para retornar à área de consulta;
sessão expirada exige login manual. Reconhecimento da tela e preparação dos campos
para a consulta seguinte dependem do próximo mapeamento de P02.

O terceiro print fornecido pelo autor mostra o formulário de consulta por
Cód. Rastreio. Preenchimento, substituição do código anterior e clique em Consultar
estão isolados em `consulta.py`, com conferência dos controles em `estado.py`.
P02 continua pendente para validação do DOM real, término da pesquisa, resultados
e expiração. O aviso inicial de lista vazia não será interpretado como resultado
da nova consulta. Nenhuma leitura fiscal ou conexão ao Brave foi implementada.

O autor confirmou o código de rastreio como primeira informação recebida no atendimento.
Não pedir o código novamente ao orientar o envio da nota pelo WhatsApp. Validar ainda seu
formato e uso no SIAT; preencher rastreio no portal continua sendo uma etapa independente.

| ID | Informação necessária | Efeito |
| --- | --- | --- |
| P01 | Formato e uso do código de rastreio inicial, subtipos e ordem de implementação nas cinco categorias | Campos, caminhos completos e elegibilidade da comparação |
| P02 | Menus, telas, resultados, estados vazios, ambiguidades e expiração SIAT | Navegação, seletores e interpretação; não inventar |
| P03 | Condições autorizadas de acesso, automação, WhatsApp institucional, dados e testes | Integração/avaliação real depende de confirmação |
| P04 | Textos revisados, aprovador e encaminhamentos | Impede orientação automática sem revisão |
| P05 | Localização e análise do código WhatsApp; evidência de envio | Define tecnologia; Playwright ainda é possibilidade |
| P06 | Retenção, perfis, recuperação após reinício/falha e controle de duplicidade | Descarte e recuperação segura |
| P07 | Procedimento, amostra, gabarito, observador, condições e registros internos | Comparação justa e conclusão correta |
| P08 | Necessidade real de rastreamento Correios | Manter manual até justificativa |
| P09 | Explicações gerais revisadas, códigos SIAT e correspondência das cinco categorias | Validar seleção da explicação; resolução e avaliação fiscal pertencem ao atendimento da SEFAZ |
| P10 | Confirmar seleção dos avisos, tela Finalizado, resultado/complementação e recuperação; validar procedimento documental e encaminhamento institucional | Descrição, resposta automática e Registro do SAC documentados com capturas; concluir validação sem enviar dados reais |

## Ordem de desenvolvimento e validação

1. Fechar P01–P04 e P07 com os responsáveis, avançando no restante com dados fictícios.
2. Implementar catálogo revisado, atendimento temporário e estados de consulta/envio.
3. Testar consulta única, timeout, sessão expirada, ambiguidade, erro, autorização inválida,
   troca de mensagem/destinatário, clique duplo, concorrência e descarte com dados fictícios.
4. Com mapeamento e autorização, integrar um caminho SIAT e conferir resultados manualmente.
5. Analisar a automação anterior; integrar envio com evidências e proteção contra repetição,
   usando destinatário de teste autorizado. Não repetir automaticamente operações incertas.
6. Executar piloto, corrigir falhas e congelar procedimento antes da avaliação principal.

Metas: requisitos/acessos/procedimento até **03/11/2026**; fluxo até **09/11**; piloto **10–12/11**;
avaliação **13–17/11**; análise/redação a partir de **18/11**; TCC completo até **27/11**.
Se categoria, acesso, mapeamento ou envio não forem resolvidos a tempo, 09/11 fica em risco.
Replanejar com o autor, sem tratar demonstração simulada como avaliação real.
