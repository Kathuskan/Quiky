# Campus Navigator — Pathfinding Algorithm Comparator

A research project empirically comparing **Dijkstra**, **A\*** and **BFS** pathfinding algorithms on a real-world spatial graph of **Sabaragamuwa University (SABRA)** campus.

---

## Research Objective

To measure and compare the **performance**, **accuracy**, and **pathing behaviour** of three routing algorithms using a custom-built campus graph derived from real GPS walkway data.

---

## System Architecture

```
SABRA.kmz  →  build_graph.py  →  NetworkX Graph
                                       ↓
                              server.py (FastAPI)
                                       ↓
                              index.html (Leaflet.js)
```

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Map Data   | KMZ (Google My Maps digitized walkways)         |
| Parsing    | BeautifulSoup (XML/KML)                         |
| Graph      | NetworkX (weighted, densified every 5 m)        |
| Backend    | Python · FastAPI · Uvicorn                      |
| Frontend   | Vanilla JS · Leaflet.js                         |
| Map Tiles  | Google Maps Satellite Hybrid                    |

---

## Algorithms Under Test

### Dijkstra's Algorithm — *The Baseline*
- Uses real Haversine edge weights (metres)
- Guarantees the **globally shortest physical route**
- **Hypothesis:** Most accurate path; highest execution time due to omnidirectional expansion

### A\* Search — *The Optimised Challenger*
- Same weighted edges as Dijkstra **+** a Haversine straight-line heuristic to the destination
- Prioritises nodes closer to the goal, pruning unnecessary exploration
- **Hypothesis:** Finds the **identical shortest path** as Dijkstra with significantly lower execution time

### Breadth-First Search — *The Unweighted Control*
- Ignores all edge weights; counts only **node hops**
- **Hypothesis:** Produces physically longer routes due to the 5 m densification — every slight directional bend adds extra hops — exposing the failure of unweighted algorithms in geospatial routing

---

## Evaluation Metrics

Every `/route` API response includes:

| Metric                 | Field                  | How Measured                        |
|------------------------|------------------------|-------------------------------------|
| Execution time         | `execution_time_ms`    | `time.perf_counter()` (Python)      |
| Path distance          | `distance`             | Cumulative Haversine edge weights   |
| Visual behaviour       | `path` coordinate list | Rendered as a polyline in Leaflet   |

---

## Project Status

| Phase | Description                                              | Status |
|-------|----------------------------------------------------------|--------|
| 1     | Digitise campus paths (KMZ) and extract coordinates      | ✅ Done |
| 2     | Build and densify the NetworkX graph                     | ✅ Done |
| 3     | Develop FastAPI routing engine and Leaflet UI            | ✅ Done |
| 4     | Integrate Dijkstra, A\*, and BFS with performance timing | ✅ Done |
| 5     | Frontend algorithm selector + execution time display     | 🔲 In progress |
| 6     | Structured test runs (short / medium / complex routes)   | 🔲 Pending |

---

## Getting Started

### Prerequisites
- Python 3.9+
- A modern web browser

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Shortcut

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
uvicorn server:app --reload
```

Then open your browser at **http://127.0.0.1:8000**.

### Using the App

1. **Click** anywhere on the campus map to place a **start point (A)**
2. **Click** a second location to place an **end point (B)**
3. Select an algorithm from the **dropdown** (Dijkstra / A\* / BFS)
4. The shortest path is drawn on the map and the **execution time + distance** are displayed in the panel
5. Click **Clear route** to start over

---

## Project Structure

```
Shortcut/
├── SABRA.kmz          # Campus walkway data (Google My Maps export)
├── build_graph.py     # KMZ parser → NetworkX graph builder (with 5 m densification)
├── server.py          # FastAPI backend — /route endpoint for all three algorithms
├── index.html         # Leaflet.js frontend — map UI, algorithm selector, results panel
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

---

## Graph Details

- **Source data:** Walkways manually digitised in Google My Maps and exported as KMZ
- **Node density:** One graph node every **5 metres** along each walkway segment (interpolated)
- **Edge weight:** Haversine great-circle distance in metres between adjacent nodes
- **Graph type:** Undirected, weighted (`networkx.Graph`)

---

## Key Design Decisions

- **Graph loaded once at startup** — the NetworkX graph is built from the KMZ a single time when the FastAPI server starts, keeping per-request latency low.
- **Nearest-node snapping** — user tap coordinates are snapped to the closest graph node before pathfinding, ensuring clicks off the walkway still produce valid routes.
- **5 m densification** — breaks long straight edges into short segments so the BFS experiment behaves meaningfully and polylines render smoothly.

---

## Research Notes

> This project is part of an undergraduate research experiment. All timing measurements are taken with `time.perf_counter()` for sub-millisecond precision. Tests are repeated across three route categories (short ≈ < 100 m, medium ≈ 100–400 m, complex ≈ > 400 m with multiple intersections) to produce statistically meaningful comparisons.
