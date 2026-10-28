from routing import compute_route, evaluate_route
import requests
import json

import os
from dotenv import load_dotenv

load_dotenv()  # loads .env into environment

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not set in environment")

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


def query_llm(prompt):
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=30
        )

        print("HF raw:", response.text[:200])

        if response.status_code != 200:
            print("HF status error:", response.status_code)
            return None

        result = response.json()

        if isinstance(result, dict) and "error" in result:
            print("HF API error:", result["error"])
            return None

        if isinstance(result, list):
            return result[0].get("generated_text", "")

        return None

    except Exception as e:
        print("HF error:", e)
        return None



def llm_decide_weights(context):

    prompt = f"""
    You are a safety AI.

    Time: {context['hour']}
    Weather: {context['weather']}

    Return ONLY JSON:
    {{
      "crime": 1,
      "accident": 1,
      "traffic": 1,
      "crowd": 1,
      "weather": 1
    }}
    """

    output = query_llm(prompt)

    import re

    try:
        if output:
            json_text = re.search(r"\{.*\}", output, re.DOTALL).group()
            return json.loads(json_text)

    except:
        pass

    print("⚠️ USING SAFE FALLBACK")

    weights = {
        "crime": 1,
        "accident": 1,
        "traffic": 1,
        "crowd": 1,
        "weather": 1
    }

    hour = context["hour"]

    if hour >= 20 or hour <= 5:
        weights["crime"] = 3
        weights["crowd"] = 0.5

    if context["weather"] in ["rain", "heavy_rain", "thunderstorm"]:
        weights["weather"] = 2
        weights["accident"] = 2

    return weights


def explain_route(weights, score):

    breakdown = score["breakdown"]

    sorted_risks = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)

    top_risks = [r[0] for r in sorted_risks[:2]]  # top 2 causes

    reasons = []

    if "crime" in top_risks:
        reasons.append("high-crime areas were avoided")

    if "traffic" in top_risks:
        reasons.append("traffic-heavy roads were minimized")

    if "crowd" in top_risks:
        reasons.append("crowded zones were reduced")

    if "accident" in top_risks:
        reasons.append("accident-prone routes were avoided")

    if weights["weather"] >= 2:
        reasons.append("weather conditions were considered")

    if not reasons:
        reasons.append("multiple safety factors were balanced")

    base = "This route was selected because " + ", ".join(reasons) + "."

    if score["total_risk"] < 30:
        base += " Overall, it is considered a safe route."
    elif score["total_risk"] < 60:
        base += " It offers moderate safety with some risk exposure."
    else:
        base += " While optimized, some risk factors still remain."

    prompt = f"""
Rewrite this in a natural and user-friendly way:

{base}

Make it 2 sentences max, and slightly more conversational.
"""

    output = query_llm(prompt)

    if output and len(output) > 20:
        return output.strip()

    return base

def run_agent(start, end, context, G):

    weights = llm_decide_weights(context)

    path = compute_route(start, end, weights, G)
    score = evaluate_route(path, G)

    if score["total_risk"] > 50:
        context["priority"] = "safest possible"
        weights = llm_decide_weights(context)
        path = compute_route(start, end, weights, G)
        score = evaluate_route(path, G)

    explanation = explain_route(weights, score)

    return {
        "path": path,
        "score": score,
        "weights": weights, 
        "explanation": explanation
    }