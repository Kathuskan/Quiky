import time
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse 
import networkx as nx

# Added extract_markers here
from build_graph import build_campus_graph, find_nearest_node, get_distance, extract_markers 

app = FastAPI()

@app.get("/")
def serve_homepage():
    return FileResponse("index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KMZ_PATH = os.path.join(BASE_DIR, 'SABRA.kmz-2') 

campus_graph = build_campus_graph(KMZ_PATH)
print(f"Server ready! Graph loaded from: {KMZ_PATH}")

# Extract the markers for the UI labels and dropdowns
campus_locations = extract_markers(KMZ_PATH)
print(f"Extracted {len(campus_locations)} building markers.")

def astar_heuristic(node1, node2):
    return get_distance(node1[0], node1[1], node2[0], node2[1])

# Endpoint to serve building names and coordinates to the frontend
@app.get("/locations")
def get_locations():
    return {"status": "success", "locations": campus_locations}

@app.get("/route")
def get_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float, algo: str = "dijkstra"):
    start_node = find_nearest_node(campus_graph, start_lat, start_lon)
    end_node = find_nearest_node(campus_graph, end_lat, end_lon)

    start_time = time.perf_counter()

    try:
        if algo == "dijkstra":
            shortest_path = nx.dijkstra_path(campus_graph, source=start_node, target=end_node, weight='weight')
        elif algo == "astar":
            shortest_path = nx.astar_path(campus_graph, source=start_node, target=end_node, heuristic=astar_heuristic, weight='weight')
        elif algo == "bfs":
            shortest_path = nx.shortest_path(campus_graph, source=start_node, target=end_node, weight=None)
        else:
            return {"status": "error", "message": "Unknown algorithm."}

        calc_time_ms = (time.perf_counter() - start_time) * 1000

        total_distance = 0
        for i in range(len(shortest_path) - 1):
            total_distance += campus_graph[shortest_path[i]][shortest_path[i+1]].get('weight', 0)
        
        return {
            "status": "success",
            "algorithm_used": algo,
            "execution_time_ms": round(calc_time_ms, 4),
            "distance": round(total_distance, 2),
            "path": [{"lat": lat, "lng": lon} for lat, lon in shortest_path]
        }
    except nx.NetworkXNoPath:
        return {"status": "error", "message": "No path found."}

# Endpoint to serve the raw paths for the blue overlay
@app.get("/graph-data")
def get_graph_data():
    edges = []
    for u, v in campus_graph.edges():
        edges.append([[u[0], u[1]], [v[0], v[1]]])
    return {"status": "success", "edges": edges}