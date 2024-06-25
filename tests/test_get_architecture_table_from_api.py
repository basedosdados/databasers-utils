import pandas as pd
from databasers_utils import get_architecture_table_from_api


def test_get_architecture_table_from_api():
    arch = get_architecture_table_from_api("br_ms_sinasc", "microdados")
    assert isinstance(arch, pd.DataFrame)
    assert len(arch) > 0
