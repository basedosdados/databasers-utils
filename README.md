# databasers-utils

- [CONTRIBUTING.md](./CONTRIBUTING.md)

## Instalação

```sh
poetry add git+https://github.com/basedosdados/databasers-utils.git
```

## Setup

### Credenciais

Para fazer o upload de colunas usando a arquitetura você deve configurar suas
credenciais.

#### Linux/WSL

Adicione no seu `.bashrc` ou `.zshrc`

```sh
export BD_DJANGO_EMAIL="seuemail@basedosdados.org"
export BD_DJANGO_PASSWORD="password"
```

#### Windows

- Right-click on 'This PC' or 'My Computer' and select 'Properties'.
- Click on 'Advanced system settings'.
- Click the 'Environment Variables' button.
- In the 'System variables' section, click 'New...' and enter OPENAI_API_KEY as the variable name and your API key as the variable value.

1. Em Pesquisar, procure e selecione: Sistema (Painel de Controle)
2. Clique no link Configurações avançadas do sistema.
3. Clique em Variáveis de Ambiente. 
4. Na seção 'Variáveis do Sistema' clique em 'Novo' e insira `BD_DJANGO_EMAIL` como nome da variável e o seu email como valor. Faça o mesmo para `BD_DJANGO_PASSWORD`.
5. Clique em OK. Feche todas as janelas restantes clicando em OK.

### Uso

```python
from databasers_utils import TableArch, copy_models_from_dev_to_prod

arch = TableArch(
    dataset_id="br_ibge_pib",
    tables={
        "uf": "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit?usp=drive_link",
        "gini": "https://docs.google.com/spreadsheets/d/1K1svie4Gyqe6NnRjBgJbapU5sTsLqXWTQUmTRVIRwQc/edit?usp=drive_link",
    },
)

# Retorna um dict[str, pd.DataFrame], cada chave o id da tabela e o dataframe
# da arquitetura
arch.tables()

# Cria o yaml file
arch.create_yaml_file()

# Cria os arquivos sql
arch.create_sql_files()

# Atualiza o dbt_project.yml
arch.update_dbt_project()

# Faz o upload das colunas para o DJango
arch.upload_columns()

# Copia os modelos em dev para prod
copy_models_from_dev_to_prod(["br_ibge_ppm", "br_ibge_pam"])
```
