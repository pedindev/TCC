/* Estado apenas em memória. Sem localStorage, rastreios em URLs ou envio automático. */
(() => {
  const el = id => document.getElementById(id);
  let estado = null, enviando = false, online = false, buscando = false, geracao = 0, erroConexao = false;
  let proximaAtualizacao;
  let copiando = false;
  let atendimentoPosicionado = null;
  let rolagemAgendada = false;
  const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
  function ajustarMensagem() {
    el('mensagem').style.height = 'auto';
    el('mensagem').style.height = `${el('mensagem').scrollHeight + 2}px`;
  }
  function posicionarResultado() {
    // UI Automation pode selecionar a aba mantendo o foco na barra do navegador.
    // A página visível já pode rolar; document.hasFocus() bloqueava esse retorno.
    if (document.hidden || rolagemAgendada || !estado || estado.ocupado ||
        estado.fase !== 'pronto' || !estado.situacao ||
        atendimentoPosicionado === estado.atendimento) return;
    const atendimento = estado.atendimento;
    rolagemAgendada = true;
    ajustarMensagem();
    // Esperar o desenho da mensagem evita rolar antes de a caixa ganhar sua altura.
    requestAnimationFrame(() => requestAnimationFrame(() => {
      rolagemAgendada = false;
      if (document.hidden || !estado || estado.atendimento !== atendimento ||
          estado.ocupado || estado.fase !== 'pronto') return;
      el('resultado-titulo').focus({preventScroll: true});
      el('etapa-resultado').scrollIntoView({behavior: 'instant', block: 'start'});
      const posicao = el('resultado-titulo').getBoundingClientRect();
      if (posicao.top >= 0 && posicao.bottom <= window.innerHeight) {
        atendimentoPosicionado = atendimento;
      }
    }));
  }
  function botoes() {
    const ocupado = !online || enviando || copiando || !estado || estado.ocupado;
    el('consultar').disabled = ocupado || estado.fase !== 'inicial' || estado.modo === 'preparacao';
    el('rastreio').disabled = ocupado || estado.fase !== 'inicial';
    el('novo').disabled = !online || enviando || copiando || !estado;
    el('mensagem-opcao').disabled = ocupado;
    el('colar').disabled = ocupado || !estado.pode_colar || estado.colagem_tentada ||
      estado.sistemas.whatsapp.estado !== 'disponivel';
    const motivo = !online ? 'Aguardando conexão com o painel.'
      : !estado ? 'Aguardando o estado do atendimento.'
      : ocupado ? 'Aguarde a operação em andamento.'
      : estado.erro && estado.mensagem ? `${estado.aviso} ${estado.acao}`
      : estado.colagem_tentada ? 'A colagem já foi tentada. Confira a mensagem no WhatsApp.'
      : !estado.pode_colar ? (estado.aviso_catalogo || 'Consulte uma encomenda com orientação disponível.')
      : estado.sistemas.whatsapp.estado !== 'disponivel' ? estado.sistemas.whatsapp.texto : '';
    el('colar-motivo').textContent = motivo;
    el('colar-motivo').hidden = !motivo;
    el('cancelar').hidden = !estado || estado.fase !== 'contagem';
    el('cancelar').disabled = !online || enviando;
  }
  function mostrar(s) {
    const faseAnterior = estado?.fase;
    const primeiro = estado === null;
    const mudou = estado && estado.atendimento !== s.atendimento;
    estado = s;
    if (mudou || primeiro || s.rastreio) {
      el('rastreio').value = s.rastreio;
    }
    if (mudou || primeiro) {
      el('copia-status').textContent = '';
      el('copia-status').hidden = true;
    }
    if (s.fase !== faseAnterior && ['contagem', 'colando', 'colado', 'erro'].includes(s.fase)) {
      el('copia-status').hidden = true;
    }
    for (const nome of ['siat', 'whatsapp']) {
      el(nome + '-status').textContent = s.sistemas[nome].texto;
      el(nome + '-indicador').dataset.estado = s.sistemas[nome].estado;
    }
    el('aviso').textContent = s.aviso;
    el('acao').textContent = s.acao;
    el('andamento').dataset.erro = s.erro ? 'sim' : 'nao';
    el('andamento').setAttribute('aria-busy', String(s.ocupado));
    el('situacao').textContent = ({retida: 'Retida', liberada: 'Liberada'})[s.situacao] ||
      (s.erro ? 'Não confirmada' : 'Aguardando consulta');
    el('motivo').textContent = s.motivo || '—';
    if (el('mensagem').value !== s.mensagem) {
      el('mensagem').value = s.mensagem;
      ajustarMensagem();
    }
    el('versao').textContent = s.versao;
    el('catalogo-aviso').textContent = s.aviso_catalogo;
    el('catalogo-aviso').hidden = !s.aviso_catalogo;
    const opcoes = s.mensagens || [];
    const seletor = el('mensagem-opcao');
    const rotulos = opcoes.map((opcao, i) => `Mensagem ${i + 1} — ${opcao.titulo}`);
    if (JSON.stringify([...seletor.options].map(o => o.text)) !== JSON.stringify(rotulos)) {
      seletor.replaceChildren(...rotulos.map((rotulo, i) => new Option(rotulo, String(i))));
    }
    seletor.value = String(s.mensagem_indice || 0);
    el('opcoes-mensagens').hidden = opcoes.length < 2;
    el('contagem').hidden = s.fase !== 'contagem';
    el('contagem').textContent = `Colagem em ${s.segundos} segundos. Abra a conversa e clique no campo.`;
    botoes();
    posicionarResultado();
  }
  async function atualizar() {
    if (buscando || enviando) return;
    buscando = true;
    const geracaoPedido = geracao;
    const controle = new AbortController();
    const limite = setTimeout(() => controle.abort(), 8000);
    try {
      const r = await fetch('/api/estado/', {cache: 'no-store', signal: controle.signal});
      if (!r.ok) throw new Error();
      const s = await r.json();
      if (geracaoPedido !== geracao) return;
      online = true;
      if (erroConexao) { el('erro-local').hidden = true; erroConexao = false; }
      if (!enviando) mostrar(s);
    } catch {
      if (geracaoPedido !== geracao) return;
      online = false;
      erroConexao = true;
      el('erro-local').hidden = false;
      el('erro-local').textContent = 'Conexão com o painel interrompida. Confira se o servidor está aberto. A mensagem continua visível; verifique o WhatsApp antes de repetir uma colagem.';
      botoes();
    } finally { clearTimeout(limite); buscando = false; }
  }
  async function comando(acao, extras = {}) {
    if (enviando || !estado || !online) return;
    enviando = true;
    geracao++;
    botoes();
    el('erro-local').hidden = true;
    try {
      const r = await fetch(`/api/${acao}/`, {
        method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf},
        body: JSON.stringify({atendimento: estado.atendimento, token: estado.token, ...extras})
      });
      const s = await r.json();
      if (!r.ok) {
        el('erro-local').textContent = `${s.mensagem || 'Ação não concluída.'} ${s.acao || 'Atualize o painel.'}`;
        el('erro-local').hidden = false;
        return false;
      } else {
        mostrar(s);
        if (acao === 'novo') el('rastreio').value = '';
        return true;
      }
    } catch {
      online = false;
      erroConexao = true;
      el('erro-local').hidden = false;
      el('erro-local').textContent = 'Não foi possível confirmar a ação. Aguarde a reconexão e confira o navegador antes de tentar novamente.';
      return false;
    } finally {
      enviando = false; botoes();
      await atualizar();
    }
  }
  async function copiarEColar() {
    if (copiando || el('colar').disabled || !estado) return;
    const texto = el('mensagem').value;
    const atendimento = estado.atendimento;
    const token = estado.token;
    if (!texto || texto !== estado.mensagem) return;
    copiando = true;
    botoes();
    el('copia-status').textContent = 'Copiando a mensagem completa…';
    el('copia-status').hidden = false;
    try {
      // Cópia no clique, sem trim, reconstrução ou perda de links e quebras de linha.
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(texto);
      } else {
        el('mensagem').focus();
        el('mensagem').select();
        if (!document.execCommand('copy')) throw new Error('copia_indisponivel');
      }
      if (!estado || estado.atendimento !== atendimento || estado.token !== token ||
          estado.mensagem !== texto || estado.ocupado) {
        el('copia-status').textContent = 'O atendimento mudou durante a cópia. Confira a mensagem atual.';
        return;
      }
      el('copia-status').textContent = 'Mensagem copiada. Iniciando a contagem para colar automaticamente.';
      if (!await comando('colar')) {
        el('copia-status').hidden = false;
        el('copia-status').textContent = 'Mensagem copiada, mas a colagem não foi iniciada. Confira o aviso do painel.';
      }
    } catch {
      el('copia-status').textContent = 'O navegador não permitiu copiar a mensagem. Permita o acesso à área de transferência deste painel e clique novamente. A colagem não foi iniciada.';
    } finally {
      copiando = false;
      botoes();
    }
  }
  el('consulta').addEventListener('submit', e => {e.preventDefault(); comando('consultar', {codigo: el('rastreio').value.trim()});});
  el('novo').addEventListener('click', () => comando('novo'));
  el('colar').addEventListener('click', copiarEColar);
  el('cancelar').addEventListener('click', () => comando('cancelar'));
  el('mensagem-opcao').addEventListener('change', () => {
    comando('selecionar_mensagem', {indice: Number(el('mensagem-opcao').value)});
  });
  window.addEventListener('resize', ajustarMensagem);
  window.addEventListener('focus', posicionarResultado);
  async function acompanhar() {
    clearTimeout(proximaAtualizacao);
    await atualizar();
    clearTimeout(proximaAtualizacao);
    const intervalo = estado?.ocupado ? 500 : (document.hidden ? 3000 : 1000);
    proximaAtualizacao = setTimeout(acompanhar, intervalo);
  }
  document.addEventListener('visibilitychange', () => { if (!document.hidden) acompanhar(); });
  acompanhar();
})();
