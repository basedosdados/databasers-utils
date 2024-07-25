import os
from typing import Optional
from distutils.dir_util import copy_tree
from .utils import update_dbt_project


def change_origin_from_dev_to_staging(
    file: str, prod_models_dataset_dir: str
) -> None:
    sql_file = f"{prod_models_dataset_dir}/{file}"

    with open(sql_file, "r") as io:
        sql_content = io.read()

    new_sql_content = sql_content.replace(
        "basedosdados-dev.", "basedosdados-staging."
    )

    with open(sql_file, "w") as io:
        io.write(new_sql_content)


def search_model_directory_recursive(directory: str) -> Optional[str]:
    # Check if 'model' is in the current directory
    ls_dir = os.listdir(directory)
    if "models" in ls_dir:
        return os.path.join(directory, "models")

    if "queries-basedosdados-dev" in ls_dir:
        return os.path.join(directory, "queries-basedosdados-dev", "models")

    # Get the parent directory
    parent_directory = os.path.dirname(directory)

    # If we've reached the root directory without finding 'model', return None
    if directory == parent_directory:
        return None

    # Otherwise, continue searching recursively in parent directories
    return search_model_directory_recursive(parent_directory)


def copy_models_from_dev_to_prod(
    datasets: list[str], dir: str = os.getcwd()
) -> None:
    dev_models_path = search_model_directory_recursive(dir)

    if dev_models_path is None:
        raise Exception(f"Failed to find model directory at {dir}")

    prod_models_dir = dev_models_path.replace(
        "queries-basedosdados-dev", "queries-basedosdados"
    )

    if not os.path.exists(prod_models_dir):
        raise Exception(
            f"Prod models directory not exists at {prod_models_dir}"
        )

    # Go to root of queries-basedosdados
    root_prod = os.path.dirname(prod_models_dir)

    for dataset_id in datasets:
        prod_models_dataset_dir = f"{prod_models_dir}/{dataset_id}"
        copy_tree(
            f"{dev_models_path}/{dataset_id}", prod_models_dataset_dir, update=1
        )
        update_dbt_project(dataset_id, dir=root_prod)
        [
            change_origin_from_dev_to_staging(file, prod_models_dataset_dir)
            for file in os.listdir(prod_models_dataset_dir)
            if file.endswith(".sql")
        ]
