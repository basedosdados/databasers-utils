import json
import pandas as pd
from basedosdados import backend as b
from .utils import get_headers, read_architecture_table
from typing import Optional


def get_directory_column_id(
    directory_column_name: str,
    directory_table_name: str,
    backend: b.Backend,
    verbose: bool = False,
) -> str:
    """
    Get the directory id from that column
    """
    query = """ query($column_name: String)
        {allColumn(name: $column_name) {
                edges {
                node {
                    name
                    _id
                    table {
                    dataset {
                        fullSlug
                    }
                    slug
                    }
                }
                }
            }
            }
    """

    variables = {"column_name": directory_column_name}
    response = backend._execute_query(query=query, variables=variables)[
        "allColumn"
    ]["items"]
    df = pd.json_normalize(response)

    colunas_de_diretorio = df[
        df["table.dataset.fullSlug"].str.contains("diretorios") == True  # noqa: E712
    ]

    for _, coluna in colunas_de_diretorio.iterrows():
        if coluna["table.slug"] == directory_table_name:
            if verbose:
                print(
                    f"Connecting to the directory column: {coluna['table.dataset.fullSlug']}.{coluna['table.slug']}:{coluna['name']}"
                )

            return coluna["_id"]  # type: ignore

    raise (
        ValueError(
            f"WARNING - Unable to find the directory column with the following information: Column name: {directory_column_name}. Table: {directory_table_name}"
        )
    )


def create_column(
    backend: b.Backend,
    mutation_parameters: Optional[dict[str, str]] = None,
    verbose: bool = False,
) -> bool:
    ## tinha que ser create or replace, por enquanto ele duplica
    ## os dados se rodar duas vezes por isso atenção na hora de rodar!

    # GraphQL mutation to create or update a column
    mutation = """
                    mutation($input: CreateUpdateColumnInput!) {
                        CreateUpdateColumn(input: $input) {
                            errors {
                                field,
                                messages
                            },
                            clientMutationId,
                            column {
                                id,
                            }
                        }
                    }
        """

    # Set headers for the GraphQL request, including the token for authentication
    headers = get_headers(backend)

    # Print the mutation parameters for debugging purposes
    pretty_json = json.dumps(mutation_parameters, indent=4)

    if verbose:
        print(pretty_json)

    # Execute the GraphQL query with the provided mutation parameters and headers
    response = backend._execute_query(
        query=mutation,
        variables={"input": mutation_parameters},  # type: ignore
        headers=headers,
    )

    # Print the response for debugging purposes
    if response["CreateUpdateColumn"]["errors"] != []:
        pretty_json = json.dumps(response, indent=4)

        if verbose:
            print(pretty_json)

        return False

    return True


def get_column_id(
    table_id: str, column_name: str, backend: b.Backend
) -> Optional[str]:
    query = f"""{{
        allColumn(table_Id:"{table_id}", name:"{column_name}"){{
        edges{{
            node{{
            _id
            }}
        }}
        }}
    }}"""

    data = backend._execute_query(query=query)["allColumn"]["items"]

    if len(data) > 0:
        return data[0]["_id"]
    else:
        return None


def get_n_columns(table_id, backend: b.Backend):
    query = f"""query get_n_columns{{
        allTable(id:"{table_id}"){{
            edges{{
            node{{
                columns{{
                edgeCount
                }}
            }}
            }}
        }}
        }}"""

    data = backend._execute_query(query=query)["allTable"]["items"]

    return data[0]["columns"]["edgeCount"]


def get_bqtype_dict(backend: b.Backend):
    # GraphQL query to fetch all BigQuery types
    query = """{
    allBigquerytype{
      edges{
        node{
          name
          _id
        }
      }
    }
  }"""

    # Execute the GraphQL query to retrieve the data
    data = backend._execute_query(query=query)["allBigquerytype"]["items"]

    # Create a dictionary where the 'name' part is the key and the '_id' is the value
    bqtype_dict = {item["name"]: item["_id"] for item in data}

    # Return the resulting dictionary
    return bqtype_dict


def check_metadata_columns(
    dataset_id: str,
    table_slug: str,
    backend: b.Backend,
    architecture: pd.DataFrame,
) -> None:
    # Get the table ID using the dataset ID and table ID
    table_id = backend._get_table_id_from_name(
        gcp_dataset_id=dataset_id, gcp_table_id=table_slug
    )

    n_columns_metadata = get_n_columns(table_id=table_id, backend=backend)
    n_columns_architecture = architecture.shape[0]

    if n_columns_metadata == n_columns_architecture:
        print("Upload done!!. Columns metadata equal to columns architecture!!")
    else:
        print(
            f"Something wrong!!. Number of metadata columns not equal to architecture, {n_columns_metadata} != {n_columns_architecture}"
        )


