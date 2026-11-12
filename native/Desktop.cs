// UI Automation local. Retorna apenas estados e o campo de retenção autorizado, nunca credenciais.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows.Automation;

public static class MvpDesktop
{
    public static int ProcessoTeste = 0; // Exclusivamente o PID criado pelo teste isolado.
    static long limite;
    static string referenciaAtual;
    static IntPtr janelaAtual;
    static Aba painelOrigem;
    static long painelValidade;
    static System.Windows.Forms.NativeWindow clipboardOwner;
    // Autorização transitória: a lupa só pode usar a resposta desta pesquisa.
    class ConsultaAtual { public string referencia, codigo, botao; public long validade; }
    static ConsultaAtual consultaAtual;
    class DetalheAtual {
        public string referencia, codigo;
        public long validade;
        public HashSet<string> anteriores;
    }
    static DetalheAtual detalheAtual;
    static readonly TreeWalker walker = TreeWalker.ControlViewWalker;
    [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] static extern bool ShowWindowAsync(IntPtr h, int n);
    [DllImport("user32.dll")] static extern bool IsIconic(IntPtr h);
    [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] static extern short GetAsyncKeyState(int key);
    [DllImport("user32.dll")] static extern uint SendInput(uint count, INPUT[] inputs, int size);
    [DllImport("user32.dll")] static extern bool OpenClipboard(IntPtr h);
    [DllImport("user32.dll")] static extern bool CloseClipboard();
    [DllImport("user32.dll")] static extern bool EmptyClipboard();
    [DllImport("user32.dll")] static extern IntPtr SetClipboardData(uint format, IntPtr memory);
    [DllImport("user32.dll")] static extern uint GetClipboardSequenceNumber();
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern uint RegisterClipboardFormat(string name);
    [DllImport("kernel32.dll")] static extern IntPtr GlobalAlloc(uint flags, UIntPtr size);
    [DllImport("kernel32.dll")] static extern IntPtr GlobalLock(IntPtr memory);
    [DllImport("kernel32.dll")] static extern bool GlobalUnlock(IntPtr memory);
    [DllImport("kernel32.dll")] static extern IntPtr GlobalFree(IntPtr memory);
    [StructLayout(LayoutKind.Sequential)] struct INPUT { public uint type; public INPUTDATA data; }
    [StructLayout(LayoutKind.Explicit)] struct INPUTDATA {
        [FieldOffset(0)] public KEYBDINPUT key;
        [FieldOffset(0)] public MOUSEINPUT mouse;
    }
    [StructLayout(LayoutKind.Sequential)] struct KEYBDINPUT {
        public ushort vk, scan; public uint flags, time; public IntPtr extra;
    }
    [StructLayout(LayoutKind.Sequential)] struct MOUSEINPUT {
        public int x, y; public uint data, flags, time; public IntPtr extra;
    }
    class Aba { public AutomationElement tab, janela; public string referencia, sistema; }

