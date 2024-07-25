import os
from databasers_utils import copy_models_from_dev_to_prod

TESTS_DEV_DIR = os.path.join(os.getcwd(), "tests", "queries-basedosdados-dev")


def test_copy_models():
    copy_models_from_dev_to_prod(datasets=["br_ibge_pib"], dir=TESTS_DEV_DIR)
