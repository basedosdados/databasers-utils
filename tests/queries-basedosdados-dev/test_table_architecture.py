import os
import pytest
import pandas as pd
import ruamel.yaml as yaml
import sys
from databasers_utils import TableArchitecture

TESTS_DEV_DIR = os.path.join(os.getcwd(), "tests", "queries-basedosdados-dev")


def test_architecture():
    table_arch = TableArchitecture(
        dataset_id="br_ibge_pib",
        tables={
            "uf": "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit?usp=drive_link",
            "gini": "https://docs.google.com/spreadsheets/d/1K1svie4Gyqe6NnRjBgJbapU5sTsLqXWTQUmTRVIRwQc/edit?usp=drive_link",
        },
    )

    tables = table_arch.tables()
    assert "uf" and "gini" in tables.keys()
    assert isinstance(tables["uf"], pd.DataFrame)
    assert isinstance(tables["gini"], pd.DataFrame)
    assert len(tables) == 2


@pytest.mark.dependency()
def test_create_yaml_file():
    table_arch = TableArchitecture(
        dataset_id="br_ibge_pib",
        tables={
            "uf": "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit?usp=drive_link",
            "gini": "https://docs.google.com/spreadsheets/d/1K1svie4Gyqe6NnRjBgJbapU5sTsLqXWTQUmTRVIRwQc/edit?usp=drive_link",
        },
    )

    os.makedirs(os.path.join(TESTS_DEV_DIR, "models"), exist_ok=True)

    table_arch.create_yaml_file(dir=TESTS_DEV_DIR)

    assert os.path.exists(
        os.path.join(TESTS_DEV_DIR, "models", "br_ibge_pib", "schema.yml")
    )


@pytest.mark.dependency()
def test_create_sql_files():
    table_arch = TableArchitecture(
        dataset_id="br_ibge_pib",
        tables={
            "uf": "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit?usp=drive_link",
            "gini": "https://docs.google.com/spreadsheets/d/1K1svie4Gyqe6NnRjBgJbapU5sTsLqXWTQUmTRVIRwQc/edit?usp=drive_link",
        },
    )

    os.makedirs(os.path.join(TESTS_DEV_DIR, "models"), exist_ok=True)

    table_arch.create_sql_files(dir=TESTS_DEV_DIR)

    assert os.path.exists(
        os.path.join(
            TESTS_DEV_DIR, "models", "br_ibge_pib", "br_ibge_pib__gini.sql"
        )
    )

    assert os.path.exists(
        os.path.join(
            TESTS_DEV_DIR, "models", "br_ibge_pib", "br_ibge_pib__uf.sql"
        )
    )


@pytest.mark.dependency()
def test_update_dbt_project():
    table_arch = TableArchitecture(
        dataset_id="br_ibge_pib",
        tables={
            "uf": "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit?usp=drive_link",
            "gini": "https://docs.google.com/spreadsheets/d/1K1svie4Gyqe6NnRjBgJbapU5sTsLqXWTQUmTRVIRwQc/edit?usp=drive_link",
        },
    )

    yaml_obj = yaml.YAML(typ="rt")
    yaml_obj.indent(mapping=2, sequence=4, offset=2)

    DBT_PROJECT_PATH = os.path.join(TESTS_DEV_DIR, "dbt_project.yml")

    with open(DBT_PROJECT_PATH, "r") as file:
        content = yaml_obj.load(file)
        file.close()

    assert content["models"]["basedosdados"].get("br_ibge_pib") is None

    table_arch.update_dbt_project(dir=TESTS_DEV_DIR)

    yaml_obj_2 = yaml.YAML(typ="rt")
    yaml_obj_2.indent(mapping=2, sequence=4, offset=2)

    with open(DBT_PROJECT_PATH, "r") as file:
        content_updated = yaml_obj_2.load(file)
        file.close()

    # Inspect changes
    yaml_obj_2.dump(content_updated, sys.stdout)

    added = content_updated["models"]["basedosdados"]["br_ibge_pib"]
    assert added["+materialized"] == "table"
    assert added["+schema"] == "br_ibge_pib"

    # Restore changes
    with open(DBT_PROJECT_PATH, "w") as io:
        yaml_obj.dump(content, io)
        io.close()
