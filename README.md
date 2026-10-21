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

## Research Notebook

`research_analysis.ipynb` contains the full automated experiment and all visualizations.

### Running the Notebook

```bash
source .venv/bin/activate
pip install jupyter scipy
jupyter notebook research_analysis.ipynb
```

> Make sure to run the notebook from the project root (where `SABRA.kmz` lives) so that
> `build_campus_graph('SABRA.kmz')` resolves correctly.

### Notebook Structure

| Section | Description |
|---------|-------------|
| §0 — Imports | Dependencies and global colour palette |
| §1 — Load Graph | Builds the campus graph from `SABRA.kmz` |
| §2 — Helpers | `haversine()`, `astar_heuristic()`, `path_distance()` |
| §3 — `automated_testing()` | Core experiment function (100 pairs × 3 algorithms) |
| §4 — Run Experiment | Executes and displays raw results + summary stats |
| §5 — RQ1 Accuracy | Bar chart + scatter plot comparing physical distances |
| §6 — RQ2 Speed | Box plot + violin comparing execution times; Welch's t-test |
| §7 — RQ3 Behaviour | Spatial path overlay on the campus graph |
| §8 — Scaling Behaviour | Execution time vs route distance regression per algorithm |
| §9 — Per-Route Timeline | Dijkstra vs A\* head-to-head across all 100 routes |
| §10 — BFS Overhead | Ranked bar + histogram of extra metres BFS adds |
| §11 — Node Count | KDE + box plot of path node counts |
| §12 — Summary Dashboard | Publication-ready 2×2 composite figure |
| §13 — Export | Saves CSV + prints final results table |
| §14 — Conclusions | Findings for each RQ |

### Output Files

After running the notebook, the following files are generated in the project root:

| File | Chart Type | Research Question |
|------|-----------|-------------------|
| `rq1_accuracy.png` | Bar chart + scatter | RQ1 — Physical distance comparison |
| `rq2_speed.png` | Box plot + violin | RQ2 — Execution time distribution |
| `rq3_behaviour.png` | Spatial graph overlay | RQ3 — Routing path behaviour |
| `scaling_behaviour.png` | Scatter + regression | How time scales with route length |
| `per_route_timeline.png` | Line chart + delta bars | A\* vs Dijkstra speed per route |
| `bfs_overhead.png` | Bar + histogram | BFS extra distance over optimal |
| `node_count_dist.png` | KDE + box plot | Node count distribution per algorithm |
| `summary_dashboard.png` | 2×2 composite | Publication-ready summary figure |
| `experiment_results.csv` | Raw data (300 rows) | All metrics for all routes |

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
├── SABRA.kmz                  # Campus walkway data (Google My Maps export)
├── build_graph.py             # KMZ parser → NetworkX graph builder (5 m densification)
├── server.py                  # FastAPI backend — /route endpoint for all three algorithms
├── index.html                 # Leaflet.js frontend — map UI, algorithm selector, results panel
├── research_analysis.ipynb    # Jupyter experiment notebook (automated testing + 8 visualizations)
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

**Generated by the notebook (not committed):**
```
├── rq1_accuracy.png           # RQ1 — physical distance comparison
├── rq2_speed.png              # RQ2 — execution time distribution
├── rq3_behaviour.png          # RQ3 — spatial path overlay
├── scaling_behaviour.png      # Time vs route distance regression
├── per_route_timeline.png     # Per-route Dijkstra vs A* timeline
├── bfs_overhead.png           # BFS overhead analysis
├── node_count_dist.png        # Node count distribution
├── summary_dashboard.png      # Publication-ready 2×2 dashboard
└── experiment_results.csv     # Raw metrics (300 rows)
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
