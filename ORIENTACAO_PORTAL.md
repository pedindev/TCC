# Orientação manual pelo portal da SEFAZ-PI

Atualização: 05/11/2026. Rascunho para revisão operacional. Fluxo descrito pelo autor,
conferido com três imagens fornecidas e com a observação anterior das páginas públicas.
Em 02/11/2026, o autor forneceu a mensagem-base de solicitação de boleto; foram criadas
versões completas para irregularidade fiscal e nota avulsa. A opção de unidade é indicada
pelo nome PF CORREIOS, não pela posição na lista. O botão humano mantém o texto da captura.
Nenhum formulário foi enviado e nenhum protocolo real foi criado ou consultado.

## Papel do MVP

A orientação reúne a explicação da retenção, o pedido adequado ao caso, a abertura manual
do SAC e o acompanhamento pelo próprio contribuinte. Abrange comercialização, SIMEI,
sem nota fiscal, e-commerce / DIFAL e irregularidades fiscais.

O sistema não calcula imposto, emite guia ou nota fiscal, decide liberação, preenche o SAC
nem envia protocolos. Dados de solicitações, comprovantes da compra, protocolo e código de acesso são
usados pelo contribuinte no portal. A nota fiscal já existente é enviada pelo WhatsApp do
atendimento, conforme correção expressa do autor; o MVP não recebe nem armazena esse arquivo; o catálogo guarda somente textos genéricos.
O uso dos modelos não presume dívida nem define quem deve pagar.

## 1. Identificar o solicitante

