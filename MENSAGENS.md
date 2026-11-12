# Mensagens de orientação ao contribuinte

Versão do documento: 0.16 — 05/11/2026. Guias gerais revisados pelo autor; explicações e demais guias em rascunho.

## Padrão definido pelo autor

O código de rastreio é a primeira informação recebida no atendimento. Não solicitá-lo
novamente no WhatsApp ao pedir o envio da nota fiscal. O contribuinte ainda o informa
nas solicitações que abrir no portal, pois é um atendimento separado.

Após identificar a retenção no SIAT Web, apresentar a primeira mensagem correspondente,
sempre começando com “Sua mercadoria está retida porque”. Ela explica o motivo
em linguagem simples. Exceção solicitada pelo autor: sem nota fiscal já inclui o envio
da nota pelo WhatsApp, após contato com o fornecedor e conferência da data de emissão
até a postagem nos Correios, sem pedir nota avulsa. Na comercialização, explicar quantidade/habitualidade e a cobrança;
no DIFAL, explicar a divisão do imposto e a responsabilidade do fornecedor na hipótese indicada.

A segunda mensagem explica como resolver: solicitar boleto, pedir nota avulsa ou obter esclarecimentos.
A nota fiscal já existente é enviada pelo WhatsApp, conforme correção do autor. Os links, modelos de pedido, anexos, passos do SAC e acompanhamento ficam nessa etapa.
Os guias abaixo fornecem esse conteúdo separado. Não acrescentar automaticamente o pedido
de nota avulsa à mensagem de ausência de nota: o foco dessa mensagem é enviar o documento.

A migração 0010 salva COM-01 na versão 5; a migração 0013 atualiza SNF-01 para a versão 8.
DIF-01 e SIM-01 permanecem na versão 4; IRF-01, na versão 3.
Há cinco mensagens atuais e dezenove versões históricas.
Guias atuais: abertura e acompanhamento v3; pedidos GERAL/COM/SIM/DIF v3;
IRF v4 e NFA v5; envio da nota existente pelo WhatsApp v4. Há 31 registros, incluindo 22 históricos.
GERAL/COM/SIM/DIF v3, IRF v4 e NFA v5 foram revisados textualmente pelo autor; demais guias permanecem
em rascunho. A revisão textual não substitui análise fiscal nem autoriza envio automático.

Confirmar o motivo atual no SIAT antes de selecionar a explicação. Comercialização exige
cobrança confirmada para usar o texto; não deduzir revenda por quantidade ou habitualidade
automaticamente. DIFAL: a responsabilidade indicada é para consumidor final não contribuinte.
SIMEI permanece provisória. Ausência de nota precisa ser confirmada; erro de consulta não
significa documento ausente. Não classificar motivo desconhecido como irregularidade fiscal.

A fundamentação e os limites ficam nas notas internas de [ORIENTACAO_PORTAL.md](ORIENTACAO_PORTAL.md)
e [REQUISITOS.md](REQUISITOS.md). A versão mais recente não significa aprovação para envio.
Os textos abaixo espelham o banco; editar apenas este arquivo não atualiza o catálogo.

## COM-01 — Comercialização

> Sua mercadoria está retida porque a fiscalização identificou características de compra para revenda. Isso pode acontecer pela quantidade de produtos ou pela habitualidade das compras, quando indicam que as mercadorias serão vendidas a outras pessoas. Nesse caso, há uma cobrança de imposto referente à mercadoria.

## DIF-01 — E-commerce / DIFAL

> Sua mercadoria está retida porque há uma pendência no pagamento da parte do imposto dessa compra que cabe ao Piauí. Quando uma loja de outro estado vende para um consumidor no Piauí, o ICMS é dividido entre o estado de origem e o de destino. A diferença que cabe ao estado que recebe a mercadoria é chamada de DIFAL. Nas compras para uso pessoal, quando o comprador não é contribuinte de ICMS, quem deve pagar essa diferença é o fornecedor, ou seja, a loja que vendeu a mercadoria.

## SIM-01 — SIMEI — provisória

> Sua mercadoria está retida porque há uma pendência de ICMS em uma compra que envolve um MEI, o Microempreendedor Individual. O ICMS é o imposto ligado à venda de mercadorias.

## SNF-01 — Sem nota fiscal

> Sua mercadoria está retida porque veio sem nota fiscal. Entre em contato com o fornecedor e peça uma cópia da nota fiscal da mercadoria, que deve ter sido emitida até a data da postagem nos Correios. Depois, envie a nota por este WhatsApp para análise da equipe do posto fiscal.

## IRF-01 — Irregularidades fiscais

