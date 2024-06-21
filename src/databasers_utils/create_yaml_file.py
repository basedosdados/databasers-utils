import os
import re
import ruamel.yaml as yaml
from typing import Optional, Union
from .utils import get_model_directory, read_architecture_table


def extract_column_parts(input_string: str) -> str:
    pattern_1 = re.compile(r"(\w+)\.(\w+):(\w+)")
    pattern_2 = re.compile(r"\w+\.(\w+)\.(\w+):(\w+)")

    if pattern_1.match(input_string):
        return pattern_1.findall(input_string)[0]
    elif pattern_2.match(input_string):
        return pattern_2.findall(input_string)[0]
    else:
        raise ValueError(
            f"Invalid input format on `{input_string}`. Expected format: 'dataset.table:column'"
        )


def extract_relationship_info(input_string: str) -> Optional[tuple[str, str]]:
    try:
        dataset, table, column = extract_column_parts(input_string)

        if column == table:
            column = f"{column}.{column}"

        field = column

        table_path = f"ref('{dataset}__{table}')"

        return table_path, field

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def create_relationships(directory_column: str) -> list[dict[str, str]]:
    relationship_table, relationship_field = extract_relationship_info(
        directory_column
    )  # type: ignore
    yaml_relationship = yaml.comments.CommentedMap()
    yaml_relationship["relationships"] = {
        "to": relationship_table,
        "field": relationship_field,
    }
    return [yaml_relationship]


def create_unique_combination(unique_keys: list[str]) -> list:
    combination = yaml.comments.CommentedMap()
    combination["dbt_utils.unique_combination_of_columns"] = {
        "combination_of_columns": unique_keys
    }
    return [combination]


def create_not_null_proportion(at_least: float) -> list:
    not_null = yaml.comments.CommentedMap()
    not_null["not_null_proportion_multiple_columns"] = {
        "at_least": at_least,
    }
    return [not_null]


def create_dict_coverage(
    dataset_id: str, list_covered_by_dict_columns: list[str]
) -> list:
    dict_coverage = yaml.comments.CommentedMap()
    dict_coverage["custom_dictionaries"] = {
        "columns_covered_by_dictionary": list_covered_by_dict_columns,
        "dictionary_model": f"ref('{dataset_id}__dicionario')",
    }
    return [dict_coverage]


def create_unique() -> list[str]:
    return ["unique", "not_null"]


def create_yaml_file(
    arch_url: Union[str, list[str]],
    table_id: Union[str, list[str]],
    dataset_id: str,
    table_description: str = "Insert table description here",
    at_least: float = 0.95,
    unique_keys: list[str] = ["insert unique keys here"],
    mkdir: bool = True,
    dir: str = os.getcwd(),
) -> str:
    """
    Creates dbt models and schema.yaml files based on the architecture table, including data quality tests automatically.

    Args:
        arch_url (str or list): The URL(s) or file path(s) of the input file(s) containing the data.
        table_id (str or list): The table ID(s) or name(s) to use as the YAML model name(s).
        dataset_id (str): The ID or name of the dataset to be used in the dbt models.
        at_least (float): The proportion of non-null values accepted in the columns.
        unique_keys (list, optional): A list of column names for which the 'dbt_utils.unique_combination_of_columns' test should be applied.
                                      Defaults to ["insert unique keys here"].
        mkdir (bool, optional): If True, creates a directory for the new model(s). Defaults to True.
        preprocessed_staging_column_names (bool, optional):  If True, builds SQL file renaming from 'original_name' to 'name' using the architecture file. Defaults to True.

    Raises:
        TypeError: If the table_id is not a string or a list.
        ValueError: If the number of URLs or file paths does not match the number of table IDs.

    Notes:
        The function generates dbt models in YAML format based on the input data and saves them to the specified output file.
        The generated YAML file includes information about the dataset, model names, descriptions, and column details.

    Example:
        ```python
        create_yaml_file(arch_url='input_data.csv', table_id='example_table', dataset_id='example_dataset')
        ```

    """
    if mkdir:
        models_path = get_model_directory(dir)
        output_path = f"{models_path}/{dataset_id}"
        os.makedirs(output_path, exist_ok=True)
    else:
        print(
            f"Directory for the new model has not been created, saving files in {os.getcwd()}"
        )
        output_path = os.getcwd()

    schema_path = f"{output_path}/schema.yml"

    yaml_obj = yaml.YAML(typ="rt")
    yaml_obj.indent(mapping=4, sequence=4, offset=2)

    if os.path.exists(schema_path):
        with open(schema_path, "r") as file:
            data = yaml_obj.load(file)
    else:
        data = yaml.comments.CommentedMap()
        data["version"] = 2
        data.yaml_set_comment_before_after_key("models", before="\n\n")
        data["models"] = []

    exclude = ["(excluded)", "(erased)", "(deleted)", "(excluido)"]

    if isinstance(table_id, str):
        table_id = [table_id]
        arch_url = [arch_url]  # type: ignore

    # If table_id is a list, assume multiple input files
    if not isinstance(arch_url, list) or len(arch_url) != len(table_id):
        raise ValueError(
            "The number of URLs or file paths must match the number of table IDs."
        )

    for url, id in zip(arch_url, table_id):
        unique_keys_copy = unique_keys.copy()
        architecture_df = read_architecture_table(url)
        architecture_df.dropna(subset=["bigquery_type"], inplace=True)
        architecture_df = architecture_df[
            ~architecture_df["bigquery_type"].apply(
                lambda x: any(word in x.lower() for word in exclude)
            )
        ]

        table = yaml.comments.CommentedMap()
        table["name"] = f"{dataset_id}__{id}"

        # If model is already in the schema.yaml, delete old model from schema and create a new one
        for model in data["models"]:
            if id == model["name"] or table["name"] == model["name"]:
                data["models"].remove(model)
                break

        table["description"] = table_description
        table["tests"] = create_unique_combination(unique_keys_copy)
        table["tests"] += create_not_null_proportion(at_least)

        covered_by_dict_columns = (
            architecture_df["covered_by_dictionary"] == "yes"
        )
        if covered_by_dict_columns.sum():
            list_covered_by_dict_columns = architecture_df[
                covered_by_dict_columns
            ]["name"].tolist()
            table["tests"] += create_dict_coverage(
                dataset_id, list_covered_by_dict_columns
            )

        table["columns"] = []

        for _, row in architecture_df.iterrows():
            column = yaml.comments.CommentedMap()
            column["name"] = row["name"]
            column["description"] = row["description"]
            directory_column = row["directory_column"]
            if len(directory_column.strip()) != 0:
                tests = []
                tests = create_relationships(directory_column)
                column["tests"] = tests
            table["columns"].append(column)

        data["models"].append(table)

    with open(schema_path, "w") as file:
        yaml_obj.dump(data, file)

    return schema_path
