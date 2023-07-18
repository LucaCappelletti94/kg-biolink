# kg-biolink
A knowledge graph for the BioLink metadata standard

## Building the latest version of the KG
To build the latest version of the KG, run the following:

```bash
python pipeline.py
```

## Loading the graph with GRAPE
After cloning the repository, you can load the graph with GRAPE by running the following:

```python
from grape import Graph

kg = Graph.from_csv(
    node_path="kg_biolink_nodes_3.5.1.tsv",
    nodes_column="node_name",
    node_list_node_types_column="node_type",
    node_types_separator="|",
    edge_path="kg_biolink_edges_3.5.1.tsv",
    sources_column="source",
    destinations_column="destination",
    edge_list_edge_types_column="edge_type",
    name="KGBioLink",
    directed=True
)
```