"""Onde a viper mora: descobrir o Python certo, instalar, remover e lembrar.

Dois escopos, como no ratt, e eles não se misturam:

  local   o ambiente virtual da pasta (.venv, venv, env) ou o que está ativo ($VIRTUAL_ENV).
          Só aquele projeto enxerga a viper.
  global  a pasta de pacotes do USUÁRIO de um Python (site.getusersitepackages()).
          Vale para aquele Python em qualquer pasta, menos dentro de um ambiente virtual,
          que existe justamente para isolar isso.

Em cada lugar a viper vira uma pasta  viper/  com um arquivo  INSTALADO_PELO_COMANDO  dentro.
É ele que diz que a pasta é do comando, e não de um  pip install : uma pasta sem ele nunca é
apagada nem reescrita.
"""
import datetime
import json
import os
import shutil
import subprocess
from pathlib import Path

from viper_cli import __version__, pasta_da_biblioteca

PACOTE = "viper"
MARCA = "INSTALADO_PELO_COMANDO"

# o que o Python-alvo responde sobre si mesmo: roda DENTRO dele
_PERGUNTA = r"""
import json, site, sys, sysconfig, importlib.util
try:
    achado = importlib.util.find_spec("viper")
    origem = achado.origin if achado else None
except Exception:
    origem = None
print(json.dumps({
    "executavel": sys.executable,
    "versao": "%d.%d.%d" % sys.version_info[:3],
    "maior_menor": [sys.version_info[0], sys.version_info[1]],
    "pacotes": sysconfig.get_paths()["purelib"],
    "usuario": site.getusersitepackages(),
    "usuario_ligado": bool(site.ENABLE_USER_SITE),
    "em_venv": sys.prefix != sys.base_prefix,
    "prefixo": sys.prefix,
    "viper_em": origem,
}))
"""


def _ambiente_limpo():
    """Pergunta-se ao Python o que está INSTALADO nele: um PYTHONPATH do shell não conta."""
    return {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}


class Recusa(Exception):
    """A viper não instala ali, e a mensagem diz por quê e o que fazer."""


# ── o registro: onde a viper foi instalada ─────────────────────────────────

def _pasta_dados():
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return Path(base) / "viper"


def _arquivo_registro():
    return _pasta_dados() / "instalacoes.json"


