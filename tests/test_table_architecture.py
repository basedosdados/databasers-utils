import os
from databasers_utils import TableArchitecture

TESTS_DIR = os.path.join(os.getcwd(), "tests")


def test_architecture():
    table_arch = TableArchitecture(
        dataset_id="br_ibge_pib",
        tables={
            "uf": "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit?usp=drive_link",
            "gini": "https://docs.google.com/spreadsheets/d/1K1svie4Gyqe6NnRjBgJbapU5sTsLqXWTQUmTRVIRwQc/edit?usp=drive_link",
        },
    )

    arch = table_arch.tables()
    assert "uf" and "gini" in arch.keys()
    assert len(arch) == 2


def test_create_yaml_file():
    table_arch = TableArchitecture(
        dataset_id="br_ibge_pib",
        tables={
            "uf": "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit?usp=drive_link",
            "gini": "https://docs.google.com/spreadsheets/d/1K1svie4Gyqe6NnRjBgJbapU5sTsLqXWTQUmTRVIRwQc/edit?usp=drive_link",
        },
    )

    os.makedirs(os.path.join(TESTS_DIR, "models"), exist_ok=True)

    table_arch.create_yaml_file(dir=TESTS_DIR)

    assert os.path.exists(
        os.path.join(TESTS_DIR, "models", "br_ibge_pib", "schema.yml")
    )


def tnst_create_sql_files():
    table_arch = TableArchitecture(
        dataset_id="br_ibge_pib",
        tables={
            "uf": "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit?usp=drive_link",
            "gini": "https://docs.google.com/spreadsheets/d/1K1svie4Gyqe6NnRjBgJbapU5sTsLqXWTQUmTRVIRwQc/edit?usp=drive_link",
        },
    )

    os.makedirs(os.path.join(TESTS_DIR, "models"), exist_ok=True)

    table_arch.create_sql_files(dir=TESTS_DIR)

    assert os.path.exists(
        os.path.join(
            TESTS_DIR, "models", "br_ibge_pib", "br_ibge_pib__gini.sql"
        )
    )

    assert os.path.exists(
        os.path.join(TESTS_DIR, "models", "br_ibge_pib", "br_ibge_pib__uf.sql")
    )
