import pandas as pd
import os
from basedosdados import Backend
from .utils import read_architecture_table, find_model_directory
from .create_yaml_file import create_yaml_file
from .update_dbt_project import update_dbt_project_yaml
from .upload_columns import upload_columns_from_architecture
from .constants import constants


class TableArch:
    def __init__(self, dataset_id: str, tables: dict[str, str]):
        self.dataset_id = dataset_id
        self.__tables = tables

    def __str__(self) -> str:
        return f"TableArch({self.dataset_id}, {str(self.__tables)})"

    def tables(self) -> dict[str, pd.DataFrame]:
        return {k: read_architecture_table(v) for k, v in self.__tables.items()}

    def create_yaml_file(
        self,
        table_description: str = "Insert table description here",
        at_least: float = 0.95,
        unique_keys: list[str] = ["insert unique keys here"],
        mkdir: bool = True,
        dir: str = os.getcwd(),
    ) -> None:
        path = create_yaml_file(
            arch_url=list(self.__tables.values()),
            table_id=list(self.__tables.keys()),
            dataset_id=self.dataset_id,
            table_description=table_description,
            at_least=at_least,
            unique_keys=unique_keys,
            mkdir=mkdir,
            dir=dir,
        )
        print(f"Files successfully created for {self.dataset_id} at {path}")
        return None

    def create_sql_files(
        self,
        preprocessed_staging_column_names: bool = True,
        dir: str = os.getcwd(),
    ) -> None:
        models_dir = find_model_directory(dir)

        output_path = f"{models_dir}/{self.dataset_id}"

        for table_id, url in self.__tables.items():
            architecture_df = read_architecture_table(url)

            if preprocessed_staging_column_names:
                architecture_df["original_name"] = architecture_df["name"]

            header = f'{{{{ config(alias="{table_id}", schema="{self.dataset_id}") }}}}'

            with open(
                f"{output_path}/{self.dataset_id}__{table_id}.sql", "w"
            ) as file:
                file.write(header + "\n")
                file.write("select\n")

                for _, column in architecture_df.iterrows():
                    original_name = column["original_name"]
                    column_name = column["name"]
                    bq_type = column["bigquery_type"].lower()  # type: ignore

                    sql_line = f"    safe_cast({original_name} as {bq_type}) {column_name},\n"
                    file.write(sql_line)

                sql_last_line = f"from `basedosdados-dev.{self.dataset_id}_staging.{table_id}` as t\n"
                file.write(sql_last_line)

        print("SQL files created!")
        return None

    def update_dbt_project(self) -> None:
        update_dbt_project_yaml(self.dataset_id, dir=os.getcwd())
        return None

    def upload_columns(self, replace_all_schema: bool = True) -> None:
        backend = Backend(graphql_url=constants.API_URL.value["prod"])
        for table_id, url in self.__tables.items():
            upload_columns_from_architecture(
                dataset_id=self.dataset_id,
                table_slug=table_id,
                url_architecture=url,
                replace_all_schema=replace_all_schema,
                backend=backend,
            )
        return None