def ler_registro():
    try:
        return json.loads(_arquivo_registro().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def _gravar_registro(itens):
    arq = _arquivo_registro()
    arq.parent.mkdir(parents=True, exist_ok=True)
    tmp = arq.with_suffix(".tmp")
    tmp.write_text(json.dumps(itens, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, arq)


# ── perguntar a um Python quem ele é ───────────────────────────────────────

def perguntar(python):
    try:
        r = subprocess.run([str(python), "-c", _PERGUNTA], capture_output=True, text=True, timeout=60,
                           env=_ambiente_limpo())
    except (OSError, subprocess.TimeoutExpired) as e:
        raise Recusa(f"não consegui rodar {python}: {e}") from e
    if r.returncode != 0:
        raise Recusa(f"{python} não respondeu:\n{r.stderr.strip()}")
    info = json.loads(r.stdout.strip().splitlines()[-1])
    if tuple(info["maior_menor"]) < (3, 9):
        raise Recusa(f"{python} é o Python {info['versao']}; a viper precisa do 3.9 ou mais novo")
    return info


def _venv_da_pasta(pasta):
    for nome in (".venv", "venv", "env", ".env"):
        if (pasta / nome / "pyvenv.cfg").is_file():
            py = pasta / nome / "bin" / "python"
            if py.exists():
                return py
    return None


def achar_local(pasta, python=None):
    """O Python do escopo local, e uma frase que diz como ele foi escolhido."""
    pasta = Path(pasta).resolve()
    if python:
        return Path(python), f"o Python que você indicou ({python})"
    py = _venv_da_pasta(pasta)
    if py:
        return py, f"o ambiente virtual da pasta ({py.parent.parent.name}/)"
    ativo = os.environ.get("VIRTUAL_ENV")
    if ativo and (Path(ativo) / "bin" / "python").exists():
        return Path(ativo) / "bin" / "python", f"o ambiente virtual ativo ({ativo})"
    if (pasta / ".python-version").is_file():
        versao = (pasta / ".python-version").read_text().strip()
        raise Recusa(
            f"esta pasta só tem um .python-version ({versao}), sem ambiente virtual.\n"
            f"  O pyenv escolhe o INTERPRETADOR da pasta, mas os pacotes dele são compartilhados por\n"
            f"  todo projeto que usa o {versao}. Instalar aqui poria a viper em todos eles.\n\n"
            f"  Para ficar só nesta pasta:   python -m venv .venv   e depois   viper install\n"
            f"  Para o {versao} inteiro:      viper install --global\n"
            f"  Se é isso mesmo que você quer:   viper install --python \"$(pyenv which python)\"")
    raise Recusa(
        "não achei um ambiente virtual nesta pasta (.venv, venv, env) nem um ativo.\n\n"
        "  Para criar um aqui:          python -m venv .venv   e depois   viper install\n"
        "  Para o seu usuário:          viper install --global")


def achar_global(python=None):
    if python:
        return Path(python), f"o Python que você indicou ({python})"
    if os.environ.get("VIRTUAL_ENV"):
        raise Recusa(
            "há um ambiente virtual ativo, e o global não mora dentro de ambiente virtual.\n\n"
            "  Saia dele primeiro:          deactivate   e depois   viper install --global\n"
            "  Ou diga qual Python:         viper install --global --python /caminho/do/python")
    for nome in ("python3", "python"):
        achado = shutil.which(nome)
        if achado:
            return Path(achado), f"o {nome} do seu PATH"
    raise Recusa("não achei python3 nem python no PATH")


# ── instalar, remover, reaplicar ───────────────────────────────────────────

def versao_instalada(pasta_pacotes):
    import re
    try:
        texto = (Path(pasta_pacotes) / PACOTE / "__init__.py").read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', texto, re.M)
    return m.group(1) if m else None


def _e_do_comando(pasta_pacotes):
    return (Path(pasta_pacotes) / PACOTE / MARCA).is_file()


def _copiar(destino):
    """Escreve a pasta viper/ deste comando em destino/viper/, trocando a anterior inteira."""
    alvo = Path(destino) / PACOTE
    tmp = Path(destino) / f".{PACOTE}.novo"
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(pasta_da_biblioteca(), tmp, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", MARCA))
    (tmp / MARCA).write_text(
        f"instalado pelo comando viper {__version__}: não edite esta pasta.\n"
        f"O  viper upgrade  e o  viper sync  reescrevem tudo aqui. O original mora no repositório.\n",
        encoding="utf-8")
    if alvo.exists():
        shutil.rmtree(alvo)
    os.replace(tmp, alvo)


def _confirmar(python):
    r = subprocess.run([str(python), "-c", "import viper; print(viper.__version__)"],
                       capture_output=True, text=True, timeout=60, env=_ambiente_limpo())
    return r.stdout.strip() if r.returncode == 0 else None, r.stderr.strip()


def instalar(escopo, python, como):
    info = perguntar(python)
    if escopo == "global":
        if info["em_venv"]:
            raise Recusa(f"{python} é de um ambiente virtual ({info['prefixo']}); o global é para um Python "
                         f"fora de ambiente. Use  viper install  (local) ali dentro.")
        if not info["usuario_ligado"]:
            raise Recusa(f"o Python {info['versao']} está com a pasta de pacotes do usuário desligada "
                         f"(site.ENABLE_USER_SITE = False); o global não teria efeito")
        destino = Path(info["usuario"])
    else:
        destino = Path(info["pacotes"])

    # este Python já enxerga uma viper que não é do comando (pip, ou a cópia de desenvolvimento):
    # não é erro — ela já está ali; só não é o comando que cuida dela
    if info["viper_em"] and not _e_do_comando(Path(info["viper_em"]).parent.parent):
        return {"destino": Path(info["viper_em"]).parent, "info": info, "ja_estava": True,
                "importa": None, "erro": ""}

    destino.mkdir(parents=True, exist_ok=True)
    _copiar(destino)
    itens = [i for i in ler_registro() if i.get("pasta_pacotes") != str(destino)]
    itens.append({"escopo": escopo, "python": info["executavel"], "versao_python": info["versao"],
                  "pasta_pacotes": str(destino), "como": como, "versao_viper": __version__,
                  "quando": datetime.datetime.now().isoformat(timespec="seconds")})
    _gravar_registro(itens)
    versao, erro = _confirmar(info["executavel"])
    return {"destino": destino, "info": info, "importa": versao, "erro": erro, "ja_estava": False}


def ambiente_da_pasta(pasta):
    """O ambiente virtual que roda nesta pasta (o da pasta ou o ativo), se houver."""
    py = _venv_da_pasta(Path(pasta).resolve())
    if py:
        return py
    ativo = os.environ.get("VIRTUAL_ENV")
    if ativo and (Path(ativo) / "bin" / "python").exists():
        return Path(ativo) / "bin" / "python"
    return None


def remover(pasta_pacotes):
    pasta = Path(pasta_pacotes)
    apagado = None
    if _e_do_comando(pasta):
        shutil.rmtree(pasta / PACOTE)
        apagado = pasta / PACOTE
    _gravar_registro([i for i in ler_registro() if i.get("pasta_pacotes") != str(pasta)])
    return apagado


def reaplicar():
    """Reescreve a viper em todo lugar registrado, com a versão deste comando."""
    feitos, sumidos = [], []
    for item in ler_registro():
        pasta = Path(item["pasta_pacotes"])
        if not _e_do_comando(pasta):
            sumidos.append(item)
            continue
        _copiar(pasta)
        item["versao_viper"] = __version__
        feitos.append(item)
    _gravar_registro(feitos)
    return feitos, sumidos
