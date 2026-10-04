"""Os testes do comando viper (não do arsenal: o arsenal se testa pelos exemplos das docstrings).

    python -m pytest tests          (ou)          python tests/test_viper.py

Cada teste cria ambientes virtuais de verdade numa pasta temporária, e o registro do comando
vai para uma pasta temporária também (XDG_DATA_HOME): nada toca as suas instalações.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"
sys.path.insert(0, str(SRC))


def _viper(args, cwd, dados, src=SRC):
    env = dict(os.environ, PYTHONPATH=str(src), XDG_DATA_HOME=str(dados), NO_COLOR="1")
    env.pop("VIRTUAL_ENV", None)
    r = subprocess.run([sys.executable, "-m", "viper_cli", *args], cwd=cwd, env=env,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def _venv(pasta):
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(pasta / ".venv")], check=True)
    py = pasta / ".venv" / "bin" / "python"
    pacotes = subprocess.run([str(py), "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
                             capture_output=True, text=True, check=True).stdout.strip()
    return py, Path(pacotes)


def test_install_local_importa_e_remove():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / "proj").mkdir()
        py, pacotes = _venv(t / "proj")
        codigo, saida = _viper(["install"], t / "proj", t / "dados")
        assert codigo == 0, saida
        assert "import viper responde a versão" in saida, saida
        assert (pacotes / "viper" / "INSTALADO_PELO_COMANDO").is_file()
        r = subprocess.run([str(py), "-c", "import viper; print(viper.__version__)"], capture_output=True, text=True)
        assert r.returncode == 0 and r.stdout.strip(), r.stderr

        codigo, saida = _viper(["status"], t / "proj", t / "dados")
        assert "1 instalação" in saida and "nesta pasta: instalada" in saida, saida

        codigo, saida = _viper(["sync"], t / "proj", t / "dados")
        assert codigo == 0 and "✓ local" in saida, saida

        codigo, saida = _viper(["uninstall"], t / "proj", t / "dados")
        assert codigo == 0 and "removida" in saida, saida
        assert not (pacotes / "viper").exists()


def test_recusa_pasta_so_com_pyenv():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / ".python-version").write_text("3.12.14\n")
        codigo, saida = _viper(["install"], t, t / "dados")
        assert codigo == 1 and ".python-version" in saida and "viper install --global" in saida, saida


def test_nao_escreve_por_cima_da_viper_do_pip():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / "proj").mkdir()
        py, pacotes = _venv(t / "proj")
        (pacotes / "viper").mkdir()                     # uma viper que não é do comando
        (pacotes / "viper" / "__init__.py").write_text("__version__ = '9.9.9'\n")
        codigo, saida = _viper(["install"], t / "proj", t / "dados")
        assert codigo == 1 and "não foi posta pelo comando" in saida, saida
        assert (pacotes / "viper" / "__init__.py").read_text() == "__version__ = '9.9.9'\n"
        codigo, saida = _viper(["uninstall"], t / "proj", t / "dados")
        assert (pacotes / "viper" / "__init__.py").exists(), saida


def test_arsenal_quebrado_nao_derruba_o_comando():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        shutil.copytree(SRC, t / "src", ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
        (t / "src" / "viper" / "arsenal.py").write_text("def quebrada(:\n    pass\n")
        codigo, saida = _viper(["-V"], t, t / "dados", src=t / "src")
        assert codigo == 0 and saida.startswith("viper "), saida
        codigo, saida = _viper(["docs"], t, t / "dados", src=t / "src")
        assert codigo == 1 and "o arsenal não importou" in saida and "SyntaxError" in saida, saida


def test_docs_le_a_docstring_e_separa_exemplo_de_resultado():
    from viper_cli import docs
    modulo = types.ModuleType("arsenal_de_teste")
    exec('''
def dobro(n):
    """Devolve o dobro de n.

    >>> dobro(2)
    4
    >>> dobro(
    ...     5)
    10

    Serve para qualquer número.
    """
    return n * 2

def _escondida():
    pass

def sem_doc(a, b=1):
    return a
''', modulo.__dict__)
    funcoes = docs.funcoes_de(modulo)
    assert [f.__name__ for f in funcoes] == ["dobro", "sem_doc"]
    assert docs.assinatura(funcoes[1]) == "sem_doc(a, b=1)"
    assert docs.primeira_linha(funcoes[0]) == "Devolve o dobro de n."
    assert docs.primeira_linha(funcoes[1]) is None
    papeis = [p for p, _ in docs.blocos(funcoes[0])]
    assert papeis == ["texto", "texto", "exemplo", "resultado", "exemplo", "exemplo", "resultado", "texto", "texto"]
    achada, parecidas = docs.procurar(funcoes, "dobra")
    assert achada is None and parecidas == ["dobro"]


def test_erros_de_uso_saem_com_2():
    with tempfile.TemporaryDirectory() as t:
        assert _viper(["foo"], t, Path(t) / "dados")[0] == 2
        assert _viper(["docs", "a", "b"], t, Path(t) / "dados")[0] == 2
        assert _viper(["--nada"], t, Path(t) / "dados")[0] == 2


if __name__ == "__main__":
    falhas = 0
    for nome, f in list(globals().items()):
        if nome.startswith("test_") and callable(f):
            try:
                f()
                print(f"ok     {nome}")
            except AssertionError as e:
                falhas += 1
                print(f"FALHOU {nome}\n{e}")
    raise SystemExit(1 if falhas else 0)
