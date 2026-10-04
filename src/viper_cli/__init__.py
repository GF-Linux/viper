"""O comando viper: instala, atualiza e documenta a biblioteca viper.

Mora num pacote separado da biblioteca de propósito: um erro escrito no arsenal não pode
derrubar o comando que atualiza e mostra o erro. Por isso a versão é LIDA do arquivo da
biblioteca, sem importá-la.
"""
import importlib.util
import re
from pathlib import Path

# de onde o viper check-update e o viper upgrade buscam a versão nova
REPOSITORIO = "GF-Linux/viper"


def pasta_da_biblioteca():
    """A pasta viper/ que este comando instala. find_spec acha sem executar o arsenal."""
    achado = importlib.util.find_spec("viper")
    return Path(list(achado.submodule_search_locations)[0])


def _ler_versao():
    texto = (pasta_da_biblioteca() / "__init__.py").read_text(encoding="utf-8")
    m = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', texto, re.M)
    return m.group(1) if m else "?"


__version__ = _ler_versao()
