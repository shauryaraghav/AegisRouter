import pandas as pd
import networkx as nx
from scipy.spatial import cKDTree
import numpy as np

print("Building optimized graph...")


nodes = pd.read_csv("data/nodes.csv", dtype={"osmid": str})
edges = pd.read_csv(
    "data/edges.csv",
    dtype={"u": str, "v": str}
)

crime = pd.read_csv("data/crime.csv")
accidents = pd.read_csv("data/accidents.csv")
traffic = pd.read_csv("data/traffic.csv")
crowd = pd.read_csv("data/crowd.csv")
weather = pd.read_csv("data/weather.csv")


def fix(df):
    df.columns = df.columns.str.lower()
    return df

crime = fix(crime)
accidents = fix(accidents)
traffic = fix(traffic)
crowd = fix(crowd)


crime["crime_risk"] = 1
accidents["accident_risk"] = 2
traffic["traffic_risk"] = traffic.get("all_motor_vehicles", 1) / 1000
crowd["crowd_score"] = crowd.get("crowd_score", 1)


G = nx.Graph()

for _, row in nodes.iterrows():
    if "x" in row and "y" in row:
        G.add_node(row["osmid"], x=float(row["x"]), y=float(row["y"]))
    elif "lon" in row and "lat" in row:
        G.add_node(row["osmid"], x=float(row["lon"]), y=float(row["lat"]))
    else:
        continue  # skip broken rows safely

if pd.notna(row["x"]) and pd.notna(row["y"]):
    G.add_node(
        row["osmid"],
        x=float(row["x"]),
        y=float(row["y"])
    )

for _, row in edges.iterrows():
    G.add_edge(row["u"], row["v"], length=row["length"])

print(" Graph created")


def build_tree(df):
    if "latitude" in df.columns:
        coords = np.vstack((df["latitude"], df["longitude"])).T
    elif "lat" in df.columns:
        coords = np.vstack((df["lat"], df["lon"])).T
    else:
        return None
    return cKDTree(coords)

crime_tree = build_tree(crime)
acc_tree = build_tree(accidents)
traffic_tree = build_tree(traffic)
crowd_tree = build_tree(crowd)


weather_risk = weather["weather_risk"].mean()


print(" Mapping risks to edges...")

for u, v, data in G.edges(data=True):
    if 'x' not in G.nodes[u] or 'x' not in G.nodes[v]:
      continue

    x = (G.nodes[u]['x'] + G.nodes[v]['x']) / 2
    y = (G.nodes[u]['y'] + G.nodes[v]['y']) / 2

    def get_val(tree, df, col):
        if tree is None:
         return 0
        _, idx = tree.query([y, x])  # y=lat, x=lon ✔
        return df.iloc[idx][col]

    data["crime_risk"] = get_val(crime_tree, crime, "crime_risk")
    data["accident_risk"] = get_val(acc_tree, accidents, "accident_risk")
    data["traffic_risk"] = get_val(traffic_tree, traffic, "traffic_risk")
    data["crowd_score"] = get_val(crowd_tree, crowd, "crowd_score")
    data["weather_risk"] = weather_risk

print(" Saving graph.pkl...")
import networkx as nx

print("Connected components:", nx.number_connected_components(G))

# keep only largest connected component
largest_cc = max(nx.connected_components(G), key=len)
G = G.subgraph(largest_cc).copy()

print("Using largest connected component:", len(G.nodes()))
print("Total nodes:", G.number_of_nodes())
print("Total edges:", G.number_of_edges())

ccs = list(nx.connected_components(G))
print("Connected components:", len(ccs))
print("Largest CC size:", len(max(ccs, key=len)))

print(type(nodes.iloc[0]["osmid"]))
print(type(edges.iloc[0]["u"]))

import pickle

with open("graph.pkl", "wb") as f:
    pickle.dump(G, f)

print(" DONE — ULTRA FAST GRAPH READY")