Acessar o [Serviço de Atendimento ao Cidadão (SAC)](https://portal.sefaz.pi.gov.br/servicos-institucional+servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337).

O fluxo mostrado na primeira captura é:
**Solicitante → Solicitação → Resposta Automática → Registro do SAC → Finalizado**.

Preencher CPF, nome completo, e-mail, confirmação do e-mail e telefone. Conferir os contatos,
informar se possui WhatsApp e escolher os avisos desejados entre as opções oferecidas pelo
portal: e-mail, SMS e WhatsApp, se disponível. Selecionar **Próximo**.

Os campos iniciais foram observados anteriormente na página pública. A escolha dos canais
de aviso foi descrita pelo autor, mas não aparece nas três capturas recebidas.

## 2. Descrever o pedido e anexar documentos

Na etapa **Solicitação**, preencher **O que você deseja? (descreva de forma detalhada)**.
Explicar o pedido, informar o código de rastreio completo e usar **Anexo** para os documentos
pertinentes. Conferir os arquivos adicionados antes de selecionar **Próximo**.
O comprovante solicitado para a nota avulsa é o pagamento da compra da mercadoria.
A nota fiscal já existente deve ser enviada pelo WhatsApp do atendimento, não por este formulário.

| Situação confirmada | Orientação e modelo no banco |
| --- | --- |
| Comercialização, e-commerce / DIFAL ou SIMEI, casos gerais | Pedir envio da guia do imposto e informar rastreio: SAC-PEDIDO-GERAL |
| Irregularidades fiscais | Pedir esclarecimentos sobre a irregularidade, orientações e guia se houver imposto a recolher; informar rastreio: SAC-PEDIDO-IRF |
| Sem nota fiscal, havendo nota já emitida | Contatar fornecedor e obter cópia da nota emitida até a postagem; enviar pelo WhatsApp do atendimento, que já recebeu o rastreio no início; SAC-PEDIDO-NF v4 orienta esse canal, sem abrir pedido no portal para esse envio |
| Sem nota fiscal, não sendo possível apresentar a nota indicada | Pedir nota avulsa, anexar comprovante da compra, informar nome, CPF e endereço do destinatário, rastreio e autorização de emissão: SAC-PEDIDO-NFA |

Os textos completos para orientar e copiar estão em [MENSAGENS.md](MENSAGENS.md).
Substituir os campos entre colchetes diretamente no portal. Não apresentar como fato um
anexo que não foi incluído, nem conceder autorização em nome de alguém sem legitimidade.

A alternativa de nota já existente não orienta emissão retroativa. Seu canal de envio é o WhatsApp, conforme correção do autor. A data e a validade
da nota serão analisadas pela SEFAZ; o corte pela postagem foi informado pelo autor e
não foi confirmado como regra legal específica. Ver os limites jurídicos abaixo.
Pagamento já realizado ou outra particularidade deve ser descrito para análise, sem
repetir automaticamente um pedido de cobrança.

## 3. Escolher atendimento humano

Na etapa **Resposta Automática**, destacar ao contribuinte:

> Para encaminhar seu pedido ao atendimento do PF Correios, selecione **Não foi satisfatória. Desejo receber atendimento humano**.

A tela informa que **A resposta foi satisfatória** registra e finaliza o atendimento automático.
Esse botão não é o caminho do pedido de atendimento humano descrito aqui. A captura também
mostra **Fazer uma nova pergunta (Voltar)**; ele não substitui o encaminhamento ao atendente.

O autor relaciona a resposta automática às transportadoras privadas. Essa exclusividade
não foi comprovada pela captura nem por norma localizada. O guia registra apenas o caminho
observado e indicado para o atendimento do PF Correios, sem generalizar o funcionamento do SAC.

## 4. Encaminhar à unidade correta

Na etapa **Registro do SAC**, tela **Informações da Solicitação**, usar o encaminhamento
informado pelo autor e visível na terceira captura:

| Campo | Preenchimento no caso descrito |
| --- | --- |
| Esta solicitação é para você? | **Sim**, quando o pedido for do próprio solicitante; representação deve ser informada corretamente |
| Desejo solicitar como | **Cidadão**, no pedido próprio descrito |
| Temática | **Mercadorias em trânsito \| Posto Fiscal** |
| Categoria | **Cálculo do imposto** |
| Unidades Organizacionais | **GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS** |
| A solicitação é relacionada a um processo? | **Não**, conforme mensagem definida pelo autor |

O nome da categoria do portal é uma escolha de encaminhamento, não uma tarefa de cálculo
do MVP. O autor indicou esse destino para os casos apresentados; sua aplicação às cinco
categorias ainda requer revisão operacional, especialmente aos pedidos de esclarecimento/NFA-e.

Conferir pedido, anexos, contatos e destino e finalizar conforme os controles do portal.
Guardar o protocolo e o código de acesso gerados. A geração desses dados foi relatada pelo
autor; a tela **Finalizado** e o texto do botão final ainda não foram apresentados.

## 5. Acompanhar a solicitação

Acessar [Acompanhe sua solicitação](https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao).
Preencher **Protocolo** e **Código de acesso** e confirmar no botão verde com o símbolo de confirmação.
Na inspeção anterior, a árvore de acessibilidade o nomeava Publicar; não orientar procurando
um rótulo Consultar que não foi observado.

Aguardar atendimento pela supervisão do posto fiscal, conforme o fluxo relatado. Consultar
a resposta e eventuais solicitações de complementação no portal. O canal escolhido poderá
receber avisos; a entrega não foi testada nem é garantida pelo MVP. Não depender somente do
aviso e não interpretar uma notificação como liberação da mercadoria. Não prometer prazo.

Se houver erro de acesso:

1. Conferir protocolo e código nos campos corretos, exatamente como recebidos, sem espaços extras.
2. Se não souber o código, usar **Esqueci o código de acesso** e seguir o próprio portal.
3. Se os dados estiverem corretos, guardá-los antes de fechar o navegador, reabrir e tentar novamente.
4. Persistindo o erro, procurar os canais oficiais da SEFAZ-PI. Evitar criar outro protocolo
   apenas para tentar corrigir falha de acesso.

Reabrir o navegador é tentativa de diagnóstico sugerida pelo autor, não solução garantida.
A recuperação, o resultado da consulta e a complementação ainda não foram testados.

## Fundamento e limites jurídicos para a pesquisa

Consulta em 01/11/2026. A fonte estadual abaixo é a publicação original de 2023; não se
atestou toda a cadeia de alterações vigente em novembro de 2026 nem sua aplicação a cada
operação interestadual. A aceitação de documento e a emissão pertencem à autoridade fiscal.

| Tema | Base localizada e alcance |
| --- | --- |
| Sigilo fiscal | **CTN, art. 198** protege informações fiscais obtidas no exercício do cargo, com exceções legais. Não contém proibição geral ao WhatsApp. A restrição específica do posto precisa de norma/procedimento institucional. |
| Momento da NF-e | **RICMS-PI, Anexo VI, art. 83, I** prevê emissão antes da saída. Isso não equivale a aceitar qualquer nota do dia da postagem; o momento da operação e a regra aplicável ao emitente precisam de exame. |
| Nota avulsa | **RICMS-PI, Anexo VI, arts. 89 e 90, V** contempla NFA-e para regularização do trânsito após ação fiscal. Não garante deferimento do pedido. |
| Anexos, CPF, endereço e autorização | São o procedimento informado pelo autor. Não foi localizada nesses artigos uma lista que comprove especificamente essas exigências para o SAC/PF Correios. |

Fontes:

- [CTN, texto atualizado disponibilizado pela Câmara dos Deputados](https://www2.camara.leg.br/legin/fed/lei/1960-1969/lei-5172-25-outubro-1966-358971-normaatualizada-pl.html), art. 198.
- [Decreto 21.866/2023, DOE nº 47, publicação original](https://www.diario.pi.gov.br/doe/files/diarios/anexo/5714d565-bd46-4f50-950d-7fa74dbdc549/DIARIO-OFICIAL-DO-ESTADO-DO-PIAUI-PUBLICACAO-N-47.pdf#page=156), Anexo VI, página impressa 156, arts. 83 e 89–90.
- [Portal de legislação SEFAZ-PI](https://portaldalegislacao.sefaz.pi.gov.br/inicio), referência para conferir consolidação; acesso anterior apresentou timeout.

Decisão do projeto: explicar a categoria de forma geral e encaminhar os detalhes fiscais
ao SAC. Essa é uma escolha operacional coerente com a proteção da informação; não deve
ser apresentada no TCC como conclusão legal de que o WhatsApp é sempre proibido.

## Evidências preservadas e uso no TCC

As três capturas originais fornecidas pelo autor foram copiadas sem edição:

- [SAC — descrição e anexo](../documentos%20do%20projeto/SAC_2026-11-01_01_solicitacao.png).
- [SAC — resposta automática e opção humana](../documentos%20do%20projeto/SAC_2026-11-01_02_resposta_automatica.png).
- [SAC — registro e unidade de destino](../documentos%20do%20projeto/SAC_2026-11-01_03_registro.png).

A data do nome é a do recebimento; não comprova quando as imagens foram capturadas.
Elementos incidentais do navegador e o exemplo digitado na segunda imagem não integram os modelos.
As capturas são evidência de interface, não legislação ou autorização para envio de dados.

| Informação | Evidência disponível | Limite |
| --- | --- | --- |
| Campos iniciais e entrada do acompanhamento | Inspeção pública anterior | Sem envio/consulta |
| Descrição, anexo, botão humano e destino | Capturas fornecidas | Sem execução completa pelo projeto |
| Documentos exigidos, avisos, supervisão e geração dos códigos | Relato do autor | Confirmar procedimento institucional e tela final |
| Dificuldade dos cidadãos na resposta automática | Relato do autor | Hipótese para avaliação, sem frequência ou ganho medidos |
| Bases legais acima | Fontes oficiais identificadas | Vigência estadual consolidada e regra interna pendentes |

Para a futura avaliação, observar se o participante descreve corretamente o pedido,
informa o rastreio, inclui o anexo quando cabível, escolhe atendimento humano, direciona
ao PF Correios e consegue localizar a resposta. Registrar confusão, retorno de etapa,
pedido incompleto e erro de acesso sem guardar dados reais. Estes são critérios propostos,
não resultados de pesquisa. O instrumento e o gabarito precisam ser definidos antes da coleta.

## Catálogo persistido e pendências

- Tabela catalogo_orientacao: cinco mensagens atuais (COM-01 v5 e SNF-01 v8, DIF-01 e SIM-01 v4, IRF-01 v3) e dezenove versões históricas.
  A migração 0009 separa as etapas: primeira mensagem explica somente o motivo em linguagem
  simples, começando com “Sua mercadoria está retida porque”; segunda mensagem orienta a
  resolução e contém os links, modelos e passos do portal.
  Correção nas migrações 0011–0013: sem nota fiscal inclui já o envio da nota pelo WhatsApp na primeira
  mensagem, com contato ao fornecedor e nota emitida até a postagem, sem pedido de nota avulsa.
  O rastreio já chega no início do atendimento; não pedi-lo novamente pelo WhatsApp. Não acrescentar esse pedido automaticamente.
- Guias atuais: abertura e acompanhamento v3; pedidos GERAL/COM/SIM/DIF v3;
  IRF v4 e NFA v5; envio da nota existente pelo WhatsApp v4. Há 31 registros, incluindo 22 históricos.
  GERAL/COM/SIM/DIF v3, IRF v4 e NFA v5 foram revisados textualmente pelo autor; demais guias permanecem
  em rascunho. A revisão textual não substitui análise fiscal nem autoriza envio automático.
- Migrações 0015–0017: mensagens curtas, aprovação do texto geral e de IRF e remoção da
  condição sobre processo de todas as mensagens atuais, conforme instrução do autor.
  GERAL/COM/SIM/DIF, IRF e NFA incluem acompanhamento; o guia complementar serve para ajuda de acesso.
  Não há integração de envio.
- O campo verificado_em indica conferência das referências em 01/11/2026, não aprovação institucional.
  Notas de origem, fundamento e lacunas também estão salvas em observacoes no banco.
- Confirmar escolha dos avisos, tela final, resultado/complementação, recuperação de acesso,
  orientação para representante/processo existente, regra documental do posto e redação estadual vigente.
- Preservar SIMEI como provisória até detalhamento do autor. O roteiro não decide a natureza do ICMS.
