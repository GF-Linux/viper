# viper

**O arsenal.** Funções que nasceram de problemas do estudo, importáveis em qualquer projeto
como as nativas:

```python
from viper import replacement
```

**Mudanças Feitas 09/10/2026** 

## 0.2.0

- [replacement(lista, palavra, condicao)]: troca por 'palavra' cada item em que a condição for
  verdadeira. Nasceu do FizzBuzz. Devolve uma lista nova (uma coluna do pandas volta como coluna,
  com o mesmo índice); recusa a condição crua, sem 'lambda', dizendo o motivo.


## 0.1.0

- O comando 'viper': 'install' (local ou --global), 'uninstall', 'status', 'docs',
  'check-update', 'upgrade', 'sync' e o menu. O mesmo fluxo do ratt.
- 'viper docs' lê as docstrings do arsenal e destaca os exemplos e os resultados.
- O arsenal começa vazio.

## Por que o nome é víbora ?

Como um grande fã do Python, apesar do nome não ter nascido inicialmente pela cobra, a minha ideia
é criar uma lista de repositórios 'irmãs' que estejam relacionados e cada um remeta a uma cobra 
com motivos biologicos.
As irmãs são cobras com uma função cada: a [cascavel](https://github.com/GF-Linux/rattlesnake)
avisa, a [coral verdadeira](https://github.com/GF-Linux/truecoral) mostra o que é verdade. A
víbora é outra coisa: uma serpente, um indivíduo próprio. É a biblioteca autoral.

## A regra do arsenal

**Toda função aqui é escrita à mão, primeiro no papel.** Ela entra quando um problema real do
estudo pede por ela. O exercício continua sendo resolvido; o que ele ensina vira ferramenta por
cima dele.

O comando 'viper' é a parte que não é escrita à mão: ele só instala, atualiza e mostra a
documentação. Ele não escreve nenhuma função.

## Instalação

São dois passos, como no ratt: instalar o comando e pôr a biblioteca onde você quer.

**1. O comando `viper`**, uma vez por máquina:

'''bash
pipx install git+https://github.com/GF-Linux/viper.git
# sem pipx:
python3 -m pip install --user git+https://github.com/GF-Linux/viper.git
'''

Com o 'pip install --user', aquele Python já enxerga a viper em qualquer pasta.

**2. Num projeto**, que tem o próprio ambiente virtual e por isso não enxerga o seu usuário:

'''bash
cd meu-projeto
python -m venv .venv          # se o projeto ainda não tem ambiente virtual
viper install                 # só este projeto

viper install --global        # o python3 do seu usuário, em qualquer pasta
'''

| | onde instala | vale para |
|---|---|---|
| 'viper install' | o ambiente virtual da pasta (.venv/, venv/, env/) ou o ativo | só aquele projeto |
| viper install --global | a pasta de pacotes do usuário daquele Python | aquele Python em qualquer pasta, **menos dentro de um ambiente virtual** |

**pyenv:** uma pasta que só tem '.python-version' escolhe o *interpretador*, mas não isola
pacotes. Por isso o 'viper install' recusa e explica.

**distrobox / toolbox:** o container enxerga a mesma pasta pessoal, mas o Python de dentro é
outro. Instale o comando também lá dentro.

## Comandos

```
viper                     sem nada, num terminal, abre o menu
viper -h                  a ajuda (viper <comando> -h: a de um comando)
viper install [--global]  instala a biblioteca
viper uninstall           remove   (--global · --all)
viper status              onde está instalada, e em que versão
viper docs [função]       as funções do arsenal; com um nome, a documentação dela
viper check-update        procura versão nova e mostra o que mudou (sai com 100 se houver)
viper upgrade             mostra o que mudou e pergunta antes de instalar
viper sync                reescreve a biblioteca em todo lugar registrado
```

## A documentação é a sua docstring

'viper docs' lista as funções com a assinatura e a primeira linha da docstring.
'viper docs <função>' mostra a docstring inteira, com os exemplos em azul e o resultado esperado
de cada um em verde. O comando não escreve documentação: ele só lê e formata a que está na
função. Uma função sem docstring aparece avisando que falta.

Os exemplos seguem o formato do 'doctest', da biblioteca padrão. Uma linha que começa com '>>>'
é um uso; a linha logo abaixo é o que ele devolve. Por isso eles valem também como teste:

'''bash
python -m doctest -v src/viper/arsenal.py
'''

## No VS Code

A extensão do [True Coral](https://github.com/GF-Linux/truecoral) traz o snippet de cada função
da viper (digite 'replacement' e aperte Tab: a chamada nasce com o 'lambda x:' já escrito) e
liga o nome dos parâmetros em cinza dentro da chamada.

## Onde ela fica, e o que ela nunca apaga

Em cada lugar a viper vira uma pasta 'viper/' com um arquivo 'INSTALADO_PELO_COMANDO' dentro.
O 'upgrade', o 'sync' e o 'uninstall' só mexem numa pasta que tem esse arquivo. Uma viper que
veio do 'pip' fica como está.

O registro de onde ela foi instalada mora em <~/.local/share/viper/instalacoes.json>.

## Testes

```bash
python -m pytest tests        # ou: python tests/test_viper.py
```

Os testes são do comando. As funções do arsenal se testam pelos exemplos das próprias docstrings.

## Licença

MIT.
