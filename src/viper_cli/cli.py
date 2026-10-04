"""O comando viper: instalar, ver, documentar, atualizar e remover a biblioteca.

viper -h imprime e sai, como git -h e dnf -h; viper sozinho, num terminal, abre o menu.
"""
import os
import sys
from pathlib import Path

from viper_cli import REPOSITORIO, __version__
from viper_cli import alvo
from viper_cli import atualizar
from viper_cli import docs

# ── cor, só quando faz sentido ─────────────────────────────────────────────

_COR = {"azul": "38;2;74;163;239", "amarelo": "38;2;240;180;60", "laranja": "38;2;240;138;60",
        "cinza": "38;2;125;133;146", "verde": "38;2;110;200;140", "negrito": "1"}


def _tem_cor():
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def c(texto, *cores):
    if not _tem_cor() or not cores:
        return str(texto)
    return "".join(f"\x1b[{_COR[k]}m" for k in cores) + str(texto) + "\x1b[0m"


def _casa(caminho):
    s = str(caminho)
    casa = os.path.expanduser("~")
    return "~" + s[len(casa):] if s.startswith(casa) else s


# ── a ajuda ────────────────────────────────────────────────────────────────

COMANDOS = [
    ("install", "instala a viper no ambiente virtual desta pasta"),
    ("install --global", "instala para o seu usuário: aquele Python, em qualquer pasta (fora de ambiente virtual)"),
    ("uninstall", "remove daqui   (--global: do usuário · --all: de todo lugar)"),
    ("status", "onde está instalada, em que versão, e se esta pasta tem"),
    ("docs [função]", "as funções do arsenal; com um nome, a documentação dela"),
    ("check-update", "procura uma versão nova e mostra o que mudou, sem instalar"),
    ("upgrade", "procura, mostra o que mudou e pergunta antes de instalar"),
    ("sync", "reescreve a viper em todo lugar registrado, com a versão deste comando"),
]


def ajuda():
    w = max(len(n) for n, _ in COMANDOS) + 4
    linhas = [
        f"{c('viper', 'verde', 'negrito')} {__version__} — o arsenal: funções suas, importáveis como as nativas",
        "",
        f"{c('uso:', 'negrito')} viper <comando> [opções]",
        f"     viper             {c('sem nada, num terminal, abre o menu', 'cinza')}",
        "",
        c("comandos:", "negrito"),
    ]
    linhas += [f"  {n:<{w}}{c(d, 'cinza')}" for n, d in COMANDOS]
    linhas += [
        "",
        c("opções:", "negrito"),
        f"  {'--python CAMINHO':<{w}}{c('usa este Python em vez de descobrir sozinho', 'cinza')}",
        f"  {'-y, --yes':<{w}}{c('não pergunta (upgrade, uninstall --all)', 'cinza')}",
        f"  {'-h, --help':<{w}}{c('esta ajuda   ·   viper <comando> -h: a ajuda de um comando', 'cinza')}",
        f"  {'-V, --version':<{w}}{c('a versão', 'cinza')}",
        "",
        c("variáveis:", "negrito"),
        f"  {'VIPER_REPO=dono/repo':<{w}}{c(f'de onde o upgrade busca (padrão: {REPOSITORIO})', 'cinza')}",
        f"  {'NO_COLOR':<{w}}{c('sem cor na saída', 'cinza')}",
        "",
        c("no seu código:", "negrito"),
        "  from viper import replacement",
        "",
        c("exemplos:", "negrito"),
        "  cd meu-projeto && python -m venv .venv && viper install",
        "  viper install --global",
        "  viper docs",
        "  viper upgrade",
    ]
    return "\n".join(linhas)