def get_all_columns_id(table_id: str, backend: b.Backend):
    query = f"""{{
        allColumn(table_Id:"{table_id}"){{
        edges{{
            node{{
            _id
            }}
        }}
        }}
    }}"""

    data = backend._execute_query(query=query)["allColumn"]["items"]

    if data:
        columns_list = [col["_id"] for col in data]
        return columns_list
    else:
        print("There is no column in this table to be deleted")


def delete_column_by_id(column_id: str, backend: b.Backend) -> bool:
    mutation = """
                    mutation($input: UUID!) {
                        DeleteColumn(id: $input) {
                            errors,
                            ok
                        }
                    }
        """

    # Set headers for the GraphQL request, including the token for authentication
    headers = get_headers(backend)
    # Execute the GraphQL query with the provided mutation parameters and headers
    response = backend._execute_query(
        query=mutation, variables={"input": column_id}, headers=headers
    )

    # Print the response for debugging purposes
    if response["DeleteColumn"]["errors"] != []:
        pretty_json = json.dumps(response, indent=4)
        print(pretty_json)
        return False

    return True


def delete_all_columns(table_id: str, backend: b.Backend) -> None:
    columns = get_all_columns_id(table_id, backend)

    if columns is not None:
        for col in columns:
            delete_column_by_id(col, backend)


def upload_columns_from_architecture(
    dataset_id: str,
    table_id: str,
    url_architecture: str,
    backend: b.Backend,
    if_column_exists: str = "pass",
    replace_all_schema: bool = True,
    verbose: bool = False,
) -> None:
    """
    Uploads columns from an architecture table to the specified dataset and table in  platform.

    Notes:
    - This function assumes a specific structure/format for the architecture table.
    - It interacts with the Base dos Dados GraphQL API to create or update columns.
    - Columns from the architecture table are uploaded to the specified dataset and table.
    - It prints information about the existing columns
    and performs metadata checks after uploading columns.
    """
    accepted_if_exists_values = ["pass", "replace"]

    if if_column_exists not in accepted_if_exists_values:
        raise ValueError(
            f"`if_exists` only accepts {accepted_if_exists_values}"
        )

    # Get the table ID using the dataset ID and table ID
    table_slug = backend._get_table_id_from_name(
        gcp_dataset_id=dataset_id, gcp_table_id=table_id
    )

    # Read the architecture table
    architecture = read_architecture_table(url=url_architecture)

    # Get the id of BigQueryTypes in a dict
    bqtype_dict = get_bqtype_dict(backend)

    if replace_all_schema:
        delete_all_columns(table_slug, backend)

    # Iterate over each row in the 'architecture' DataFrame
    for _, row in architecture.iterrows():
        column_name = row["name"]

        if verbose:
            print(f"\nColumn: {column_name}")

        column_id = get_column_id(
            table_id=table_slug,
            column_name=column_name,
            backend=backend,
        )

        if column_id is None and verbose:
            print(f"{column_name} dont exists")

        if column_id is not None and if_column_exists == "pass":
            if verbose:
                print("row already exists")
            continue

        # Define the mutation parameters for creating a new column
        directory_column_id = None
        if row["directory_column"]:
            directory_table_slug = (
                row["directory_column"].split(":")[0].split(".")[1]
            )
            directory_column_name = row["directory_column"].split(":")[1]
            directory_column_id = get_directory_column_id(
                directory_column_name, directory_table_slug, backend, verbose
            )

        row_bq_type = row["bigquery_type"].strip().upper()
        bigquery_type = "BOOLEAN" if row_bq_type == "BOOL" else row_bq_type

        mutation_parameters = {
            "table": table_slug,
            "bigqueryType": bqtype_dict[bigquery_type],
            "name": row["name"],
            "description": row["description"],
            "coveredByDictionary": row["covered_by_dictionary"] == "yes",
            "measurementUnit": row["measurement_unit"],
            "containsSensitiveData": row["has_sensitive_data"] == "yes",
            "observations": row["observations"],
            "directoryPrimaryKey": directory_column_id,
        }

        if column_id is not None:
            mutation_parameters["id"] = column_id

        create_column(
            backend, mutation_parameters=mutation_parameters, verbose=verbose
        )

    check_metadata_columns(
        dataset_id=dataset_id,
        table_slug=table_id,
        backend=backend,
        architecture=architecture,
    )
