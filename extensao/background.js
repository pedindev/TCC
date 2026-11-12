importScripts("site.js");

const hosts = {siat: "webas.sefaz.pi.gov.br", whatsapp: "web.whatsapp.com"};
const padroes = {
  siat: ["https://webas.sefaz.pi.gov.br/*", "http://webas.sefaz.pi.gov.br/*"],
  whatsapp: ["https://web.whatsapp.com/*"]
};
const paineis = new Set();
const emitidos = new Set();
let pulso = null;
let pulsando = false;
const identidade = chrome.storage.session.get("instancia").then(async dados => {
  const instancia = dados.instancia || crypto.randomUUID();
  await chrome.storage.session.set({instancia});
  return instancia;
});

function painelPermitido(url) {
  try {
    const u = new URL(url);
    return u.protocol === "http:" && ["127.0.0.1", "localhost"].includes(u.hostname)
      && u.port === "8000" && ["/", "/painel/"].includes(u.pathname);
  } catch (_) { return false; }
}

function iniciarPulso() {
  if (pulso) return;
  pulso = setInterval(async () => {
    if (pulsando) return;
    pulsando = true;
    try {
      await Promise.all([...paineis].map(async id => {
        try {
          const aba = await chrome.tabs.get(id);
          if (!painelPermitido(aba.url)) throw new Error();
          await chrome.tabs.sendMessage(id, {tipo: "pulso"});
        } catch (_) { paineis.delete(id); }
      }));
      if (!paineis.size) { clearInterval(pulso); pulso = null; }
    } finally { pulsando = false; }
  }, 1000);
}

async function inspecionar(sistema) {
  const abas = await chrome.tabs.query({url: padroes[sistema]});
  if (!abas.length) return {estado: "ausente", aba: null};
  if (abas.length !== 1) return {estado: "duplicada", aba: null};
  const aba = abas[0].id;
  try {
    const [retorno] = await chrome.scripting.executeScript({
      target: {tabId: aba}, func: operarSite, args: [sistema, "estado", "", 0]
    });
    return {estado: retorno?.result || "erro", aba};
  } catch (_) { return {estado: "erro", aba}; }
}

async function executar(comando) {
  const c = comando;
  if (!c || typeof c.id !== "string" || !Number.isInteger(c.aba)
      || typeof c.valor !== "string" || c.valor.length > 30000
      || !Number.isFinite(c.limite) || c.limite * 1000 <= Date.now()
      || c.limite * 1000 > Date.now() + 10000
      || !(c.sistema === "siat" && ["consultar", "abrir_consulta", "sair"].includes(c.acao)
        || c.sistema === "whatsapp" && c.acao === "colar") || emitidos.has(c.id)) return "falha";
  emitidos.add(c.id);
  if (emitidos.size > 1000) emitidos.delete(emitidos.values().next().value);
  try {
    const abas = await chrome.tabs.query({url: padroes[c.sistema]});
    if (abas.length !== 1 || abas[0].id !== c.aba
        || new URL(abas[0].url).hostname !== hosts[c.sistema]) return "falha";
    const [retorno] = await chrome.scripting.executeScript({
      target: {tabId: c.aba}, func: operarSite,
      args: [c.sistema, c.acao, c.valor, c.limite]
    });
    return retorno?.result || "incerto";
  } catch (_) {
    // Uma navegação pode destruir o contexto da saída. Confirme somente a rota de login.
    if (c.sistema === "siat") {
      try {
        const aba = await chrome.tabs.get(c.aba);
        const url = new URL(aba.url);
        if (url.hostname === hosts.siat && url.pathname.split(";")[0] === "/siatweb/faces/login.xhtml") {
          return c.acao === "sair" ? "ok" : "login";
        }
      } catch (_) { /* Aba fechada. */ }
    }
    return c.acao === "colar" ? "incerto" : "falha";
  }
}

chrome.runtime.onMessage.addListener((mensagem, remetente, responder) => {
  if (remetente.id !== chrome.runtime.id || !remetente.tab || !painelPermitido(remetente.url)) return;
  paineis.add(remetente.tab.id);
  iniciarPulso();
  (async () => {
    if (mensagem?.tipo === "registrar") return true;
    if (mensagem?.tipo === "estados") {
      const [siat, whatsapp] = await Promise.all([inspecionar("siat"), inspecionar("whatsapp")]);
      return {instancia: await identidade, estados: {siat, whatsapp}};
    }
    if (mensagem?.tipo === "executar") return executar(mensagem.comando);
    return null;
  })().then(responder, () => responder(null));
  return true;
});

// Retoma o heartbeat se o service worker for reiniciado pelo navegador.
chrome.tabs.query({url: ["http://127.0.0.1/*", "http://localhost/*"]}).then(abas => {
  for (const aba of abas) if (painelPermitido(aba.url)) paineis.add(aba.id);
  if (paineis.size) iniciarPulso();
});
