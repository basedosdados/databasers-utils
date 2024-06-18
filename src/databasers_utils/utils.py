import io
import os
import pandas as pd
import numpy as np
import requests
from urllib.parse import urlparse, urlunparse, urlencode
import basedosdados as bd


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


def get_credentials_from_env() -> dict[str, str]:
    return {
        "email": os.getenv("BD_DJANGO_EMAIL").strip(),  # type: ignore
        "password": os.getenv("BD_DJANGO_PASSWORD").strip(),  # type: ignore
    }


def get_headers(backend: bd.Backend) -> dict[str, str]:
    """
    Get headers to be able to do mutations in backend api
    """

    credentials = get_credentials_from_env()

    mutation = """
        mutation ($email: String!, $password: String!) {
            tokenAuth(email: $email, password: $password) {
                token
            }
        }
    """

    variables = {
        "email": credentials["email"],
        "password": credentials["password"],
    }

    response = backend._execute_query(query=mutation, variables=variables)
    token = response["tokenAuth"]["token"]

    header_for_mutation_query = {"Authorization": f"Bearer {token}"}

    return header_for_mutation_query


def find_model_directory(dir: str) -> str:
    model_dir = f"{dir}/models"
    if os.path.exists(model_dir):
        return model_dir
    else:
        raise Exception(f"Failed to find models directory under {dir}")


# def find_model_directory(directory: str) -> str | None:
#     # Check if 'model' is in the current directory
#     if "models" in os.listdir(directory):
#         return os.path.join(directory, "models")
#
#     if "queries-basedosdados-dev" in os.listdir(directory):
#         return os.path.join(directory, "queries-basedosdados-dev", "models")
#
#     # Get the parent directory
#     parent_directory = os.path.dirname(directory)
#
#     # If we've reached the root directory without finding 'model', return None
#     if directory == parent_directory:
#         return None
#
#     # Otherwise, continue searching recursively in parent directories
#     return find_model_directory(parent_directory)
