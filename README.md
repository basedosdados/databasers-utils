# databasers-utils

## Setup

1. Ative a versão 3.9 do Python

```sh
pyenv shell 3.9
```

2. Crie a env ou ativa se já existir

```sh
poetry shell
```

3. Instale as dependências

```sh
poetry install
```

## Aplicando o lint

> [!IMPORTANT]
> O command vai executar o formatador `ruff format .` e o linter `ruff check --fix .`. Algumas regras do linter requer intervenção manual para ser resolvido

```sh
poetry run lint
```

## Executando testes

```sh
poetry run pytest
```

## Adicionando `databasers-utils` como dependência em um projeto

```sh
poetry add git+https://github.com/basedosdados/databasers-utils.git
```

## Uso básico

```python
import databasers_utils

df_arch = databasers_utils.read_architecture_table(
    "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit?usp=drive_link"
)
```