> Sua mercadoria está retida porque foi identificado um problema fiscal relacionado ao envio. Esse tipo de retenção pode ter motivos diferentes, e o aviso de irregularidade fiscal, sozinho, não informa qual é o problema no seu caso.

## Guias e modelos de pedido persistidos

A migração 0018 salva a orientação de nota avulsa aprovada pelo autor, com nome, CPF e endereço
explicitamente identificados como dados do destinatário. Texto completo e acompanhamento preservados.

Guias atuais: abertura e acompanhamento v3; pedidos GERAL/COM/SIM/DIF v3;
IRF v4 e NFA v5; envio da nota existente pelo WhatsApp v4. Há 31 registros, incluindo 22 históricos.
GERAL/COM/SIM/DIF v3, IRF v4 e NFA v5 foram revisados textualmente pelo autor; demais guias permanecem
em rascunho. A revisão textual não substitui análise fiscal nem autoriza envio automático.

A migração 0017 retira a condição sobre processo de todas as mensagens atuais e salva a
orientação de situação fiscal irregular aprovada no chat. A opção fica apenas Não.
As versões anteriores permanecem como histórico. GERAL/COM/SIM/DIF, IRF e NFA já incluem o link de acompanhamento.
O guia complementar permanece disponível para ajuda de acesso. Blocos prontos para copiar no WhatsApp.

### SAC-ABERTURA — versão 3 — rascunho

```text
1. Acesse o Serviço de Atendimento ao Cidadão (SAC) no portal da SEFAZ-PI. Na etapa Solicitante, preencha seus dados: CPF, nome completo, e-mail, confirmação do e-mail e telefone. Confira os contatos e informe se possui WhatsApp. Escolha os avisos que deseja receber entre as opções disponíveis: e-mail, SMS e WhatsApp, se oferecido. Selecione Próximo.

2. Em Solicitação, no campo O que você deseja? (descreva de forma detalhada), explique seu pedido e informe o código de rastreio da mercadoria retida. Use o modelo correspondente ao motivo da retenção, substituindo os campos entre colchetes. Quando houver documentos para apresentar, utilize Anexo e confira se foram adicionados antes de selecionar Próximo.

3. Na etapa Resposta Automática, para encaminhar este pedido ao atendimento do PF Correios, selecione Não foi satisfatória. Desejo receber atendimento humano. A opção A resposta foi satisfatória registra e finaliza o atendimento automático; ela não é o caminho deste pedido de atendimento humano.

4. Em Informações da Solicitação, se o pedido for para você, marque Sim em Esta solicitação é para você? e selecione Cidadão em Desejo solicitar como. Se estiver representando outra pessoa, informe essa condição corretamente. Selecione:
Temática: Mercadorias em trânsito | Posto Fiscal.
Categoria: Cálculo do imposto.
Unidades Organizacionais: GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS.
Em A solicitação é relacionada a um processo?, marque Não.

5. Confira os dados, o pedido, os anexos e a unidade de destino e finalize a solicitação. Guarde o protocolo e o código de acesso apresentados ao concluir. Eles serão necessários para acompanhar o atendimento no portal.
```

### SAC-ACOMPANHAMENTO — versão 3 — rascunho

```text
*ACOMPANHE SUA SOLICITAÇÃO*

➡️ https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao

Digite o *protocolo* e o *código de acesso* recebidos ao finalizar o pedido. Confirme no botão verde.

Aguarde o atendimento da supervisão do posto fiscal. Veja a resposta e eventuais pedidos de documentos pelo portal, mesmo que não chegue aviso por e-mail, SMS ou WhatsApp. O aviso não significa que a mercadoria já foi liberada.

*Não conseguiu acessar?*
• Confira o protocolo e o código de acesso, sem espaços extras.
• Perdeu o código? Use *Esqueci o código de acesso*.
• O erro continua? Guarde os códigos, feche e reabra o navegador. Se persistir, procure o atendimento oficial da SEFAZ. Não abra outro protocolo apenas por um erro de acesso.
```

### SAC-PEDIDO-COM — versão 3 — revisado

```text
*SOLICITE O BOLETO*

➡️ Acesse:
https://portal.sefaz.pi.gov.br/servicos-institucional+servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337

1️⃣ Preencha seus dados e escolha como receber avisos, entre as opções disponíveis. Clique em *Próximo*.

2️⃣ No campo *O QUE VOCÊ DESEJA?*, escreva:

“Solicito o boleto do imposto da mercadoria retida nos Correios. Código de rastreio: [COLOQUE SEU CÓDIGO].”

3️⃣ Clique em *Próximo*. Na resposta automática, escolha:
*Não foi satisfatória. Desejo receber atendimento humano.*

4️⃣ Na próxima tela, selecione:

• Solicitação para você: *Sim*.
• Solicitar como: *Cidadão*.
• Temática: *Mercadorias em trânsito | Posto Fiscal*.
• Categoria: *Cálculo do imposto*.
• Unidade: *GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS*.
• Relacionada a processo: *Não*.

5️⃣ Confira e finalize. *Guarde o protocolo e o código de acesso.*

Aguarde o atendimento da supervisão do posto fiscal. Para acompanhar a resposta, use esses dois códigos:
https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao
```

