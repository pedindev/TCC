/* Executada no mundo isolado da extensão. Retorna apenas enums, nunca dados pessoais. */
async function operarSite(sistema, acao, valor, limite) {
  const host = sistema === "siat" ? "webas.sefaz.pi.gov.br" : "web.whatsapp.com";
  if (location.hostname !== host) return "falha";
  const visivel = e => !!e && !!e.getClientRects().length && getComputedStyle(e).visibility !== "hidden";
  const unico = lista => lista.length === 1 ? lista[0] : null;
  const texto = e => (e.innerText || e.textContent || "").trim().replace(/\s+/g, " ");
  const controles = (raiz, nome) => [...raiz.querySelectorAll('a,button,input[type="submit"],input[type="button"],[role="button"]')]
    .filter(e => visivel(e) && (texto(e) === nome || e.value === nome || e.getAttribute("aria-label") === nome));
  const saida = () => unico([...document.querySelectorAll("a")].filter(e => visivel(e)
    && (/^Sair(?: Sair)?$/.test(texto(e)) || e.querySelector('img[alt="Sair"]'))));
  const login = () => location.pathname.split(";")[0] === "/siatweb/faces/login.xhtml";
  const formulario = () => document.querySelector('form[id="frmConsultar"]');
  const editor = () => unico([...document.querySelectorAll('#main footer [contenteditable="true"][role="textbox"]')].filter(visivel));
  const valido = () => Date.now() < limite * 1000;
  const esperar = async teste => {
    const prazo = Math.min(limite * 1000, Date.now() + 5000);
    while (Date.now() < prazo) {
      if (teste()) return true;
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return false;
  };
  if (acao === "estado") {
    if (sistema === "whatsapp") return editor() ? "pronto" : "aberto";
    if (login()) return "login";
    if (!saida()) return "desconhecida";
    if (visivel(formulario())) return "consulta";
    const menu = [...document.querySelectorAll("a,span,button")].some(e => visivel(e) && texto(e) === "Trânsito");
    return menu ? "inicio" : "desconhecida";
  }
  if (!valido()) return "demora";
  if (sistema === "whatsapp" && acao === "colar") {
    const campo = editor();
    if (!campo || !document.hasFocus() || document.activeElement !== campo
        || campo.innerText.trim() || campo.querySelector("img,video")) return "sem_foco";
    if (!valido()) return "demora";
    // Edição nativa apenas no campo que o operador focalizou. Não há Enter nem envio.
    const inseriu = document.execCommand("insertText", false, valor);
    const normalizar = s => s.replace(/\r\n/g, "\n").replace(/\u00a0/g, " ").replace(/\n{3,}/g, "\n\n").trim();
    return inseriu && normalizar(campo.innerText) === normalizar(valor) ? "ok" : "incerto";
  }
  if (sistema !== "siat") return "falha";
  if (login()) return "login";
  if (!saida()) return "falha";
  if (acao === "sair") {
    if (!valido()) return "demora";
    saida().click();
    return await esperar(login) ? "ok" : "falha";
  }
  if (acao === "abrir_consulta") {
    if (visivel(formulario())) return "ok";
    for (const nome of ["Trânsito", "Notificação Correios", "Consultar Notificação"]) {
      // Aceita o span interno, mas aciona o link/botão efetivo quando presente.
      const itens = [...document.querySelectorAll("a,button,span")].filter(e => visivel(e) && texto(e) === nome);
      const item = itens.find(e => !itens.some(outro => outro !== e && e.contains(outro)));
      if (!item || !valido()) return "falha";
      const alvo = item.closest("a,button") || item;
      for (const tipo of ["mouseover", "mouseenter", "mousemove"]) alvo.dispatchEvent(new MouseEvent(tipo, {bubbles: true}));
      if (nome === "Consultar Notificação") alvo.click();
      else await new Promise(resolve => setTimeout(resolve, 150));
    }
    return await esperar(() => visivel(formulario()) || login()) ? (login() ? "login" : "ok") : "demora";
  }
  if (acao !== "consultar" || !valor.trim() || /\s/.test(valor) || valor.length > 64) return "falha";
  const form = formulario();
  if (!visivel(form)) return "falha";
  const seletor = unico([...form.querySelectorAll("select")].filter(visivel));
  const campo = unico([...form.querySelectorAll('input[type="text"],input:not([type])')].filter(visivel));
  const botao = unico(controles(form, "Consultar"));
  const opcao = seletor && [...seletor.options].find(o => o.text.trim() === "Cód. Rastreio");
  if (!opcao || !campo || !botao) return "falha";
  seletor.value = opcao.value;
  seletor.dispatchEvent(new Event("change", {bubbles: true}));
  // O seletor pode provocar reconstrução assíncrona: não acione controles já removidos.
  await new Promise(resolve => setTimeout(resolve, 200));
  if (!form.isConnected || !campo.isConnected || !valido()) return "falha";
  Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set.call(campo, valor);
  campo.dispatchEvent(new Event("input", {bubbles: true}));
  campo.dispatchEvent(new Event("change", {bubbles: true}));
  if (!valido()) return "demora";
  botao.click();
  if (!await esperar(() => !form.isConnected || login())) return "demora";
  if (login()) return "login";
  const tabela = document.getElementById("frmConsultar:dTableNotificacao");
  if (!visivel(formulario()) || !visivel(tabela)) return "falha";
  // Lê exclusivamente o marcador de vazio; não exporta linhas nem dados do contribuinte.
  const vazio = [...tabela.querySelectorAll("td,span")].some(e => visivel(e) && texto(e) === "Nenhuma Notificação encontrada!");
  return vazio ? "vazio" : "atualizado";
}
