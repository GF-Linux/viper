# Changelog

## 0.2.1

- `viper install --global` num Python que já tem a viper (do `pip install --user`) não dá mais
  "nada a fazer" com código de erro: diz que ela já está ali, e sai com 0.
- `viper install --global` dentro de uma pasta com ambiente virtual (`.venv/`) agora avisa na hora:
  o ambiente virtual não enxerga o global, e o `import viper` ali (e no VS Code) daria
  `ModuleNotFoundError`. Para o projeto: `viper install`.

## 0.2.0

- `replacement(lista, palavra, condicao)`: troca por `palavra` cada item em que a condição for
  verdadeira. Nasceu do FizzBuzz. Devolve uma lista nova (uma coluna do pandas volta como coluna,
  com o mesmo índice); recusa a condição crua, sem `lambda`, dizendo o motivo.


## 0.1.0

- O comando `viper`: `install` (local ou `--global`), `uninstall`, `status`, `docs`,
  `check-update`, `upgrade`, `sync` e o menu. O mesmo fluxo do ratt.
- `viper docs` lê as docstrings do arsenal e destaca os exemplos e os resultados.
- O arsenal começa vazio.