AJUDA_COMANDO = {
    "install": """viper install [--global] [--python CAMINHO]

  sem --global   instala no ambiente virtual desta pasta: .venv/, venv/ ou env/; se não houver,
                 no ambiente ativo ($VIRTUAL_ENV). Só aquele projeto enxerga a viper.
  --global       instala na pasta de pacotes do seu usuário de um Python (o python3 do PATH).
                 Vale para aquele Python em qualquer pasta, mas não entra em ambiente virtual:
                 o venv isola justamente isso. Num projeto com .venv, use o install local.
  --python P     escolhe o Python à mão.

  O Python em que o próprio comando foi instalado (pip install --user) já enxerga a viper:
  ali o install não tem o que fazer, e diz isso.""",
    "uninstall": """viper uninstall [--global] [--all] [--python CAMINHO] [-y]

  sem opção      remove do ambiente virtual desta pasta
  --global       remove do seu usuário (o python3 do PATH, ou --python)
  --all          remove de todo lugar que o comando lembra (pergunta antes, a menos que -y)

  Só apaga uma pasta viper/ que o próprio comando pôs lá. A que veio do pip fica.""",
    "status": """viper status

  Lista todo lugar onde a viper foi instalada, a versão de cada um, e diz se esta pasta
  enxerga a viper.""",
    "docs": """viper docs [função]

  sem nome       lista as funções do arsenal: a assinatura e a primeira linha da docstring
  com um nome    a docstring inteira daquela função, com os exemplos (>>>) e o resultado de
                 cada um destacados

  A documentação é a docstring que você escreveu: o comando só lê e formata.""",
    "check-update": """viper check-update

  Procura a versão no repositório e mostra o que mudou desde a sua. Não instala nada.""",
    "upgrade": """viper upgrade [-y]

  Procura a versão nova, mostra o que mudou e pergunta [s/N]. Se sim, atualiza o comando
  (pelo pipx ou pelo pip, do jeito que ele foi instalado) e reescreve a viper em todo lugar
  registrado.""",
    "sync": """viper sync

  Reescreve a viper em todo lugar registrado com a versão deste comando. O upgrade chama
  sozinho; à mão, serve depois de editar o arsenal na sua cópia de desenvolvimento.""",
}


# ── os comandos ─────────────────────────────────────────────────────────────