    static Dictionary<string, object> Resposta(string resultado) {
        return new Dictionary<string, object> { {"resultado", resultado} };
    }
    static object Erro(Exception erro, string resultado) {
        var resposta=Resposta(resultado);
        if (ProcessoTeste>0) resposta["diagnosticoTeste"]=erro.GetType().Name+":"+erro.StackTrace;
        return resposta;
    }
    static long Agora() { return (long)(DateTime.UtcNow - new DateTime(1970,1,1)).TotalMilliseconds; }
    static void Prazo() { if (Agora() >= limite) throw new TimeoutException(); }
    static bool Visivel(AutomationElement e) { return !e.Current.IsOffscreen; }
    static string Identidade(AutomationElement e) { return string.Join(".", e.GetRuntimeId()); }
    static bool Selecionada(AutomationElement e) {
        object p;
        return e.TryGetCurrentPattern(SelectionItemPattern.Pattern, out p)
            && ((SelectionItemPattern)p).Current.IsSelected;
    }
    // Não entra em Document: a observação de abas não percorre conversas ou registros.
    static List<AutomationElement> Moldura(AutomationElement raiz, ControlType tipo) {
        var resultado = new List<AutomationElement>();
        var fila = new Queue<AutomationElement>(); fila.Enqueue(raiz);
        int vistos = 0;
        while (fila.Count > 0 && vistos++ < 1200) {
            Prazo(); var e = fila.Dequeue();
            if (e.Current.ControlType == tipo) resultado.Add(e);
            if (e.Current.ControlType == ControlType.Document) continue;
            for (var filho = walker.GetFirstChild(e); filho != null; filho = walker.GetNextSibling(filho)) {
                fila.Enqueue(filho);
            }
        }
        if (fila.Count > 0) throw new InvalidOperationException();
        return resultado;
    }
    static List<Aba> Abas() {
        var lista = new List<Aba>();
        var janelas = AutomationElement.RootElement.FindAll(TreeScope.Children,
            new PropertyCondition(AutomationElement.ClassNameProperty, "Chrome_WidgetWin_1"));
        foreach (AutomationElement janela in janelas) {
            Prazo();
            int pid = janela.Current.ProcessId;
            if (ProcessoTeste > 0 && pid != ProcessoTeste) continue;
            string processo = Process.GetProcessById(pid).ProcessName.ToLowerInvariant();
            if (processo != "chrome" && processo != "brave") continue;
            foreach (var tab in Moldura(janela, ControlType.TabItem)) {
                string nome = tab.Current.Name;
                nome = Regex.Replace(nome,@"^(?:Uso da memória em |Memory usage (?:in|for) )","",RegexOptions.IgnoreCase);
                string sistema = Regex.IsMatch(nome, @"^SIAT(?:\s|[-–])", RegexOptions.IgnoreCase) ? "siat"
                    : Regex.IsMatch(nome, @"^(?:\(\d+\)\s*)?WhatsApp(?:\s|:|$)", RegexOptions.IgnoreCase) ? "whatsapp"
                    : Regex.IsMatch(nome, @"^Painel\s*•\s*MVP(?:\s|:|$)",RegexOptions.IgnoreCase) ? "painel" : null;
                if (sistema != null) lista.Add(new Aba { tab=tab, janela=janela, sistema=sistema,
                    referencia=janela.Current.NativeWindowHandle.ToString()+":"+Identidade(tab) });
            }
        }
        return lista;
    }
    static Aba Unica(List<Aba> abas, string sistema, string referencia) {
        Aba achada = null;
        foreach (var a in abas) if (a.sistema == sistema) {
            if (achada != null) throw new InvalidOperationException(); achada = a;
        }
        if (achada == null || (referencia.Length > 0 && achada.referencia != referencia))
            throw new InvalidOperationException();
        return achada;
    }
    static Uri Endereco(Aba aba) {
        AutomationElement barra = null;
        foreach (var e in Moldura(aba.janela, ControlType.Edit)) {
            string nome = e.Current.Name;
            if (nome == "Address and search bar" || nome == "Barra de endereço e pesquisa"
                || nome == "Barra de endereços e pesquisa" || nome == "Barra de endereço e de pesquisa") {
                if (barra != null) throw new InvalidOperationException(); barra = e;
            }
        }
        if (barra == null) throw new InvalidOperationException();
        string valor = ((ValuePattern)barra.GetCurrentPattern(ValuePattern.Pattern)).Current.Value;
        // Chrome omite o esquema do endereço local. O painel é HTTP, os sites
        // externos continuam usando HTTPS como padrão quando o esquema é omitido.
        if (!valor.Contains("://")) valor = (aba.sistema=="painel" ? "http://" : "https://") + valor;
        Uri url; if (!Uri.TryCreate(valor, UriKind.Absolute, out url)) throw new InvalidOperationException();
        if (aba.sistema=="painel") {
            if (url.Scheme!="http" || (url.Host!="127.0.0.1" && url.Host!="localhost")
                || url.Port!=8000 || (url.AbsolutePath!="/" && url.AbsolutePath!="/painel/")
                || url.UserInfo!="")
                throw new InvalidOperationException();
            return url;
        }
        string esperado = aba.sistema == "siat" ? "webas.sefaz.pi.gov.br" : "web.whatsapp.com";
        if (url.Host != esperado || !(url.Scheme == "https" || aba.sistema == "siat" && url.Scheme == "http"))
            throw new InvalidOperationException();
        return url;
    }
    static AutomationElement Documento(Aba aba) {
        long ate=Math.Min(limite,Agora()+1500);
        while (Agora()<ate) {
            var docs = Moldura(aba.janela, ControlType.Document);
            AutomationElement unico = null;
            foreach (var d in docs) if (Visivel(d) &&
                (aba.sistema=="siat" ? Regex.IsMatch(d.Current.Name,@"^SIAT(?:\s|[-–])",RegexOptions.IgnoreCase)
                : Regex.IsMatch(d.Current.Name,@"^(?:\(\d+\)\s*)?WhatsApp(?:\s|$)",RegexOptions.IgnoreCase))) {
                if (unico != null) throw new InvalidOperationException("documentos_ambiguos"); unico = d;
            }
            if (unico!=null) return unico;
            Thread.Sleep(100);
        }
        throw new InvalidOperationException("documento_ausente");
    }
    static List<AutomationElement> Encontrar(AutomationElement doc, ControlType tipo, string nome) {
        var condicoes = new List<Condition>();
        if (tipo != null) condicoes.Add(new PropertyCondition(AutomationElement.ControlTypeProperty, tipo));
        if (nome != null) condicoes.Add(new PropertyCondition(AutomationElement.NameProperty, nome));
        Condition condicao = condicoes.Count == 1 ? condicoes[0] : new AndCondition(condicoes.ToArray());
        var lista = new List<AutomationElement>();
        foreach (AutomationElement e in doc.FindAll(TreeScope.Descendants, condicao)) {
            Prazo(); if (Visivel(e)) lista.Add(e);
        }
        return lista;
    }
    static AutomationElement Um(AutomationElement doc, ControlType tipo, string nome) {
        var lista = Encontrar(doc,tipo,nome);
        if (lista.Count != 1) throw new InvalidOperationException(); return lista[0];
    }
    static string EstadoSiat(Aba aba) {
        var url = Endereco(aba);
        if (url.AbsolutePath.Split(';')[0] == "/siatweb/faces/login.xhtml") return "login";
        var doc = Documento(aba);
        if (Encontrar(doc,ControlType.Hyperlink,"Sair").Count != 1
            && Encontrar(doc,ControlType.Hyperlink,"Sair Sair").Count != 1) return "desconhecida";
        if (CamposRetencao(doc).FindAll(Visivel).Count>0) return "detalhes";
        if (Encontrar(doc,ControlType.Button,"Consultar").Count == 1
            && Encontrar(doc,ControlType.ComboBox,null).Count == 1
            && Encontrar(doc,ControlType.Edit,null).Count == 1) return "consulta";
        if (Encontrar(doc,null,"Trânsito").Count > 0) return "inicio";
        return "desconhecida";
    }
    static void Guarda(Aba aba) {
        Prazo();
        if (!Selecionada(aba.tab) || GetForegroundWindow() != (IntPtr)aba.janela.Current.NativeWindowHandle)
            throw new InvalidOperationException("foco");
        Endereco(aba);
    }
    static void Ativar(Aba aba) {
        consultaAtual=null;
        painelOrigem=null;
        var paineis=Abas().FindAll(delegate(Aba a) {return a.sistema=="painel";});
        // Prefere a aba que iniciou a consulta. Se o foco já mudou, só usa
        // alternativa quando existe um único painel; a URL é conferida no retorno.
        foreach (var origem in paineis) if (Selecionada(origem.tab)
            && GetForegroundWindow()==(IntPtr)origem.janela.Current.NativeWindowHandle) {
            Endereco(origem); painelOrigem=origem;
        }
        if (painelOrigem==null && paineis.Count==1) painelOrigem=paineis[0];
        painelValidade=Agora()+360000;
        var h = (IntPtr)aba.janela.Current.NativeWindowHandle;
        if (IsIconic(h)) ShowWindowAsync(h, 9);
        SetForegroundWindow(h);
        ((SelectionItemPattern)aba.tab.GetCurrentPattern(SelectionItemPattern.Pattern)).Select();
        aba.tab.SetFocus(); Thread.Sleep(150); Guarda(aba);
        referenciaAtual = aba.referencia; janelaAtual = h;
    }
    static string RetornarPainel(List<Aba> abas) {
        var origem=painelOrigem; painelOrigem=null;
        if (origem==null || Agora()>painelValidade) return "painel_indisponivel";
        Aba destino=null;
        foreach (var aba in abas) if (aba.sistema=="painel" && aba.referencia==origem.referencia)
            destino=aba;
        if (destino==null) {
            // O Chrome pode recriar o objeto acessível da aba. Não depender só
            // desse ID: procurar um painel único na mesma janela capturada.
            var candidatos=abas.FindAll(delegate(Aba a) {
                return a.sistema=="painel" && a.janela.Current.NativeWindowHandle==origem.janela.Current.NativeWindowHandle;
            });
            if (candidatos.Count==1) destino=candidatos[0];
        }
        if (destino==null) return "painel_indisponivel";
        if (Selecionada(destino.tab) && GetForegroundWindow()==(IntPtr)destino.janela.Current.NativeWindowHandle) {
            Endereco(destino); return "ok";
        }
        // Só troca o foco enquanto o operador ainda aguarda no SIAT.
        var siat=Unica(abas,"siat",referenciaAtual);
        Guarda(siat);
        var h=(IntPtr)destino.janela.Current.NativeWindowHandle;
        if (IsIconic(h)) ShowWindowAsync(h,9);
        SetForegroundWindow(h);
        ((SelectionItemPattern)destino.tab.GetCurrentPattern(SelectionItemPattern.Pattern)).Select();
        destino.tab.SetFocus();
        long ate=Math.Min(limite,Agora()+2000);
        while (Agora()<ate) {
            Thread.Sleep(100);
            if (Selecionada(destino.tab) && GetForegroundWindow()==h) {
                Endereco(destino); return "ok";
            }
        }
        return "painel_indisponivel";
    }
    static void Invocar(Aba aba, AutomationElement e) {
        Guarda(aba);
        ((InvokePattern)e.GetCurrentPattern(InvokePattern.Pattern)).Invoke();
    }
    static string PrepararConsulta(Aba aba) {
        consultaAtual=null; detalheAtual=null;
        if (EstadoSiat(aba)=="login") return "login";
        var doc=Documento(aba);
        var campos=CamposRetencao(doc).FindAll(Visivel);
        if (campos.Count==0) return "sem_detalhes";
        if (campos.Count!=1) return "detalhes_ambiguos";
        // Botão completo fornecido pelo autor: frmVisualizar:j_idt98 / Fechar.
        // Não mistura o X do cabeçalho com esse botão nem usa o link Sair.
        AutomationElement fechar=null;
        var exatos=Encontrar(doc,ControlType.Button,"Fechar").FindAll(delegate(AutomationElement e) {
            return e.Current.IsEnabled && e.Current.AutomationId=="frmVisualizar:j_idt98";
        });
        if (exatos.Count>1) return "fechar_ambiguo";
        if (exatos.Count==1) fechar=exatos[0];
        // Caso o Chrome não exporte o id HTML, restringe o nome Fechar ao
        // contêiner do campo de retenção, antes de alcançar o formulário de consulta.
        var raiz=walker.GetParent(campos[0]);
        for (int nivel=0;fechar==null && raiz!=null && nivel<16;nivel++,raiz=walker.GetParent(raiz)) {
            Prazo();
            if (Automation.Compare(raiz,doc)) break;
            if (raiz.FindFirst(TreeScope.Descendants,
                new PropertyCondition(AutomationElement.NameProperty,"Consultar"))!=null) break;
            var candidatos=new List<AutomationElement>();
            foreach (var e in Encontrar(raiz,ControlType.Button,"Fechar"))
                if (e.Current.IsEnabled && string.IsNullOrEmpty(e.Current.AutomationId))
                    candidatos.Add(e);
            if (candidatos.Count>1) return "fechar_ambiguo";
            if (candidatos.Count==1) {fechar=candidatos[0];break;}
        }
        if (fechar==null) return "fechar_indisponivel";
        Invocar(aba,fechar);
        while (Agora()<limite) {
            Thread.Sleep(100); Guarda(aba);
            string estado=EstadoSiat(aba);
            if (estado=="login") return "login";
            if (CamposRetencao(Documento(aba)).FindAll(Visivel).Count==0 && estado=="consulta")
                return "detalhes_fechados";
        }
        return "fechar_nao_confirmado";
    }
    static string Abrir(Aba aba) {
        if (EstadoSiat(aba) == "consulta") return "ok";
        foreach (string nome in new [] {"Trânsito", "Notificação Correios", "Consultar Notificação"}) {
            Guarda(aba); var doc = Documento(aba);
            var candidatos = Encontrar(doc, ControlType.Hyperlink, nome);
            if (candidatos.Count == 0) candidatos = Encontrar(doc,ControlType.Button,nome);
            if (candidatos.Count != 1) return "falha";
            var e = candidatos[0];
            if (nome == "Consultar Notificação") Invocar(aba,e);
            else {
                // Coordenada obtida do controle atual, nunca posição fixa de um print.
                var ponto = e.GetClickablePoint(); Guarda(aba);
                SetCursorPos((int)ponto.X,(int)ponto.Y); Thread.Sleep(200);
            }
        }
        while (Agora() < limite) {
            string estado = EstadoSiat(aba);
            if (estado == "login") return "login";
            if (estado == "consulta") return "ok";
            Thread.Sleep(100);
        }
        return "demora";
    }
    static string Consultar(Aba aba, string codigo) {
        consultaAtual=null;
        if (codigo.Length == 0 || codigo.Length > 64 || Regex.IsMatch(codigo,@"\s")) return "falha";
        if (EstadoSiat(aba) == "login") return "login";
        var doc = Documento(aba);
        var seletor = Um(doc,ControlType.ComboBox,null);
        object padrao;
        string selecionado = "";
        if (seletor.TryGetCurrentPattern(ValuePattern.Pattern,out padrao))
            selecionado = ((ValuePattern)padrao).Current.Value;
        if (selecionado != "Cód. Rastreio") {
            Guarda(aba);
            if (seletor.TryGetCurrentPattern(ExpandCollapsePattern.Pattern,out padrao))
                ((ExpandCollapsePattern)padrao).Expand();
            Thread.Sleep(100);
            var opcao = Um(Documento(aba),ControlType.ListItem,"Cód. Rastreio");
            Guarda(aba);
            ((SelectionItemPattern)opcao.GetCurrentPattern(SelectionItemPattern.Pattern)).Select();
        }
        doc = Documento(aba);
        var campo = Um(doc,ControlType.Edit,null);
        var botao = Um(doc,ControlType.Button,"Consultar");
        if (campo.Current.IsPassword) return "falha";
        Guarda(aba); ((ValuePattern)campo.GetCurrentPattern(ValuePattern.Pattern)).SetValue(codigo);
        string anterior = Identidade(botao);
        Invocar(aba,botao);
        while (Agora() < limite) {
            Thread.Sleep(100); Guarda(aba);
            if (EstadoSiat(aba) == "login") return "login";
            var atual = Encontrar(Documento(aba),ControlType.Button,"Consultar");
            if (atual.Count == 1 && Identidade(atual[0]) != anterior) {
                if (EstadoSiat(aba) != "consulta") return "falha";
                if (Encontrar(Documento(aba),ControlType.Text,"Nenhuma Notificação encontrada!").Count > 0)
                    return "vazio";
                consultaAtual=new ConsultaAtual {referencia=aba.referencia,codigo=codigo,
                    botao=Identidade(atual[0]),validade=Agora()+30000};
                return "atualizado";
            }
        }
        return "demora"; // Marcador antigo de vazio jamais provoca logout.
    }
    static string Sair(Aba aba) {
        consultaAtual=null;
        var doc = Documento(aba);
        var links = Encontrar(doc,ControlType.Hyperlink,"Sair");
        if (links.Count == 0) links = Encontrar(doc,ControlType.Hyperlink,"Sair Sair");
        if (links.Count != 1) return "falha";
        Invocar(aba,links[0]);
        while (Agora() < limite) {
            Thread.Sleep(100);
            if (EstadoSiat(aba) == "login") return "ok";
        }
        return "demora";
    }
    static string AbrirDetalhes(Aba aba, string codigo) {
        detalheAtual=null;
        var consulta=consultaAtual;
        // Consome antes do clique: erro ou navegação não permitem uma segunda tentativa.
        consultaAtual=null;
        if (consulta==null || consulta.validade<Agora() || consulta.referencia!=aba.referencia
            || consulta.codigo!=codigo) return "resultado_nao_confirmado";
        Guarda(aba);
        var doc=Documento(aba);
        if (Identidade(Um(doc,ControlType.Button,"Consultar"))!=consulta.botao)
            return "resultado_nao_confirmado";
        var campo=Um(doc,ControlType.Edit,null);
        if (((ValuePattern)campo.GetCurrentPattern(ValuePattern.Pattern)).Current.Value!=codigo)
            return "resultado_nao_confirmado";
        AutomationElement botao=null, celulaRastreio=null;
        int correspondencias=0;
        // Escopo estrutural: tabela com cabeçalhos conhecidos, linha do rastreio,
        // coluna Opções. Nunca procura o span genérico na página inteira.
        var tabelas=doc.FindAll(TreeScope.Descendants,
            new PropertyCondition(AutomationElement.IsTablePatternAvailableProperty,true));
        foreach (AutomationElement tabela in tabelas) {
            Prazo(); if (!Visivel(tabela)) continue;
            object p;
            if (!tabela.TryGetCurrentPattern(GridPattern.Pattern,out p)) continue;
            var grid=(GridPattern)p;
            var headers=((TablePattern)tabela.GetCurrentPattern(TablePattern.Pattern)).Current.GetColumnHeaders();
            if (headers.Length!=grid.Current.ColumnCount || grid.Current.RowCount>200) continue;
            int colunaCodigo=-1, colunaOpcoes=-1;
            for (int i=0;i<headers.Length;i++) {
                string nome=headers[i].Current.Name.Trim();
                if (nome=="Cód. Rastreio") {if(colunaCodigo>=0) return "linha_ambigua"; colunaCodigo=i;}
                if (nome=="Opções") {if(colunaOpcoes>=0) return "linha_ambigua"; colunaOpcoes=i;}
            }
            if (colunaCodigo<0 || colunaOpcoes<0) continue;
            for (int r=0;r<grid.Current.RowCount;r++) {
                Prazo(); var celula=grid.GetItem(r,colunaCodigo);
                bool corresponde=celula.Current.Name.Trim()==codigo ||
                    Encontrar(celula,ControlType.Text,codigo).Count==1;
                if (!corresponde) continue;
                correspondencias++;
                if (correspondencias>1) return "linha_ambigua";
                celulaRastreio=celula;
                var opcoes=grid.GetItem(r,colunaOpcoes);
                var botoes=Encontrar(opcoes,ControlType.Button,null);
                if (botoes.Count==1 && LupaConhecida(botoes[0])) botao=botoes[0];
            }
        }
        if (correspondencias!=1) return "linha_nao_confirmada";
        if (botao==null) return "lupa_indisponivel";
        // Reconfere o vínculo imediatamente antes da ação.
        Guarda(aba);
        if (celulaRastreio.Current.Name.Trim()!=codigo &&
            Encontrar(celulaRastreio,ControlType.Text,codigo).Count!=1) return "linha_nao_confirmada";
        var anteriores=new HashSet<string>();
        foreach (var anterior in CamposRetencao(doc)) {
            // Um detalhe já visível pode pertencer ao caso anterior: não reutilizar.
            if (Visivel(anterior)) return "detalhe_anterior_aberto";
            anteriores.Add(Identidade(anterior));
        }
        Invocar(aba,botao);
        detalheAtual=new DetalheAtual {referencia=aba.referencia,codigo=codigo,
            validade=Agora()+30000,anteriores=anteriores};
        // O onclick fornecido executa dlgVisualizar.show() e atualiza frmVisualizar.
        // Aciona o botão normal; não chama o AJAX diretamente nem presume dados carregados.
        return "detalhes_acionados";
    }
    static List<AutomationElement> CamposRetencao(AutomationElement doc) {
        var campos=new List<AutomationElement>();
        var edits=doc.FindAll(TreeScope.Descendants,
            new PropertyCondition(AutomationElement.ControlTypeProperty,ControlType.Edit));
        foreach (AutomationElement campo in edits) {
            Prazo();
            string id=campo.Current.AutomationId;
            bool corresponde=id=="frmVisualizar:j_idt68";
            // Sem id exportado, aceitar somente vínculo acessível explícito ao rótulo.
            // Não escolher por coordenada nem ler valores dos demais campos.
            if (string.IsNullOrEmpty(id)) {
                var label=campo.Current.LabeledBy;
                corresponde=campo.Current.Name.Trim()=="Inf. Adicionais:" ||
                    (label!=null && label.Current.Name.Trim()=="Inf. Adicionais:");
            }
            if (corresponde && !campo.Current.IsPassword) campos.Add(campo);
        }
        return campos;
    }
    static object LerRetencao(Aba aba, string codigo) {
        var detalhe=detalheAtual;
        detalheAtual=null; // Uma tentativa vinculada ao clique desta consulta.
        if (detalhe==null || detalhe.validade<Agora() || detalhe.referencia!=aba.referencia
            || detalhe.codigo!=codigo) return Resposta("resultado_nao_confirmado");
        string ultima=null, identidade=null;
        long estavelDesde=0;
        while (Agora()<limite) {
            Guarda(aba);
            var campos=CamposRetencao(Documento(aba)).FindAll(Visivel);
            if (campos.Count>1) return Resposta("campo_ambiguo");
            if (campos.Count==1 && !detalhe.anteriores.Contains(Identidade(campos[0]))) {
                object p;
                if (!campos[0].TryGetCurrentPattern(ValuePattern.Pattern,out p)
                    || !((ValuePattern)p).Current.IsReadOnly) return Resposta("campo_incompativel");
                string texto=((ValuePattern)p).Current.Value;
                if (texto.Length>250) return Resposta("campo_incompativel");
                string atual=Identidade(campos[0]);
                if (!string.IsNullOrWhiteSpace(texto)) {
                    if (texto!=ultima || atual!=identidade) {
                        ultima=texto; identidade=atual; estavelDesde=Agora();
                    } else if (Agora()-estavelDesde>=800) {
                        Guarda(aba);
                        var resposta=Resposta("retencao_lida");
                        resposta["descricao"]=texto;
                        return resposta;
                    }
                } else { ultima=null; identidade=null; }
            } else { ultima=null; identidade=null; }
            Thread.Sleep(100);
        }
        return Resposta("campo_indisponivel");
    }
    static bool LupaConhecida(AutomationElement botao) {
        if (!botao.Current.IsEnabled || botao.Current.Name.Trim()!="ui-button") return false;
        string id=botao.Current.AutomationId;
        // O Chrome pode não exportar o id HTML por UIA. Nesse caso, o vínculo com
        // linha/coluna e o nome acessível continuam obrigatórios. Um id divergente é recusado.
        return string.IsNullOrEmpty(id) || Regex.IsMatch(id,
            @"^frmConsultar:dTableNotificacao:[0-9]+:j_idt47$");
    }
    static string Conteudo(AutomationElement campo, int maximo) {
        object p;
        if (campo.TryGetCurrentPattern(ValuePattern.Pattern,out p))
            return ((ValuePattern)p).Current.Value;
        if (campo.TryGetCurrentPattern(TextPattern.Pattern,out p))
            return ((TextPattern)p).DocumentRange.GetText(maximo);
        throw new InvalidOperationException();
    }
    public static bool RotuloCompositor(string nome) {
        if (nome==null) return false;
        nome=nome.Trim();
        // O WhatsApp acrescenta contexto ao nome acessível do editor. Não é
        // necessário ler, registrar ou interpretar esse complemento.
        return nome=="Mensagem" || Regex.IsMatch(nome,
            @"^(?:Digite uma mensagem|Type a message)(?:$|[\s:])",RegexOptions.IgnoreCase);
    }
    static bool Compositor(AutomationElement campo, AutomationElement doc) {
        if (campo.Current.ControlType != ControlType.Edit || campo.Current.IsPassword || !Visivel(campo)) return false;
        if (!RotuloCompositor(campo.Current.Name)) return false;
        object p;
        if (campo.TryGetCurrentPattern(ValuePattern.Pattern,out p) && ((ValuePattern)p).Current.IsReadOnly)
            return false;
        for (var e=campo; e!=null; e=walker.GetParent(e)) if (Automation.Compare(e,doc)) return true;
        return false;
    }
    static AutomationElement CompositorFocado(AutomationElement doc) {
        // Chrome pode dar foco a um filho do contenteditable, em vez do Edit.
        var campo=AutomationElement.FocusedElement;
        for (int i=0;campo!=null && i<12;i++,campo=walker.GetParent(campo)) {
            Prazo();
            if (Automation.Compare(campo,doc)) break;
            if (Compositor(campo,doc)) return campo;
        }
        return null;
    }
    static void FormatoClipboard(uint formato, byte[] bytes) {
        IntPtr memoria = GlobalAlloc(2,(UIntPtr)bytes.Length);
        if (memoria == IntPtr.Zero) throw new InvalidOperationException();
        IntPtr destino = GlobalLock(memoria);
        if (destino == IntPtr.Zero) { GlobalFree(memoria); throw new InvalidOperationException(); }
        Marshal.Copy(bytes,0,destino,bytes.Length); GlobalUnlock(memoria);
        if (SetClipboardData(formato,memoria) == IntPtr.Zero) {
            GlobalFree(memoria); throw new InvalidOperationException();
        }
    }
    static string Colar(Aba aba, string texto) {
        if (texto.Length == 0 || texto.Length > 30000) return "falha";
        // Não ativa janela/conversa: o operador precisa focalizar o campo durante a contagem.
        Guarda(aba);
        var campo = CompositorFocado(Documento(aba));
        if (campo==null) return "campo_nao_identificado";
        string anterior;
        try { anterior=Conteudo(campo,30001); }
        catch { return "campo_nao_legivel"; }
        if (anterior.Length>=30001 || anterior.Trim(' ','\t','\r','\n','\u200b','\ufeff').Length != 0)
            return "campo_ocupado";
        foreach (int tecla in new [] {16,17,18,91,92})
            if ((GetAsyncKeyState(tecla)&0x8000)!=0) return "tecla_pressionada";
        uint sequencia = 0;
        bool tentativa=false;
        if (clipboardOwner == null) {
            clipboardOwner = new System.Windows.Forms.NativeWindow();
            clipboardOwner.CreateHandle(new System.Windows.Forms.CreateParams());
        }
        try {
            if (!OpenClipboard(clipboardOwner.Handle)) return "clipboard_indisponivel";
            try {
                EmptyClipboard();
                FormatoClipboard(RegisterClipboardFormat("CanIncludeInClipboardHistory"),new byte[4]);
                FormatoClipboard(RegisterClipboardFormat("CanUploadToCloudClipboard"),new byte[4]);
                FormatoClipboard(13,Encoding.Unicode.GetBytes(texto+"\0"));
                sequencia = GetClipboardSequenceNumber();
            } finally { CloseClipboard(); }
            Guarda(aba);
            var focado=CompositorFocado(Documento(aba));
            if (focado==null || !Automation.Compare(campo,focado)) return "foco";
            var inputs = new INPUT[4];
            for (int i=0;i<4;i++) inputs[i].type=1;
            inputs[0].data.key.vk=17; inputs[1].data.key.vk=86;
            inputs[2].data.key.vk=86; inputs[2].data.key.flags=2;
            inputs[3].data.key.vk=17; inputs[3].data.key.flags=2;
            tentativa=true;
            if (SendInput(4,inputs,Marshal.SizeOf(typeof(INPUT))) != 4) return "incerto";
            // O WhatsApp processa a colagem de forma assíncrona. Mantém o clipboard
            // até a confirmação ou o prazo, sem reenviar Ctrl+V nem pressionar Enter.
            long ate=Math.Min(limite,Agora()+3000);
            while (Agora()<ate) {
                Thread.Sleep(100);
                Guarda(aba);
                focado=CompositorFocado(Documento(aba));
                if (focado==null || !Automation.Compare(campo,focado)) return "incerto";
                if (Normalizar(Conteudo(campo,texto.Length+100))==Normalizar(texto)) return "ok";
            }
            return "incerto";
        } catch (Exception) {
            // Após Ctrl+V não oferecer repetição como se nada tivesse acontecido.
            return tentativa ? "incerto" : "falha_pre_colagem";
        } finally {
            // Não apaga uma cópia que o operador tenha feito depois da nossa.
            if (sequencia != 0 && GetClipboardSequenceNumber() == sequencia && OpenClipboard(clipboardOwner.Handle)) {
                try { EmptyClipboard(); } finally { CloseClipboard(); }
            }
        }
    }
    static string Normalizar(string texto) {
        // UIA do Chrome omite parágrafos vazios. Confere linhas de texto e links;
        // a formatação visual permanece para a conferência do operador.
        return Regex.Replace(texto.Replace("\r\n","\n").Replace("\r","\n").Replace('\u00a0',' '),@"\n+","\n").Trim();
    }
    // Diagnóstico local: só tipos/padrões e prefixos fixos de rótulos, nunca valores
    // ou nomes de contatos. Não ativa abas, não acessa clipboard e não escreve na página.
    public static object DiagnosticarCampoWhatsApp() {
        limite=Agora()+12000;
        var aba=Unica(Abas(),"whatsapp","");
        if (!Selecionada(aba.tab)) return Resposta("whatsapp_em_outra_aba");
        Endereco(aba);
        var doc=Documento(aba);
        var lista=new List<object>();
        var elementos=doc.FindAll(TreeScope.Descendants,
            new PropertyCondition(AutomationElement.IsKeyboardFocusableProperty,true));
        foreach (AutomationElement e in elementos) {
            Prazo(); if (!Visivel(e)) continue;
            string nome=e.Current.Name.Trim();
            string rotulo=null;
            foreach (string prefixo in new [] {"Digite uma mensagem","Type a message","Mensagem","Message"})
                if (nome.StartsWith(prefixo,StringComparison.OrdinalIgnoreCase)) {rotulo=prefixo;break;}
            if (rotulo==null) continue;
            object p;
            bool value=e.TryGetCurrentPattern(ValuePattern.Pattern,out p);
            bool leitura=value && ((ValuePattern)p).Current.IsReadOnly;
            bool text=e.TryGetCurrentPattern(TextPattern.Pattern,out p);
            lista.Add(new Dictionary<string,object> {
                {"rotulo",rotulo},{"sufixo",nome.Length>rotulo.Length},
                {"tipo",e.Current.ControlType.ProgrammaticName},
                {"valuePattern",value},{"somenteLeitura",leitura},{"textPattern",text},
                {"focado",e.Current.HasKeyboardFocus}
            });
        }
        return lista;
    }
    public static object Executar(string acao, string referencia, string valor, long fim) {
        limite = Math.Min(fim,Agora()+12000);
        if (consultaAtual!=null && consultaAtual.validade<Agora()) consultaAtual=null;
        if (detalheAtual!=null && (detalheAtual.validade<Agora() ||
            acao=="ativar" || acao=="consultar" || acao=="sair" || acao=="abrir")) detalheAtual=null;
        try {
            Prazo(); var abas = Abas();
            if (acao=="retornar_painel") return Resposta(RetornarPainel(abas));
            if (acao == "status") {
                var estados = new Dictionary<string,object>();
                foreach (string sistema in new [] {"siat","whatsapp"}) {
                    var itens = abas.FindAll(delegate(Aba a) {return a.sistema==sistema;});
                    string estado = itens.Count == 0 ? "ausente" : itens.Count > 1 ? "duplicada" : "localizada";
                    if (itens.Count == 1 && sistema == "siat" && Selecionada(itens[0].tab)
                        && !IsIconic((IntPtr)itens[0].janela.Current.NativeWindowHandle)) {
                        try { string tela = EstadoSiat(itens[0]); if (tela!="desconhecida") estado=tela; } catch { }
                    }
                    estados[sistema] = new Dictionary<string,object> {{"estado",estado},
                        {"referencia",itens.Count==1 ? itens[0].referencia : ""}};
                }
                return estados;
            }
            var aba = Unica(abas,acao=="colar" ? "whatsapp" : "siat",referencia);
            if (acao == "ativar") { Ativar(aba); return Resposta("ok"); }
            if (acao == "estado") return Resposta(Selecionada(aba.tab) ? EstadoSiat(aba) : "desconhecida");
            if (acao == "colar") return Resposta(Colar(aba,valor));
            if (referenciaAtual != aba.referencia || janelaAtual != (IntPtr)aba.janela.Current.NativeWindowHandle)
                return Resposta("falha");
            Guarda(aba);
            if (EstadoSiat(aba) == "login") return Resposta("login");
            if (acao == "abrir") return Resposta(Abrir(aba));
            if (acao == "preparar_consulta") return Resposta(PrepararConsulta(aba));
            if (acao == "consultar") return Resposta(Consultar(aba,valor));
            if (acao == "detalhes") return Resposta(AbrirDetalhes(aba,valor));
            if (acao == "retencao") return LerRetencao(aba,valor);
            if (acao == "sair") return Resposta(Sair(aba));
            return Resposta("falha");
        } catch (TimeoutException) { return Resposta("demora"); }
        catch (InvalidOperationException erro) { return Erro(erro,erro.Message=="foco" ? "foco" : "falha"); }
        catch (Exception erro) { return Erro(erro,acao=="colar" ? "incerto" : "falha"); }
    }
}
