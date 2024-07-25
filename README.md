# databasers-utils

Pacote para uso da equipe de dados na Base dos Dados.

- [CONTRIBUTING.md](./CONTRIBUTING.md)

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

- Em Pesquisar, procure e selecione: Sistema (Painel de Controle)
- Clique no link Configurações avançadas do sistema.
- Clique em Variáveis de Ambiente. 
- Na seção 'Variáveis do Sistema' clique em 'Novo' e insira `BD_DJANGO_EMAIL` como nome da variável e o seu email como valor. Faça o mesmo para `BD_DJANGO_PASSWORD`.
- Clique em OK. Feche todas as janelas restantes clicando em OK.

### Uso

```python
from databasers_utils import (
    TableArchitecture,
    copy_models_from_dev_to_prod,
    get_architecture_table_from_api,
)

arch = TableArchitecture(
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

# Retorna um DataFrame da arquitetura obtida na API
# Util para gerar arquitetura quando ela não está no Drive
get_architecture_table_from_api("br_ms_sinasc", "microdados")
```