def _perguntar_sim(pergunta, sim_sempre=False):
    if sim_sempre:
        return True
    if not sys.stdin.isatty():
        print(c("sem terminal para perguntar: use -y para confirmar", "laranja"))
        return False
    try:
        return input(f"{pergunta} [s/N] ").strip().lower() in ("s", "sim", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def cmd_install(op):
    if op["global"]:
        python, como = alvo.achar_global(op["python"])
    else:
        python, como = alvo.achar_local(Path.cwd(), op["python"])
    escopo = "global" if op["global"] else "local"
    print(f"{c('viper install', 'verde', 'negrito')} · {escopo} · {como}")
    r = alvo.instalar(escopo, python, como)
    info = r["info"]
    print(f"  {c('✓', 'verde')} instalada em {_casa(r['destino'] / alvo.PACOTE)}")
    print(f"    Python {info['versao']} · {_casa(info['executavel'])}")
    if r["importa"]:
        print(c(f"  · conferido: import viper responde a versão {r['importa']}", "cinza"))
    else:
        print(c("  ⚠ os arquivos estão lá, mas  import viper  falhou neste Python:", "laranja"))
        for linha in r["erro"].splitlines()[-4:]:
            print(c("    " + linha, "laranja"))
    if escopo == "global":
        print(c("  · vale para este Python em qualquer pasta, menos dentro de ambiente virtual (lá, viper install)",
                "cinza"))
    return 0


def cmd_uninstall(op):
    if op["all"]:
        itens = alvo.ler_registro()
        if not itens:
            print("o comando não lembra de nenhuma instalação")
            return 0
        for i in itens:
            print(f"  {i['escopo']:<7} {_casa(i['pasta_pacotes'])}")
        if not _perguntar_sim(f"remover dos {len(itens)} lugares?", op["yes"]):
            return 1
        for i in itens:
            alvo.remover(i["pasta_pacotes"])
        print(c(f"✓ removida de {len(itens)} lugares", "verde"))
        return 0
    if op["global"]:
        python, _ = alvo.achar_global(op["python"])
        pasta = alvo.perguntar(python)["usuario"]
    else:
        python, _ = alvo.achar_local(Path.cwd(), op["python"])
        pasta = alvo.perguntar(python)["pacotes"]
    if alvo.remover(pasta):
        print(c("✓ removida", "verde") + f" de {_casa(pasta)}")
    elif (Path(pasta) / alvo.PACOTE).exists():
        print(f"a viper em {_casa(pasta)} não foi posta pelo comando (veio do pip?): ficou onde estava")
    else:
        print(f"não estava instalada em {_casa(pasta)}")
    return 0


def cmd_status(op):
    itens = alvo.ler_registro()
    print(f"{c('viper', 'verde', 'negrito')} {__version__} · "
          f"{len(itens)} instalaç{'ão' if len(itens) == 1 else 'ões'}")
    if itens:
        print()
        for i in itens:
            existe = alvo._e_do_comando(i["pasta_pacotes"])
            v = alvo.versao_instalada(i["pasta_pacotes"]) if existe else None
            if not existe:
                estado = c("sumiu (ambiente apagado?)", "laranja")
            elif v != __version__:
                estado = c(f"{v} → rode viper sync", "amarelo")
            else:
                estado = c(v, "verde")
            print(f"  {i['escopo']:<7} Python {i['versao_python']:<8} {_casa(i['pasta_pacotes'])}  {estado}")
    print()
    try:
        python, como = alvo.achar_local(Path.cwd())
        em = alvo.perguntar(python)["viper_em"]
        if em:
            print(f"nesta pasta: {c('instalada', 'verde')} — {como}")
        else:
            print(f"nesta pasta: {c('não instalada', 'amarelo')} — {como}; para instalar:  viper install")
    except alvo.Recusa:
        print(f"nesta pasta: {c('sem ambiente virtual', 'cinza')} — vale o global, se houver")
    return 0


def cmd_docs(op):
    funcoes, erro = docs.carregar()
    if erro:
        print(c("o arsenal não importou — o erro, como o Python escreveu:", "laranja", "negrito"))
        print()
        print(erro.rstrip())
        return 1
    if not funcoes:
        print(f"{c('viper', 'verde', 'negrito')} {__version__} · o arsenal ainda está vazio")
        print(c("  a primeira função nasce à mão, em viper/arsenal.py", "cinza"))
        return 0
    if op["nome"] is None:
        print(f"{c('viper', 'verde', 'negrito')} {__version__} · {len(funcoes)} "
              f"funç{'ão' if len(funcoes) == 1 else 'ões'} no arsenal")
        print()
        for f in funcoes:
            resumo = docs.primeira_linha(f)
            print(f"  {c(docs.assinatura(f), 'azul', 'negrito')}")
            print(f"      {c(resumo, 'cinza') if resumo else c('(sem docstring)', 'laranja')}")
        print()
        print(c("  viper docs <função>: a documentação inteira de uma delas", "cinza"))
        return 0
    f, parecidas = docs.procurar(funcoes, op["nome"])
    if f is None:
        print(f"não há {c(op['nome'], 'laranja')} no arsenal" +
              (f" — você quis dizer {', '.join(c(p, 'azul') for p in parecidas)}?" if parecidas else ""))
        return 1
    print(c(docs.assinatura(f), "azul", "negrito"))
    print()
    pedacos = docs.blocos(f)
    if not pedacos:
        print(c("  (sem docstring: a documentação desta função é a docstring que ela ainda não tem)", "laranja"))
    cor = {"texto": (), "exemplo": ("azul",), "resultado": ("verde",)}
    for papel, linha in pedacos:
        print("  " + c(linha, *cor[papel]))
    arquivo, linha = docs.onde(f)
    if arquivo:
        print()
        print(c(f"  {_casa(arquivo)}, linha {linha}", "cinza"))
    return 0


def cmd_check_update(op):
    print(f"{c('viper check-update', 'verde', 'negrito')} · {atualizar._repositorio()}")
    try:
        remota = atualizar.versao_remota()
    except Exception as e:
        print(c(f"  não consegui consultar o repositório: {e}", "laranja"))
        return 1
    if atualizar._tupla(remota) <= atualizar._tupla(__version__):
        print(f"  {c('✓', 'verde')} você está na versão mais nova ({__version__})")
        return 0
    print(f"  versão nova: {c(__version__, 'cinza')} → {c(remota, 'verde', 'negrito')}")
    for versao, texto in atualizar.novidades(__version__):
        print()
        print(c(f"  {versao}", "amarelo", "negrito"))
        for linha in texto.splitlines():
            print("    " + linha)
    return 100      # como o dnf check-update: 100 = há atualização


def cmd_upgrade(op):
    codigo = cmd_check_update(op)
    if codigo != 100:
        return codigo
    forma = atualizar.como_foi_instalado()
    cmd = atualizar.comando_de_atualizacao(forma)
    print()
    if cmd is None:
        print(c("  este comando é uma cópia de desenvolvimento: atualize com  git pull  na pasta dele e depois  "
                "viper sync", "amarelo"))
        return 1
    print(c(f"  vai rodar: {' '.join(cmd)}", "cinza"))
    if not _perguntar_sim("  atualizar?", op["yes"]):
        return 1
    import subprocess
    if subprocess.run(cmd).returncode != 0:
        print(c("  a atualização falhou — nada foi trocado nas instalações", "laranja"))
        return 1
    return atualizar.reaplicar_com_a_versao_nova()


def cmd_sync(op):
    feitos, sumidos = alvo.reaplicar()
    for i in feitos:
        print(f"  {c('✓', 'verde')} {i['escopo']:<7} {_casa(i['pasta_pacotes'])}  → {__version__}")
    for i in sumidos:
        print(f"  {c('·', 'cinza')} {i['escopo']:<7} {_casa(i['pasta_pacotes'])}  {c('sumiu: saiu do registro', 'cinza')}")
    if not feitos and not sumidos:
        print("o comando não lembra de nenhuma instalação")
    return 0


EXECUTA = {"install": cmd_install, "uninstall": cmd_uninstall, "status": cmd_status, "docs": cmd_docs,
           "check-update": cmd_check_update, "upgrade": cmd_upgrade, "sync": cmd_sync}


# ── o menu ──────────────────────────────────────────────────────────────────

def menu():
    opcoes = [
        ("status", "onde está instalada", "status", {}),
        ("instalar nesta pasta", "install", "install", {}),
        ("instalar no usuário (global)", "install --global", "install", {"global": True}),
        ("documentação do arsenal", "docs", "docs", {}),
        ("procurar atualização", "check-update", "check-update", {}),
        ("atualizar", "upgrade", "upgrade", {}),
        ("remover desta pasta", "uninstall", "uninstall", {}),
    ]
    while True:
        print()
        print(f"{c('viper', 'verde', 'negrito')} {__version__} {c('— o arsenal', 'cinza')}")
        print()
        for n, (nome, cmd, _, _) in enumerate(opcoes, 1):
            print(f"  {c(n, 'amarelo', 'negrito')}  {nome:<30}{c('viper ' + cmd, 'cinza')}")
        print(f"  {c(0, 'amarelo', 'negrito')}  sair")
        try:
            escolha = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if escolha in ("0", "q", "sair", ""):
            return 0
        if not escolha.isdigit() or not 1 <= int(escolha) <= len(opcoes):
            print(c("escolha um número da lista", "laranja"))
            continue
        _, _, comando, extra = opcoes[int(escolha) - 1]
        op = dict(_OPCOES_PADRAO, **extra)
        print()
        _rodar(comando, op)


# ── a entrada ───────────────────────────────────────────────────────────────

_OPCOES_PADRAO = {"global": False, "all": False, "yes": False, "python": None, "help": False, "nome": None}


def _erro_de_uso(msg):
    """Como as ferramentas do Linux: erro de uso vai para o stderr e sai com 2."""
    print(f"viper: {msg} (veja viper -h)", file=sys.stderr)
    raise SystemExit(2)


def _ler_argumentos(args):
    comando, op = None, dict(_OPCOES_PADRAO)
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-h", "--help"):
            op["help"] = True
        elif a in ("-V", "--version"):
            return "versao", op
        elif a == "--global":
            op["global"] = True
        elif a == "--all":
            op["all"] = True
        elif a in ("-y", "--yes"):
            op["yes"] = True
        elif a == "--python" or a.startswith("--python="):
            if "=" in a:
                op["python"] = a.split("=", 1)[1]
            else:
                i += 1
                if i >= len(args):
                    _erro_de_uso("--python precisa de um caminho")
                op["python"] = args[i]
        elif a.startswith("-"):
            _erro_de_uso(f"opção desconhecida: {a}")
        elif comando is None:
            comando = a
        elif comando == "docs" and op["nome"] is None:
            op["nome"] = a
        else:
            _erro_de_uso(f"argumento a mais: {a}")
        i += 1
    return comando, op


def _rodar(comando, op):
    try:
        return EXECUTA[comando](op)
    except alvo.Recusa as e:
        print(c("viper: ", "laranja", "negrito") + str(e))
        return 1


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    comando, op = _ler_argumentos(args)
    if comando == "versao":
        print(f"viper {__version__}")
        return 0
    if comando is None:
        if op["help"] or not (sys.stdin.isatty() and sys.stdout.isatty()):
            print(ajuda())
            return 0
        return menu()
    if comando not in EXECUTA:
        _erro_de_uso(f"comando desconhecido: {comando}")
    if op["help"]:
        print(AJUDA_COMANDO.get(comando, ajuda()))
        return 0
    return _rodar(comando, op)
