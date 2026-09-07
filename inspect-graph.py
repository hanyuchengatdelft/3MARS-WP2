import networkx as nx
import numpy as np
import pandas as pd

nodes = pd.read_csv("nodes.csv")
links = pd.read_csv("links.csv", dtype={"operator": str})

# Basic table integrity
assert nodes["node_id"].notna().all(), "Missing node IDs"
assert nodes["node_id"].is_unique, "Duplicate node IDs"

assert links[["src", "trg"]].notna().all().all(), "Missing link endpoints"
assert links["time"].notna().all(), "Missing travel times"
assert np.isfinite(links["time"]).all(), "Non-finite travel times"
assert links["time"].gt(0).all(), "Non-positive travel times"

assert nodes["lon"].between(-180, 180).all(), "Invalid longitude"
assert nodes["lat"].between(-90, 90).all(), "Invalid latitude"

node_ids = set(nodes["node_id"])
link_node_ids = set(links["src"]) | set(links["trg"])

unknown_nodes = link_node_ids - node_ids
assert not unknown_nodes, f"Links reference unknown nodes: {unknown_nodes}"

# operator and frequency are absent only for car links
non_car = links["mode"].ne("Car")
assert links.loc[non_car, "operator"].notna().all()
assert links.loc[non_car, "freq"].notna().all()
assert links["freq"].dropna().gt(0).all()

# Construct a directed multigraph
G = nx.MultiDiGraph()

for row in nodes.itertuples(index=False):
    attributes = row._asdict()
    node_id = attributes.pop("node_id")
    G.add_node(node_id, **attributes)

for row in links.itertuples(index=False):
    attributes = row._asdict()
    src = attributes.pop("src")
    trg = attributes.pop("trg")
    G.add_edge(src, trg, **attributes)

# Verify that construction did not lose records
assert G.number_of_nodes() == len(nodes)
assert G.number_of_edges() == len(links)

# Network statistics
weak_components = list(nx.weakly_connected_components(G))
strong_components = list(nx.strongly_connected_components(G))
isolated_nodes = list(nx.isolates(G))

# Density is easier to interpret after ignoring parallel links
simple_G = nx.DiGraph(G)

stats = pd.Series({
    "Nodes": f"{G.number_of_nodes():,}",
    "Links": f"{G.number_of_edges():,}",
    "Isolated nodes": f"{len(isolated_nodes):,}",
    "Self links": f"{nx.number_of_selfloops(G):,}",
    "Weak Components": f"{len(weak_components):,}",
    "Largest weak component": f"{max(map(len, weak_components)):,}",
    "Strong components": f"{len(strong_components):,}",
    "Largest strong component": f"{max(map(len, strong_components)):,}",
    "Simple directed density": f"{nx.density(simple_G):.2f}",
    "Mean in-degree": f"{sum(dict(G.in_degree()).values()) / len(G):.2f}",
    "Mean out-degree": f"{sum(dict(G.out_degree()).values()) / len(G):.2f}",
}, name="value").rename_axis("metric").reset_index().assign(category="Graph")

stats = [("Graph", k, v) for k, v in {
    "Nodes": f"{G.number_of_nodes():,}",
    "Links": f"{G.number_of_edges():,}",
    "Isolated nodes": f"{len(isolated_nodes):,}",
    "Self links": f"{nx.number_of_selfloops(G):,}",
    "Weak Components": f"{len(weak_components):,}",
    "Largest weak component": f"{max(map(len, weak_components)):,}",
    "Strong components": f"{len(strong_components):,}",
    "Largest strong component": f"{max(map(len, strong_components)):,}",
    "Simple directed density": f"{nx.density(simple_G):.2f}",
    "Mean in-degree": f"{sum(dict(G.in_degree()).values()) / len(G):.2f}",
    "Mean out-degree": f"{sum(dict(G.out_degree()).values()) / len(G):.2f}",
}.items()]
# Node types
stats.extend([
    ("Node types", k, str(v)) for k, v in 
    nodes["kind"].value_counts().sort_index().items()
])
# Link types
stats.extend([
    ("Link types", k, f"{v:,}") for k, v in 
    links["kind"].value_counts().sort_index().items()
])
# Link modes
stats.extend([
    ("Link modes", k, f"{v:,}") for k, v in 
    links["mode"].value_counts().sort_index().items()
])
df = pd.DataFrame(stats, columns=["Category", "Indicator", "Value"])
print("Summary statistics:")
print(df.set_index(["Category", "Indicator"]))

print("\nIsolated nodes:")
print(nodes.loc[nodes["node_id"].isin(isolated_nodes)])
