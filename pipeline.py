import yaml
import requests
import pandas as pd
import compress_json

if __name__ == '__main__':
    # Retrieve the biolink yaml file.
    # Do note that there also exists a JSON version, but
    # it does not come with all of the definitions or descriptions
    data = yaml.safe_load(requests.get(
        "https://raw.githubusercontent.com/biolink/biolink-model/master/biolink-model.yaml"
    ).text)

    # We retrieve the version of the current data
    version = data["version"]

    # Set of the keys to keep
    category_keys = ("types", "slots", "classes",)

    metadata = compress_json.local_load("metadata.json")

    nodes = pd.DataFrame([
        dict(
            node_name=src,
            description=node_metadata.get("description", ""),
            node_type="|".join([
                label
                for label in [
                    node_metadata.get(node_type, "")
                    for node_type in metadata["node_types"]
                ]
                if label != ""
            ])
        )
        for group_name, group in data.items()
        if group_name in category_keys
        for main_src, node_metadata in group.items()
        for src in [
            sub_src
            for node_alias_link in metadata["node_alias_links"]
            for sub_src in (
                node_metadata.get(node_alias_link, [])
                if isinstance(node_metadata.get(node_alias_link, []), list)
                else [node_metadata[node_alias_link]]
            )
        ] + [main_src]
        if src != "" and src is not None
    ])
    nodes.drop_duplicates("node_name", inplace=True)
    nodes.reset_index(drop=True, inplace=True)

    edges = pd.DataFrame([
        dict(
            source=src,
            edge_type=edge_type,
            destination=dst.strip()
        )
        for group_name, group in data.items()
        if group_name in category_keys
        for main_src, node_metadata in group.items()
        for edge_type in metadata["edge_types"]
        for dst in (
            node_metadata.get(edge_type, [])
            if isinstance(node_metadata.get(edge_type, []), list)
            else [node_metadata[edge_type]]
        )
        for src in [
            sub_src.strip()
            for node_alias_link in metadata["node_alias_links"]
            for sub_src in (
                node_metadata.get(node_alias_link, [])
                if isinstance(node_metadata.get(node_alias_link, []), list)
                else [node_metadata[node_alias_link]]
            )
        ] + [main_src]
        if src != "" and dst != "" and src is not None and dst is not None
    ])
    edges.drop_duplicates(inplace=True)
    edges.reset_index(drop=True, inplace=True)
    
    missing_node_names = (set(edges.source) | set(edges.destination)) - set(nodes.node_name)

    nodes = pd.concat([
        nodes,
        pd.DataFrame([
            dict(
                node_name=node_name,
            )
            for node_name in missing_node_names
        ])
    ])

    nodes.to_csv(f"kg_biolink_nodes_{version}.tsv", index=False, sep="\t")
    edges.to_csv(f"kg_biolink_edges_{version}.tsv", index=False, sep="\t")