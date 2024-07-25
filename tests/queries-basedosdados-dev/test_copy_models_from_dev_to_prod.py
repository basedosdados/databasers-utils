import os
import pytest
from databasers_utils import copy_models_from_dev_to_prod

TESTS_DEV_DIR = os.path.join(os.getcwd(), "tests", "queries-basedosdados-dev")


@pytest.mark.dependency(
    depends=[
        "test_table_architecture.test_create_yaml_file",
        "test_table_architecture.test_create_sql_files",
        "test_table_architecture.test_update_dbt_project",
    ]
)
def test_copy_models():
    copy_models_from_dev_to_prod(datasets=["br_ibge_pib"], dir=TESTS_DEV_DIR)
