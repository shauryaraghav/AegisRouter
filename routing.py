import networkx as nx
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree


def build_node_tree(G):
    rows = []

    for n, data in G.nodes(data=True):
        if "x" in data and "y" in data:
            rows.append((n, float(data["y"]), float(data["x"])))

    nodes = pd.DataFrame(rows, columns=["osmid", "lat", "lon"])

    coords = np.vstack((nodes["lat"], nodes["lon"])).T
    tree = cKDTree(coords)

    return nodes, tree



def nearest_node(lat, lon, nodes, tree):
    _, idx = tree.query([lat, lon])
    return nodes.iloc[idx]["osmid"]



def apply_weights(G, weights, weather_risk):

    if weights is None:
        print("weights None → using default")
        weights = {
            "crime": 1,
            "accident": 1,
            "traffic": 1,
            "crowd": 1,
            "weather": 1
        }

    for _, _, data in G.edges(data=True):

        crime = data.get("crime_risk", 0) / 5
        accident = data.get("accident_risk", 0) / 5
        traffic = data.get("traffic_risk", 0) / 100
        crowd = data.get("crowd_score", 0) / 5
        weather = weather_risk / 5

        risk = (
            weights["crime"] * crime +
            weights["accident"] * accident +
            weights["traffic"] * traffic +
            weights["crowd"] * crowd +
            weights["weather"] * weather
        )

        risk = min(risk, 5)
        data["weight"] = data["length"] * (1 + risk)


def compute_route(start, end, weights, G, weather_risk=1):

    nodes, tree = build_node_tree(G)

    apply_weights(G, weights, weather_risk)

    start_node = nearest_node(start[0], start[1], nodes, tree)
    end_node = nearest_node(end[0], end[1], nodes, tree)

    path = nx.shortest_path(G, start_node, end_node, weight="weight")

    return path


def evaluate_route(path, G):

    total_length = 0
    crime_vals = []
    traffic_vals = []
    crowd_vals = []
    accident_vals = []

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        edge = G[u][v]

        # MULTI-EDGE GRAPH
        if isinstance(edge, dict) and any(isinstance(v, dict) for v in edge.values()):
            edge_data = min(
                edge.values(),
                key=lambda d: d.get("weight", d.get("length", 1))
            )
        else:
            # SINGLE EDGE GRAPH
            edge_data = edge

        total_length += edge_data.get("length", 0)

        crime_vals.append(edge_data.get("crime_risk", 0) / 5)
        accident_vals.append(edge_data.get("accident_risk", 0) / 5)
        traffic_vals.append(edge_data.get("traffic_risk", 0) / 100)
        crowd_vals.append(edge_data.get("crowd_score", 0) / 5)

    crime_mean = float(np.mean(crime_vals)) if crime_vals else 0.0
    accident_mean = float(np.mean(accident_vals)) if accident_vals else 0.0
    traffic_mean = float(np.mean(traffic_vals)) if traffic_vals else 0.0
    crowd_mean = float(np.mean(crowd_vals)) if crowd_vals else 0.0

    return {
        "total_risk": round(
            (crime_mean + accident_mean + traffic_mean + crowd_mean) / 4 * 100, 2
        ),
        "total_length": round(total_length, 2),
        "breakdown": {
            "crime": crime_mean,
            "accident": accident_mean,
            "traffic": traffic_mean,
            "crowd": crowd_mean
        }
    }