import os
import networkx as nx
from build_graph import build_campus_graph

# Safely locate your KMZ file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KMZ_PATH = os.path.join(BASE_DIR, 'SABRA.kmz-2')

print("Loading graph data...")
campus_graph = build_campus_graph(KMZ_PATH)

# Calculate the connected components (islands)
islands = list(nx.connected_components(campus_graph))
num_islands = len(islands)

print(f"\n--- MAP DIAGNOSTICS ---")
print(f"Total Nodes: {campus_graph.number_of_nodes()}")
print(f"Total Edges: {campus_graph.number_of_edges()}")
print(f"Total Islands: {num_islands}\n")

if num_islands == 1:
    print("✅ SUCCESS: Your entire map is perfectly connected! No broken paths.")
else:
    print("⚠️ WARNING: Your map is broken into disconnected pieces.\n")
    
    # Sort islands by size (largest first, which is usually the "main" map)
    islands.sort(key=len, reverse=True)
    
    for i, island in enumerate(islands):
        nodes_in_island = len(island)
        # Grab a random coordinate from this island to help locate it
        sample_node = list(island)[0] 
        
        print(f"Island {i + 1} ({nodes_in_island} nodes):")
        if i == 0:
            print(f"  -> This is your main map network.")
        else:
            print(f"  -> 🔍 BROKEN PIECE: Paste {sample_node[0]:.6f}, {sample_node[1]:.6f} into Google Maps to find this disconnected path.")