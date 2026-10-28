from flask import Flask, request, jsonify, render_template
from agent import run_agent
import networkx as nx
import pandas as pd


app = Flask(__name__)

import pickle

with open("graph.pkl", "rb") as f:
    G = pickle.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/route", methods=["POST"])
def route():

    data = request.json

    start = data["start"]
    end = data["end"]

    context = {
        "hour": int(data.get("hour", 18)),
        "weather": data.get("weather", "clear")
    }

    result = run_agent(start, end, context, G)

    # convert node path → lat lon
    path_coords = [(G.nodes[n]["y"], float(G.nodes[n]["x"])) for n in result["path"]]

    score = {
        "total_risk": float(result["score"]["total_risk"]),
        "total_length": float(result["score"]["total_length"])
    }

    return jsonify({
        "path_coords": path_coords,
        "explanation": result["explanation"],
        "score": score
    })

if __name__ == "__main__":
    app.run(debug=True)