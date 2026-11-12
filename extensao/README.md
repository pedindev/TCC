# Extensão de conexão do MVP

**Alternativa anterior, fora do fluxo padrão.** O operador agora usa o verificador
Windows integrado ao programa; não é necessário instalar esta extensão.

No Brave: `brave://extensions` → **Modo do desenvolvedor** → **Carregar sem compactação**
→ selecionar esta pasta. No Chrome, use `chrome://extensions`.
Atualize o painel em `http://127.0.0.1:8000/` depois de instalar ou recarregar a extensão.

Use as abas já abertas do SIAT e WhatsApp. Podem ficar em janelas diferentes do
mesmo navegador/perfil. Não é necessário abrir os sites por um script nem instalar
a extensão do ChatGPT. O servidor local deve estar executando e o painel aberto.

## Dados e funcionamento

- Permissões apenas para SIAT, WhatsApp e painel local. Sem acesso a histórico,
  cookies, senhas, depuração, todos os sites ou área de transferência.
- `storage.session` armazena somente uma identidade aleatória da instância da extensão.
  Não há armazenamento de rastreios, resultados, orientações ou conversas.
- A observação retorna só estados e IDs de abas; comandos são temporários, com prazo.
- Login é manual. Não seleciona conversas e nunca envia mensagens.
- A colagem só ocorre no campo único, vazio e focado, após solicitação do painel.
- Sem painel aberto, a comunicação para. Sem heartbeat por 12s, o servidor informa
  extensão desconectada. A suspensão do computador interrompe a observação.
- A extensão não altera o banco de orientações nem aprova textos em rascunho.

Não está publicada em loja. Em cada atualização dos arquivos, clique **Recarregar**
no cartão da extensão e atualize o painel. A validação usa páginas fictícias.
A leitura dos detalhes da retenção ainda depende do mapeamento do SIAT real;
os controles do WhatsApp e os eventos dos menus do SIAT precisam de validação real.
