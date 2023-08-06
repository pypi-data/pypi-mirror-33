from csv import DictWriter
from json import load

import click


# CSV formatting
END_ID = ":END_ID"
LABELS = ":LABEL"
LABEL_DELIMITER = ";"
START_ID = ":START_ID"
SUBJECT_ID = "subjectId:ID"
TYPE = ":TYPE"


def property_type(value):
    """
    Return the type for given value in Neo4j land.

    """
    if isinstance(value, str):
        return "string"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        # Nb. Python floats are double precision
        return "double"
    elif isinstance(value, bool):
        return "boolean"

    # Default fallback
    return "string"


def property_name(key, type_="string"):
    return f"{key}:{type_}[]"


@click.command()
@click.argument(
    "input_file",
    type=click.File(mode="r"),
)
@click.argument(
    "output_file",
    type=click.File(mode="w"),
)
def export_nodes_main(input_file, output_file):
    """
    Transform nodes from the JSON returned by the `GET /api/v1/node` API endpoint
    to the CSV format expected by `neo4j-admin import`.

    """
    json = load(input_file)
    nodes = json["items"]
    property_names = set(
        property_name(key, type_=property_type(node["properties"][key][0]))
        for node in nodes
        for key in node["properties"]
    )

    fieldnames = [SUBJECT_ID, LABELS, *property_names]
    writer = DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    for node in json["items"]:
        # TODO: properly infer property type from input JSON
        row = {
            SUBJECT_ID: node["id"],
            LABELS: LABEL_DELIMITER.join(node["labels"]),
            **{
                property_name(key, type_=property_type(values[0])): ";".join(values)
                for key, values in node["properties"].items()
            },
        }
        writer.writerow(row)


@click.command()
@click.argument(
    "input_file",
    type=click.File(mode="r"),
)
@click.argument(
    "output_file",
    type=click.File(mode="w"),
)
def export_relationships_main(input_file, output_file):
    """
    Transform relationships from the JSON returned by the `GET /api/v1/relationship` API endpoint
    to the CSV format expected by `neo4j-admin import`.

    """
    json = load(input_file)
    relationships = json["items"]
    property_names = set(
        key
        for relationship in relationships
        for key in relationship["properties"]
    )

    fieldnames = [START_ID, END_ID, TYPE, *property_names]
    writer = DictWriter(output_file, fieldnames=fieldnames)
    writer.writeheader()
    for relationship in json["items"]:
        row = {
            START_ID: relationship["startId"],
            END_ID: relationship["endId"],
            TYPE: relationship["type"],
            **relationship["properties"],
        }
        writer.writerow(row)
