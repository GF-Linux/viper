"""viper docs: a documentação do arsenal, tirada das docstrings que você escreveu.

Nada aqui é escrito pelo comando: ele só lê o arsenal.py, acha as funções e formata a
docstring de cada uma. Uma função sem docstring aparece assim mesmo, avisando que falta.
"""
import difflib
import importlib
import inspect
import traceback


def carregar():
    """(funções em ordem de escrita, erro). O erro é o texto do traceback se o arsenal não importou."""
    try:
        modulo = importlib.import_module("viper.arsenal")
    except Exception:
        return [], traceback.format_exc(limit=-1)
    return funcoes_de(modulo), None


def funcoes_de(modulo):
    achadas = [obj for nome, obj in vars(modulo).items()
               if inspect.isfunction(obj) and obj.__module__ == modulo.__name__ and not nome.startswith("_")]
    return sorted(achadas, key=lambda f: f.__code__.co_firstlineno)


def assinatura(f):
    try:
        return f"{f.__name__}{inspect.signature(f)}"
    except (TypeError, ValueError):
        return f"{f.__name__}(…)"


def primeira_linha(f):
    doc = inspect.getdoc(f)
    return doc.splitlines()[0] if doc else None


def procurar(funcoes, nome):
    por_nome = {f.__name__: f for f in funcoes}
    if nome in por_nome:
        return por_nome[nome], []
    return None, difflib.get_close_matches(nome, list(por_nome), n=3, cutoff=0.5)


def blocos(f):
    """A docstring em pedaços com papel: ('texto'|'exemplo'|'resultado', linha)."""
    doc = inspect.getdoc(f)
    if not doc:
        return []
    saida, em_exemplo = [], False
    for linha in doc.splitlines():        # a regra do doctest: o resultado vai até a linha em branco
        tirada = linha.lstrip()
        if tirada.startswith(">>>") or (em_exemplo and tirada.startswith("...")):
            saida.append(("exemplo", linha))
            em_exemplo = True
        elif em_exemplo and tirada:
            saida.append(("resultado", linha))
        else:
            saida.append(("texto", linha))
            em_exemplo = False
    return saida


def onde(f):
    try:
        return inspect.getsourcefile(f), f.__code__.co_firstlineno
    except TypeError:
        return None, None
