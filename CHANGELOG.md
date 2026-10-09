# Changelog

## 0.2.0

- `replacement(lista, palavra, condicao)`: troca por `palavra` cada item em que a condição for
  verdadeira. Nasceu do FizzBuzz. Devolve uma lista nova (uma coluna do pandas volta como coluna,
  com o mesmo índice); recusa a condição crua, sem `lambda`, dizendo o motivo.
- Esta primeira função foi escrita pelo Claude, a pedido do Jared, em 2026-10-09 — o desenho
  (o nome, a ordem dos parâmetros, uma condição por chamada) é dele.

## 0.1.0

- O comando `viper`: `install` (local ou `--global`), `uninstall`, `status`, `docs`,
  `check-update`, `upgrade`, `sync` e o menu. O mesmo fluxo do ratt.
- `viper docs` lê as docstrings do arsenal e destaca os exemplos e os resultados.
- O arsenal começa vazio. A primeira função, `replacement`, nasce à mão.
