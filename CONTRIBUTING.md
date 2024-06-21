# Contribuindo

## Setup

Requisitos:

- [pyenv](https://github.com/pyenv/pyenv): Recomendado
- [poetry](https://python-poetry.org/)

1. Clone o repositório e entre no diretório clonado

```sh
git clone https://github.com/basedosdados/databasers-utils
```

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
poetry install --with dev --no-root
```

## Code Style

Após finalizar as alterações no código execute:

```sh
poetry run lint
```

> [!IMPORTANT]
> O command vai executar o formatador `ruff format .` e o linter `ruff check --fix .`. Algumas regras do linter requer intervenção manual para ser resolvido

## Testes

Para rodar os testes:

```sh
poetry run pytest
```