### SAC-PEDIDO-DIF — versão 3 — revisado

```text
*SOLICITE O BOLETO*

➡️ Acesse:
https://portal.sefaz.pi.gov.br/servicos-institucional+servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337

1️⃣ Preencha seus dados e escolha como receber avisos, entre as opções disponíveis. Clique em *Próximo*.

2️⃣ No campo *O QUE VOCÊ DESEJA?*, escreva:

“Solicito o boleto do DIFAL da mercadoria retida nos Correios para encaminhar ao fornecedor. Código de rastreio: [COLOQUE SEU CÓDIGO].”

3️⃣ Clique em *Próximo*. Na resposta automática, escolha:
*Não foi satisfatória. Desejo receber atendimento humano.*

4️⃣ Na próxima tela, selecione:

• Solicitação para você: *Sim*.
• Solicitar como: *Cidadão*.
• Temática: *Mercadorias em trânsito | Posto Fiscal*.
• Categoria: *Cálculo do imposto*.
• Unidade: *GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS*.
• Relacionada a processo: *Não*.

5️⃣ Confira e finalize. *Guarde o protocolo e o código de acesso.*

Aguarde o atendimento da supervisão do posto fiscal. Para acompanhar a resposta, use esses dois códigos:
https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao
```

### SAC-PEDIDO-GERAL — versão 3 — revisado

```text
*SOLICITE O BOLETO*

➡️ Acesse:
https://portal.sefaz.pi.gov.br/servicos-institucional+servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337

1️⃣ Preencha seus dados e escolha como receber avisos, entre as opções disponíveis. Clique em *Próximo*.

2️⃣ No campo *O QUE VOCÊ DESEJA?*, escreva:

“Solicito o boleto do imposto da mercadoria retida nos Correios. Código de rastreio: [COLOQUE SEU CÓDIGO].”

3️⃣ Clique em *Próximo*. Na resposta automática, escolha:
*Não foi satisfatória. Desejo receber atendimento humano.*

4️⃣ Na próxima tela, selecione:

• Solicitação para você: *Sim*.
• Solicitar como: *Cidadão*.
• Temática: *Mercadorias em trânsito | Posto Fiscal*.
• Categoria: *Cálculo do imposto*.
• Unidade: *GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS*.
• Relacionada a processo: *Não*.

5️⃣ Confira e finalize. *Guarde o protocolo e o código de acesso.*

Aguarde o atendimento da supervisão do posto fiscal. Para acompanhar a resposta, use esses dois códigos:
https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao
```

### SAC-PEDIDO-IRF — versão 4 — revisado

```text
*SITUAÇÃO FISCAL IRREGULAR — SOLICITE INFORMAÇÕES E O BOLETO*

➡️ Acesse:
https://portal.sefaz.pi.gov.br/servicos-institucional+servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337

1️⃣ Preencha seus dados e escolha como receber avisos, entre as opções disponíveis. Clique em *Próximo*.

2️⃣ No campo *O QUE VOCÊ DESEJA?*, escreva:

“Minha mercadoria está retida por irregularidade fiscal. Quero saber qual é o problema e o que preciso fazer para resolver. Se houver imposto a pagar, solicito o boleto. Código de rastreio: [COLOQUE SEU CÓDIGO].”

3️⃣ Clique em *Próximo*. Na resposta automática, escolha:
*Não foi satisfatória. Desejo receber atendimento humano.*

4️⃣ Na próxima tela, selecione:

• Solicitação para você: *Sim*.
• Solicitar como: *Cidadão*.
• Temática: *Mercadorias em trânsito | Posto Fiscal*.
• Categoria: *Cálculo do imposto*.
• Unidade: *GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS*.
• Relacionada a processo: *Não*.

5️⃣ Confira e finalize. *Guarde o protocolo e o código de acesso.*

Aguarde o atendimento da supervisão do posto fiscal. Para acompanhar a resposta, use esses dois códigos:
https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao
```

### SAC-PEDIDO-NF — versão 4 — rascunho

```text
Entre em contato com o fornecedor e peça uma cópia da nota fiscal da mercadoria, que deve ter sido emitida até a data da postagem nos Correios. Depois, envie a nota por este WhatsApp para análise da equipe do posto fiscal.
```

