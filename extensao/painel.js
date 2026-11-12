/* Ponte no painel local: nada é gravado; a proteção CSRF continua obrigatória. */
(() => {
  if (location.port !== "8000" || !["/", "/painel/"].includes(location.pathname)) return;
  let ocupada = false;
  let resposta = null;
  async function sincronizar() {
    if (ocupada) return;
    const csrf = document.querySelector('[name="csrfmiddlewaretoken"]')?.value;
    if (!csrf) return;
    ocupada = true;
    try {
      const dados = await chrome.runtime.sendMessage({tipo: "estados"});
      if (!dados?.estados) return;
      const controle = new AbortController();
      const prazo = setTimeout(() => controle.abort(), 6000);
      let retorno;
      try {
        retorno = await fetch("/api/extensao/sincronizar/", {
          method: "POST", credentials: "same-origin", cache: "no-store",
          headers: {"Content-Type": "application/json", "X-CSRFToken": csrf},
          body: JSON.stringify({...dados, resposta}), signal: controle.signal
        });
      } finally { clearTimeout(prazo); }
      if (!retorno.ok) return;
      resposta = null;
      const {comando} = await retorno.json();
      if (comando) {
        const resultado = await chrome.runtime.sendMessage({tipo: "executar", comando});
        resposta = {id: comando.id, resultado: resultado || "incerto"};
        // Reduz a permanência do texto e do rastreio em memória.
        comando.valor = "";
      }
    } catch (_) {
      // O painel informa indisponibilidade quando o heartbeat vence. Sem logs de dados.
    } finally {
      ocupada = false;
      if (resposta) setTimeout(sincronizar, 50);
    }
  }
  chrome.runtime.onMessage.addListener((mensagem, remetente) => {
    if (remetente.id === chrome.runtime.id && mensagem?.tipo === "pulso") sincronizar();
  });
  chrome.runtime.sendMessage({tipo: "registrar"}).catch(() => {});
  sincronizar();
})();
