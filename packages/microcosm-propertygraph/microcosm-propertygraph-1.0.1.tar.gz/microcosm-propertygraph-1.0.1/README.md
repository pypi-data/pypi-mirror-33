# microcosm-propertygraph

Conventions for exposing a [property graph](https://neo4j.com/developer/graph-database/#property-graph) view of data.


## Exporting to Neo4J

Services which expose the Node/Relationship conventions defined in this package make for easy exporting of data to a Property Graph-style database, e.g. [Neo4J](https://neo4j.com).

This is facilitiated by two API endpoints:

* `GET /api/v1/node` - Enumerate all nodes in the graph, returning their id, types and scalar-valued properties.
* `GET /api/v1/relationship` - Enumerate all relationships between nodes in graph ,returning the start/end node ids, relation type, and relation properties.


## Usage

To load up data into a Neo4j instance, we can use the [Neo4j import](https://neo4j.com/docs/operations-manual/current/tools/import/) functionality to import nodes and relationships from CSV files.

We supply a couple of utility scripts that makes the transformation from the raw API output to required Neo4J import CSV format. Typical usage would look like this:


	http 127.0.0.1:5401/api/v1/node |  neo4j-nodes - nodes.csv
	http 127.0.0.1:5401/api/v1/relationship | neo4j-relationships - relationships.csv
	neo4j_home$ bin/neo4j-admin import --nodes nodes.csv --relationships relationships.csv
