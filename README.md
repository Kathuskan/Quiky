# Campus Navigator — Pathfinding Algorithm Comparator

> An undergraduate research project empirically comparing **Dijkstra**, **A\*** and **BFS** pathfinding algorithms on a real-world spatial graph of **Sabaragamuwa University of Sri Lanka (SABRA)** campus.

---

## Table of Contents

1. [Research Objective](#research-objective)
2. [System Architecture](#system-architecture)
3. [How It Works](#how-it-works)
4. [Algorithms Under Test](#algorithms-under-test)
5. [Evaluation Metrics](#evaluation-metrics)
6. [Research Hypotheses](#research-hypotheses)
7. [Project Structure](#project-structure)
8. [Getting Started](#getting-started)
9. [API Reference](#api-reference)
10. [Research Notebook](#research-notebook)
11. [Visualizations](#visualizations)
12. [Project Status](#project-status)

---

## Research Objective

To empirically measure and compare the **performance**, **accuracy**, and **pathing behaviour** of three classic graph traversal algorithms applied to a custom-built, densified real-world campus walkway graph — and to prove that algorithm choice has a direct, measurable impact on route quality and computation time.

**Research Questions:**

| # | Question |
|---|----------|
| RQ1 | Does algorithm choice affect the **physical accuracy** of the computed route? |
| RQ2 | Does A\*'s directional heuristic offer a measurable **speed advantage** over Dijkstra? |
| RQ3 | Do different algorithms produce visually **distinct routing behaviour** on a densified spatial graph? |

---

## System Architecture

```
SABRA.kmz (Google My Maps)
      │
      ▼
build_graph.py
 ├── parse KML walkway LineStrings
 ├── densify edges → 1 node every 5 m
 ├── compute Haversine edge weights (metres)
 └── return NetworkX Graph
      │
      ▼
server.py  (FastAPI)
 ├── GET /             → serves index.html
 ├── GET /locations    → building names & coordinates
 ├── GET /route        → runs chosen algorithm, returns path + metrics
 └── GET /graph-data   → all graph edges for the blue overlay
      │
      ▼
index.html  (Leaflet.js)
 ├── Google Satellite Hybrid tile layer
 ├── Blue graph overlay (all walkways)
 ├── Algorithm dropdown selector
 ├── Click-to-place A/B pins
 └── Results panel (distance, walk time, exec time)
```

| Layer | Technology |
|-------|-----------|
| Map Data | KMZ — Google My Maps digitised walkways |
| KML Parsing | `BeautifulSoup` + `lxml` |
| Graph Engine | `NetworkX` (undirected, weighted) |
| Backend | `FastAPI` + `Uvicorn` |
| Frontend | Vanilla JS + `Leaflet.js 1.9.4` |
| Map Tiles | Google Maps Satellite Hybrid (`mt1.google.com`) |
| Research | `Jupyter` + `Pandas` + `Matplotlib` + `Seaborn` + `SciPy` |

---

## How It Works

### 1. Map Digitisation
Campus walkways were manually traced in **Google My Maps** and exported as a `.kmz` file. Each traced path becomes a `LineString` in the embedded KML.

### 2. Graph Construction (`build_graph.py`)
```
KML LineStrings
    → extract (lon, lat) coordinate pairs
    → for each segment, compute Haversine distance
    → interpolate: insert a new node every 5 metres
    → add NetworkX edge with weight = Haversine distance (metres)
```
The **5-metre densification** is critical to the experiment:
- It makes the drawn polyline visually smooth on the map
- It gives BFS enough intermediate nodes to behave distinctly from weighted algorithms
- It ensures user tap coordinates snap accurately to the nearest walkway node

### 3. Routing (`server.py`)
When the frontend calls `/route`:
1. The clicked (lat, lon) is **snapped** to the nearest graph node via a linear scan
2. The selected algorithm is run and timed with `time.perf_counter()`
3. The response includes the path coordinates, total distance, and execution time

### 4. Frontend Interaction (`index.html`)
- Click once → place **Start pin (A)**
- Click again → place **End pin (B)**, route calculated automatically
- The blue overlay shows every walkway edge in the graph
- Results panel shows **Distance (m)**, **Est. walk time**, and **Exec. time (ms)**
- Click **Clear Map** to reset

---

## Algorithms Under Test

### 🟢 Dijkstra's Algorithm — *The Baseline*

Uses the real Haversine edge weights to explore the graph layer by layer, expanding in all directions from the source until it reaches the destination.

```python
nx.dijkstra_path(graph, source=start_node, target=end_node, weight='weight')
```

- **Optimises for:** Minimum total physical distance (metres)
- **Search pattern:** Omnidirectional wavefront
- **Guarantees:** Globally optimal shortest path

---

### 🟩 A\* Search — *The Optimised Challenger*

Extends Dijkstra by adding a **Haversine straight-line heuristic** to the destination. At each step, nodes closer to the goal are prioritised, pruning unnecessary branches.

```python
nx.astar_path(graph, source=start_node, target=end_node,
              heuristic=astar_heuristic, weight='weight')

def astar_heuristic(node1, node2):
    return get_distance(node1[0], node1[1], node2[0], node2[1])
```

- **Optimises for:** Minimum total physical distance (metres) — identical result to Dijkstra
- **Search pattern:** Directed towards the goal
- **Why the heuristic is admissible:** The straight-line Haversine distance never overestimates the true path cost on a real map, so A\* is guaranteed to find the same optimal solution as Dijkstra while expanding fewer nodes

---

### 🟠 Breadth-First Search — *The Unweighted Control*

Ignores all edge weights and treats every edge as having equal cost. It expands one hop at a time, finding the path with the **fewest node crossings**.

```python
nx.shortest_path(graph, source=start_node, target=end_node, weight=None)
```

- **Optimises for:** Minimum number of nodes (hops)
- **Search pattern:** Layer-by-layer, ignoring distance
- **Known failure mode on densified graphs:** Because the graph has a node every 5 m, any directional bend in a walkway adds extra hops. BFS avoids these bends, producing paths that are physically longer in metres while crossing fewer nodes — demonstrating its unsuitability for geospatial routing

---

## Evaluation Metrics

Every `/route` API response returns a JSON payload with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"success"` or `"error"` |
| `algorithm_used` | string | `"dijkstra"`, `"astar"`, or `"bfs"` |
| `execution_time_ms` | float | Wall-clock time measured with `time.perf_counter()`, in milliseconds (4 decimal places) |
| `distance` | float | Total physical length of the returned path in metres (sum of Haversine edge weights) |
| `path` | array | Ordered list of `{lat, lng}` coordinates forming the route polyline |

### Example Response
```json
{
  "status": "success",
  "algorithm_used": "astar",
  "execution_time_ms": 3.8471,
  "distance": 247.63,
  "path": [
    {"lat": 6.7134, "lng": 80.7892},
    {"lat": 6.7136, "lng": 80.7894},
    "..."
  ]
}
```

### Notebook Metrics (automated experiment)

The research notebook records these additional metrics per route:

| Metric | Column | How Collected |
|--------|--------|--------------|
| Route identifier | `route_id` | Integer 0–99 |
| Algorithm name | `algorithm` | `Dijkstra` / `A*` / `BFS` |
| Execution time | `execution_time_ms` | `time.perf_counter()` (nanosecond resolution) |
| Physical distance | `distance` | Sum of Haversine edge weights along the returned path |
| Path length | `node_count` | `len(path)` — number of nodes in the result |

---

## Research Hypotheses

| Hypothesis | Expected Outcome |
|------------|-----------------|
| **H1 — Accuracy** | Dijkstra and A\* will produce **identical** physical distances on every route. BFS will produce routes measurably **longer in metres**. |
| **H2 — Speed** | A\* will have **lower mean and median execution times** than Dijkstra, because the heuristic prunes directionally irrelevant nodes. |
| **H3 — Behaviour** | On the spatial graph overlay, Dijkstra and A\* will follow the same direct corridor. BFS will zig-zag along the densified 5 m grid. |

---

## Project Structure

```
Shortcut/
├── SABRA.kmz                  # Campus walkway data — original KMZ export
├── SABRA.kmz-2                # Updated KMZ with building marker pins
├── build_graph.py             # KMZ parser, graph builder, node densifier, marker extractor
├── server.py                  # FastAPI server — /route, /locations, /graph-data endpoints
├── index.html                 # Leaflet.js web UI — map, algorithm selector, results panel
├── research_analysis.ipynb    # Jupyter research notebook — 100-pair automated experiment
├── requirements.txt           # All Python dependencies (pinned versions)
├── .gitignore                 # Excludes .venv, __pycache__, .DS_Store, results/
└── README.md                  # This file
```


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

# 3. Install all dependencies
pip install -r requirements.txt
```

### Running the Web App

```bash
uvicorn server:app --reload
```

Then open **http://127.0.0.1:8000** in your browser.

### Running the Research Notebook

```bash
jupyter notebook research_analysis.ipynb
# or
jupyter lab research_analysis.ipynb
```

Run all cells top-to-bottom. Outputs are saved to the project root.

---

## API Reference

### `GET /`
Serves `index.html`.

---

### `GET /locations`
Returns all named building markers extracted from the KMZ file.

**Response:**
```json
{
  "status": "success",
  "locations": [
    {"name": "Faculty of Applied Sciences", "lat": 6.714, "lng": 80.790},
    "..."
  ]
}
```

---

### `GET /route`

Calculates the shortest path between two coordinates using the selected algorithm.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_lat` | float | ✅ | Start latitude |
| `start_lon` | float | ✅ | Start longitude |
| `end_lat` | float | ✅ | End latitude |
| `end_lon` | float | ✅ | End longitude |
| `algo` | string | ❌ | `dijkstra` (default) · `astar` · `bfs` |

**Example:**
```
GET /route?start_lat=6.713&start_lon=80.789&end_lat=6.715&end_lon=80.791&algo=astar
```

---

### `GET /graph-data`
Returns all graph edges as coordinate pairs — used by the frontend to draw the blue walkway overlay.

**Response:**
```json
{
  "status": "success",
  "edges": [
    [[6.7130, 80.7890], [6.7131, 80.7891]],
    "..."
  ]
}
```

---

## Research Notebook

[`research_analysis.ipynb`](./research_analysis.ipynb) contains the full automated experiment.

### Notebook Sections

| Section | Description |
|---------|-------------|
| §0 — Imports | All dependencies + global colour palette |
| §1 — Load Graph | Builds campus graph from `SABRA.kmz-2` |
| §2 — Helpers | `haversine()`, `astar_heuristic()`, `path_distance()` |
| §3 — `automated_testing()` | Core function: 100 random pairs × 3 algorithms |
| §4 — Run Experiment | Executes the test, prints progress + summary stats |
| §5 — RQ1 Accuracy | Bar chart + Dijkstra vs BFS scatter plot |
| §6 — RQ2 Speed | Box plot + violin + Welch's t-test |
| §7 — RQ3 Behaviour | Spatial path overlay on full campus graph |
| §8 — Scaling Behaviour | Execution time vs distance regression per algorithm |
| §9 — Per-Route Timeline | Dijkstra vs A\* head-to-head across all 100 routes |
| §10 — BFS Overhead | Ranked bar + histogram of extra metres BFS adds |
| §11 — Node Count | KDE + box plot of path node counts |
| §12 — Summary Dashboard | 2×2 publication-ready composite figure |
| §13 — Export | Saves CSV + prints final results table |
| §14 — Conclusions | Findings per RQ |


## Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Digitise campus walkways (KMZ) | ✅ Complete |
| 2 | Build & densify the NetworkX graph | ✅ Complete |
| 3 | FastAPI routing backend | ✅ Complete |
| 4 | Three-algorithm support (Dijkstra / A\* / BFS) with timing | ✅ Complete |
| 5 | Frontend algorithm selector + exec-time display panel | ✅ Complete |
| 5b | Building markers + `/locations` endpoint | ✅ Complete |
| 5c | Graph edge overlay on the live map | ✅ Complete |
| 6 | Automated 100-pair research notebook | ✅ Complete |
| 7 | Structured test runs & write-up | 🔲 In progress |

---

## Graph Technical Details

| Property | Value |
|----------|-------|
| Graph type | Undirected, weighted (`networkx.Graph`) |
| Node density | 1 node per 5 metres along each walkway |
| Edge weight | Haversine great-circle distance (metres) |
| Source data | Google My Maps — manually traced campus paths |
| Coordinate format | (latitude, longitude) tuples as node identifiers |
| Snapping method | Linear nearest-node scan (`find_nearest_node`) |

---

## Key Design Decisions

- **Graph built once at startup** — `campus_graph` is constructed from the KMZ a single time when the server starts, keeping per-request latency low.
- **5 m node densification** — Long straight edges are split into 5 m segments. This is what makes BFS behave distinctly (more hops per metre of deviation) and makes route polylines render smoothly on the map.
- **Haversine as both weight and heuristic** — Using the same distance function for edge weights and the A\* heuristic guarantees the heuristic is admissible (never overestimates), so A\* is provably optimal.
- **Isolated timing** — Each algorithm is timed independently using `time.perf_counter()` to prevent cache effects or cross-contamination between algorithm calls in the notebook.

---

## Dependencies

| Package | Version | Role |
|---------|---------|------|
| `fastapi` | 0.115.0 | Web framework |
| `uvicorn[standard]` | 0.30.6 | ASGI server |
| `networkx` | 3.3 | Graph construction & pathfinding |
| `beautifulsoup4` | 4.12.3 | KML/XML parsing |
| `lxml` | 5.2.2 | XML parser backend |
| `httpx` | 0.27.0 | HTTP client |
| `numpy` | 2.0.2 | Numerical arrays |
| `pandas` | 2.3.3 | DataFrame / CSV export |
| `matplotlib` | 3.9.4 | Plotting |
| `seaborn` | 0.13.2 | Statistical visualizations |
| `scipy` | 1.13.1 | Regression & Welch's t-test |
| `jupyter` | 1.1.1 | Notebook runtime |
| `jupyterlab` | 4.5.11 | Notebook UI |

---

*Undergraduate research experiment — Sabaragamuwa University of Sri Lanka.*  
*All timing results use `time.perf_counter()` (nanosecond resolution). Experiment seed fixed at 42 for reproducibility.*
