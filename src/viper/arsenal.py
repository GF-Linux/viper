"""O arsenal. Cada função aqui nasceu de um problema real do estudo, primeiro no papel.

A docstring de cada função é a documentação dela: é o que o  viper docs <nome>  mostra.
As linhas que começam com  >>>  são exemplos de uso, e a linha logo abaixo é o resultado
esperado. Elas valem também como teste:  python -m doctest -v arsenal.py
"""


def replacement(lista, palavra, condicao):
    """Troca por palavra cada item de lista em que a condição for verdadeira.

    Nasceu do FizzBuzz (LeetCode 412): "dada uma condição, o valor é trocado".
    Uma chamada, uma condição. Os itens em que a condição dá False ficam como estão.

    lista     qualquer coisa que se percorre: lista, range, tupla, coluna do pandas
    palavra   o que entra no lugar do item
    condicao  uma função que recebe o item e diz True ou False — guardada para
              depois com lambda; escrita crua (x % 3 == 0) o Python calcula na hora

    Devolve uma lista NOVA: a original não muda. Se a entrada for uma coluna do
    pandas, devolve uma coluna com o mesmo índice e o mesmo nome.

    >>> replacement([1, 2, 3, 4, 5], 'par', lambda x: x % 2 == 0)
    [1, 'par', 3, 'par', 5]

    >>> replacement(range(1, 7), 'divisível', lambda x: x % 3 == 0)
    [1, 2, 'divisível', 4, 5, 'divisível']

    As duas condições juntas vão na mesma chamada, com and:

    >>> replacement(range(1, 16), 'FizzBuzz', lambda x: x % 3 == 0 and x % 5 == 0)[-1]
    'FizzBuzz'

    A original não muda:

    >>> pesos = [31.0, 0.0, 33.0]
    >>> replacement(pesos, 'erro de pesagem', lambda x: x <= 0)
    [31.0, 'erro de pesagem', 33.0]
    >>> pesos
    [31.0, 0.0, 33.0]

    Cuidado ao encadear: a segunda chamada recebe os itens que a primeira já trocou.
    Se a condição dela não serve para o texto novo, dá erro — por isso a condição
    composta vem primeiro, ou as duas vão na mesma chamada.

    A condição crua, sem lambda, é recusada com o motivo:

    >>> replacement([1, 2, 3], 'x', True)
    Traceback (most recent call last):
        ...
    TypeError: condicao precisa ser uma função (ex.: lambda x: x % 2 == 0), e veio bool
    """
    if not callable(condicao):
        raise TypeError("condicao precisa ser uma função (ex.: lambda x: x % 2 == 0), "
                        f"e veio {type(condicao).__name__}")
    nova = [palavra if condicao(item) else item for item in lista]
    if hasattr(lista, "index") and hasattr(lista, "name") and hasattr(lista, "map"):
        return type(lista)(nova, index=lista.index, name=lista.name)    # coluna do pandas
    return nova


def compare(v1, v2):
    """Iguala o tamanho de duas versões, completando com zeros, para comparar por fora.

    Nasceu do Compare Version Numbers (LeetCode 165) e da frase sys.version_info >= (maior, menor):
    3.12 e 3.12.0.0.0 são a mesma versão, mas [3, 12] e [3, 12, 0, 0, 0] não são iguais
    para o Python. A função só iguala; quem compara é quem chama, com < == >=.

    v1, v2   texto ('3.12'), número (3.12), lista, tupla ou sys.version_info
             — de cada parte fica só o primeiro número ('v2' → 2, '0rc1' → 0);
             a parte sem número nenhum sai ('final', do sys.version_info)

    Devolve os dois lados, sempre como lista, com o mesmo tamanho.

    >>> compare('3.12', '3.12.0.0.0')
    ([3, 12, 0, 0, 0], [3, 12, 0, 0, 0])

    >>> a, b = compare('3.12', '3.12.0.1')
    >>> a, b
    ([3, 12, 0, 0], [3, 12, 0, 1])
    >>> a < b
    True

    Comparar como texto erra; como número de cada parte, não:

    >>> '1.2' < '1.10'
    False
    >>> a, b = compare('1.2', '1.10')
    >>> a < b
    True

    O sistema entra como está (aqui, a tupla que o sys.version_info do 3.12.14 é):

    >>> compare((3, 12, 14, 'final', 0), '3.12')
    ([3, 12, 14, 0], [3, 12, 0, 0])

    Versão como número perde o zero do fim antes de chegar aqui: 3.10 é 3.1.

    >>> compare(3.10, '3.1')
    ([3, 1], [3, 1])
    """
    a, b = _numeros_da_versao(v1), _numeros_da_versao(v2)
    tamanho = max(len(a), len(b))
    return a + [0] * (tamanho - len(a)), b + [0] * (tamanho - len(b))


def _numeros_da_versao(v):
    """O primeiro número de cada parte da versão; a parte sem número sai."""
    import re
    if isinstance(v, (list, tuple)):          # lista, tupla e sys.version_info
        partes = [str(p) for p in v]
    else:                                      # texto e número
        partes = str(v).split(".")
    numeros = []
    for parte in partes:
        achado = re.search(r"\d+", parte)
        if achado:
            numeros.append(int(achado.group()))
    return numeros
