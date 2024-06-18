import ruamel.yaml as yaml
import os


def update_dbt_project_yaml(dataset_id: str, dir: str) -> None:
    if "dbt_project.yml" not in os.listdir(dir):
        raise Exception(
            "Failed to find root direcoty with dbt_project.yml file"
        )

    dbt_project_path = f"{dir}/dbt_project.yml"

    yaml_obj = yaml.YAML(typ="rt")
    yaml_obj.explicit_start = True
    yaml_obj.indent(mapping=2, sequence=2, offset=2)

    with open(dbt_project_path, "r") as file:
        data = yaml_obj.load(file)

    models = data["models"]["basedosdados"]
    models.update(
        {dataset_id: {"+materialized": "table", "+schema": dataset_id}}
    )

    data["models"]["basedosdados"] = {
        key: models[key] for key in sorted(models)
    }

    with open(dbt_project_path, "w") as file:
        yaml_obj.dump(data, file)

    print(f"dbt_project successfully updated with {dataset_id}!")
