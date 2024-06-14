import io
import pandas as pd
import numpy as np
import requests
from urllib.parse import urlparse, urlunparse, urlencode


def read_architecture_table(url: str) -> pd.DataFrame:
    parsed_url = urlparse(url)

    # Path Format: /spreadsheets/d/<ID>/edit
    # Drop /edit and add "/export"
    new_path = "/".join(parsed_url.path.split("/")[0:-1]) + "/export"

    new_query = urlencode({"format": "csv"}, doseq=True)
    new_url = parsed_url._replace(path=new_path, query=new_query)

    export_url = urlunparse(new_url)

    df_architecture = pd.read_csv(
        io.StringIO(
            requests.get(export_url, timeout=10).content.decode("utf-8")
        )
    )

    df_architecture = df_architecture.loc[
        df_architecture["name"] != "(excluido)"
    ]

    return df_architecture.replace(np.nan, "", regex=True)
