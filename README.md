
# AegisRouter
### Agentic AI for Safer, Smarter Navigation

> **Not just the shortest route — the smartest and safest one.**

---

##  Overview

**AegisRouter AI** is an agent-driven routing system that computes the **safest path between two locations**, not merely the fastest.  
It integrates **crime statistics, traffic density, accident hotspots, crowd intensity, and weather conditions** to recommend routes that minimize real-world risk.

Unlike traditional navigation systems that optimize only distance or time, AegisRouter AI prioritizes **human safety**, especially in unfamiliar, high-risk, or night-time travel scenarios.

---

##  Why AegisRouter AI?

Most navigation apps ask:  
> *“How fast can you get there?”*

AegisRouter AI asks:  
> *“How safely can you get there?”*

This project demonstrates how **agentic AI systems** can make context-aware, explainable decisions in safety-critical environments.

---

##  Key Highlights

-  **Agentic AI Decision Pipeline**  
  The system *thinks → decides → acts → evaluates → explains* rather than following static rules.

-  **Graph-Based Risk-Aware Routing**  
  Road networks are modeled as graphs with dynamically weighted edges representing safety risk.

-  **LLM-Assisted Reasoning (with Fallback)**  
  Generates human-readable explanations for route choices while remaining functional without LLM access.

-  **Interactive, Real-Time Routing**  
  Users select start and end points directly on a map and receive instant safe-route recommendations.

-  **Multi-Factor Risk Modeling**  
  Combines multiple spatial datasets into a unified, interpretable safety score.

---

##  System Architecture

```

User Input (Map Clicks + Context)
↓
Agent Brain (LLM / Logic Layer)
↓
Dynamic Weight Decision
(Crime / Traffic / Weather / Crowd)
↓
Graph Engine (NetworkX)
↓
Safest Route Computation
↓
Risk Evaluation
↓
Human-Friendly Explanation

```

---

##  Tech Stack

| Layer        | Technology |
|-------------|------------|
| Backend     | Flask |
| Frontend    | HTML, CSS, JavaScript |
| Mapping     | Leaflet.js |
| Graph Engine| NetworkX |
| Data        | Pandas, NumPy |
| Spatial Ops | KD-Tree (SciPy) |
| AI Layer    | HuggingFace (FLAN-T5) + Rule-Based Fallback |

---

##  Datasets

The system integrates multiple **public, anonymized datasets**, spatially mapped onto road networks:

- Crime reports (geo-tagged)
- Traffic density data
- Accident records
- Crowd intensity / POIs
- Weather conditions

>  All datasets are used **strictly for demonstration and research purposes**.

---

##  How It Works

### Spatial Data Mapping
All datasets are mapped to road network edges using **KD-Tree nearest-neighbor search**.

---

### Risk Modeling

Each road segment is assigned a normalized risk score:

```

Risk = w₁·crime + w₂·traffic + w₃·accidents + w₄·crowd + w₅·weather

```

All features are normalized to a common scale before aggregation.

---

### Agentic Weight Decision

The agent dynamically adjusts weights based on context:

-  Night-time → higher crime weight  
-  Rain → higher accident & weather weight  
-  Congestion → higher traffic weight  

---

###  Route Computation

Routing uses a modified shortest-path formulation:

```

Adjusted Weight = distance × (1 + risk)

````

This biases the algorithm toward safer roads, not just shorter ones.

---

### Explainability

The system generates **human-readable explanations** describing:
- Why a route was chosen
- Which risks were avoided
- What trade-offs were made

---

## Features

-  Click-to-select start and end points
-  Time-based risk adjustment
-  Weather-aware routing
-  AI-generated safety explanations
-  Relative risk scoring
-  Clean, responsive UI with live route rendering

---

## Demo

### Run Locally

```bash
pip install -r requirements.txt
python app.py
````

Open in browser:

```
http://127.0.0.1:5000
```

---

### Public Demo (Ngrok)

```bash
pip install pyngrok
```

Add to `app.py`:

```python
from pyngrok import ngrok

public_url = ngrok.connect(5000)
print(public_url)
```

Run:

```bash
python app.py
```

---

##  Project Structure

```
AegisRouterAI/
│
├── data/                # Preprocessed datasets (not tracked in production)
├── raw/                 # Raw public datasets
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── agent.py             # Agentic decision logic
├── routing.py           # Risk-aware routing engine
├── build_graph.py       # Graph construction
├── app.py               # Flask application
└── requirements.txt
```

---

##  Agent Flow

```text
THINK   → Analyze context
DECIDE  → Assign risk weights
ACT     → Compute safest route
EVALUATE→ Assess overall risk
REFINE  → Retry if threshold exceeded
EXPLAIN → Generate reasoning
```

---

##  Limitations

* Relies on dataset quality and coverage
* LLM responses may fallback to deterministic logic
* Risk scores are **comparative**, not absolute safety guarantees

---

##  Future Enhancements

*  Live traffic & weather APIs
*  Risk heatmap visualization
*  Mobile-optimized UI
*  Stronger or on-device LLMs
*  Voice-based navigation assistant

---

##  Potential Use Cases

* Personal safety navigation
* Night-time travel planning
* Smart city infrastructure analysis
* Emergency response routing

---

##  Author

**Shreya Raghav**

---

## Inspiration

> Navigation apps optimize for time.
> **AegisRouter AI optimizes for life.**

---

 If you found this project interesting, consider giving it a star!

 NOTE: Source datasets are git-ignored and restricted for privacy reasons.

```
