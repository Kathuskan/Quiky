from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse 
import networkx as nx
from build_graph import build_campus_graph, find_nearest_node

app = FastAPI()

# Serve the index.html file when visiting the root URL
@app.get("/")
def serve_homepage():
    return FileResponse("index.html")

# Allow the frontend web page to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the graph into memory once when the server starts
campus_graph = build_campus_graph('SABRA.kmz')
print("Server ready! Graph loaded.")

@app.get("/route")
def get_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    # 1. Snap coordinates to the nearest nodes on your graph
    start_node = find_nearest_node(campus_graph, start_lat, start_lon)
    end_node = find_nearest_node(campus_graph, end_lat, end_lon)

    try:
        # 2. Calculate shortest path
        shortest_path = nx.shortest_path(campus_graph, source=start_node, target=end_node, weight='weight')
        distance = nx.shortest_path_length(campus_graph, source=start_node, target=end_node, weight='weight')
        
        # 3. Return as JSON for the web app
        return {
            "status": "success",
            "distance": round(distance, 2),
            "path": [{"lat": lat, "lng": lon} for lat, lon in shortest_path]
        }
    except nx.NetworkXNoPath:
        return {"status": "error", "message": "No path found."}