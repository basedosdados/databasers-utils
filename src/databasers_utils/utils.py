import io
import os
import pandas as pd
import numpy as np
import requests
from basedosdados import Backend
from urllib.parse import urlparse, urlunparse, urlencode
from .constants import constants
import ruamel.yaml as yaml


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
        "email": os.getenv(constants.ENV.value["email"]).strip(),  # type: ignore
        "password": os.getenv(constants.ENV.value["password"]).strip(),  # type: ignore
    }


def get_headers(backend: Backend) -> dict[str, str]:
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


def update_dbt_project(dataset_id: str, dir: str) -> None:
    if ["dbt_project.yml", "dbt_project.yaml"] not in os.listdir(dir):
        raise Exception("Failed to find root directory with dbt_project file")

    dbt_project_yaml = f"{dir}/dbt_project.yml"

    if not os.path.exists(dbt_project_yaml):
        dbt_project_yaml = f"{dir}/dbt_project.yaml"

    yaml_obj = yaml.YAML(typ="rt")
    yaml_obj.explicit_start = True
    yaml_obj.indent(mapping=2, sequence=2, offset=2)

    with open(dbt_project_yaml, "r") as file:
        data = yaml_obj.load(file)

    models = data["models"]["basedosdados"]
    models.update(
        {dataset_id: {"+materialized": "table", "+schema": dataset_id}}
    )

    data["models"]["basedosdados"] = {
        key: models[key] for key in sorted(models)
    }

    with open(dbt_project_yaml, "w") as file:
        yaml_obj.dump(data, file)

    print(f"dbt_project successfully updated with {dataset_id}!")