### SAC-PEDIDO-NFA — versão 5 — revisado

```text
*SOLICITE A NOTA FISCAL AVULSA*

➡️ Acesse:
https://portal.sefaz.pi.gov.br/servicos-institucional+servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337

1️⃣ Preencha seus dados e escolha como receber avisos, entre as opções disponíveis. Clique em *Próximo*.

2️⃣ No campo *O QUE VOCÊ DESEJA?*, escreva e substitua os campos entre colchetes. *Nome, CPF e endereço devem ser os dados do destinatário:*

“Solicito e autorizo a emissão de nota fiscal avulsa para minha mercadoria retida nos Correios.
Código de rastreio: [COLOQUE SEU CÓDIGO].
Nome do destinatário: [NOME COMPLETO].
CPF: [CPF].
Endereço: [ENDEREÇO COMPLETO, INCLUINDO CEP].”

📎 Em *Anexo*, envie o *comprovante de pagamento da compra da mercadoria*. Confira se o arquivo foi anexado.

3️⃣ Clique em *Próximo*. Na resposta automática, escolha:
*Não foi satisfatória. Desejo receber atendimento humano.*

4️⃣ Na próxima tela, selecione:

• Solicitação para você: *Sim*.
• Solicitar como: *Cidadão*.
• Temática: *Mercadorias em trânsito | Posto Fiscal*.
• Categoria: *Cálculo do imposto*.
• Unidade: *GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS*.
• Relacionada a processo: *Não*.

5️⃣ Confira e finalize. *Guarde o protocolo e o código de acesso.*

Aguarde o atendimento da supervisão do posto fiscal. Para acompanhar a resposta, use esses dois códigos:
https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao
```

### SAC-PEDIDO-SIM — versão 3 — revisado

```text
*SOLICITE O BOLETO*

➡️ Acesse:
https://portal.sefaz.pi.gov.br/servicos-institucional+servico-de-atendimento-ao-cidadao-sac+66ec6df8f327ef3a7ecb4337

1️⃣ Preencha seus dados e escolha como receber avisos, entre as opções disponíveis. Clique em *Próximo*.

2️⃣ No campo *O QUE VOCÊ DESEJA?*, escreva:

“Solicito o boleto do imposto da mercadoria retida nos Correios. Código de rastreio: [COLOQUE SEU CÓDIGO].”

3️⃣ Clique em *Próximo*. Na resposta automática, escolha:
*Não foi satisfatória. Desejo receber atendimento humano.*

4️⃣ Na próxima tela, selecione:

• Solicitação para você: *Sim*.
• Solicitar como: *Cidadão*.
• Temática: *Mercadorias em trânsito | Posto Fiscal*.
• Categoria: *Cálculo do imposto*.
• Unidade: *GASEC > SUPREC > UNITRAN > GTRAN / PF CORREIOS*.
• Relacionada a processo: *Não*.

5️⃣ Confira e finalize. *Guarde o protocolo e o código de acesso.*

Aguarde o atendimento da supervisão do posto fiscal. Para acompanhar a resposta, use esses dois códigos:
https://portal.sefaz.pi.gov.br/acompanhe-sua-solicitacao
```

## Fontes e próxima revisão

- [LC 87/1996 — Câmara dos Deputados](https://www2.camara.leg.br/legin/fed/leicom/1996/leicomplementar-87-13-setembro-1996-370965-normaatualizada-pl.html).
- [LC 123/2006 — Câmara dos Deputados](https://www2.camara.leg.br/legin/fed/leicom/2006/leicomplementar-123-14-dezembro-2006-548099-normaatualizada-pl.html).
- [RICMS-PI — publicação original de 2023](https://www.diario.pi.gov.br/doe/files/diarios/anexo/5714d565-bd46-4f50-950d-7fa74dbdc549/DIARIO-OFICIAL-DO-ESTADO-DO-PIAUI-PUBLICACAO-N-47.pdf).

O texto estadual original não comprova a redação vigente; a aplicação do regime de transportadoras
conveniadas aos Correios também está pendente. Antes do uso real, revisar cada mensagem contra o motivo
do SIAT, a norma vigente e o procedimento do posto, registrar aprovador e data, e substituir campos
pendentes. Mudanças de conteúdo exigem nova revisão. Não prometer liberação, entrega ou prazo.

A fundamentação do sigilo fiscal, da emissão da NF-e e da NFA-e está registrada no
[guia do portal](ORIENTACAO_PORTAL.md). O limite pela data de postagem e a lista de anexos
são procedimentos informados pelo autor, com validação específica pendente. A orientação
não afirma proibição geral de WhatsApp nem sugere retroagir a data de documentos.
