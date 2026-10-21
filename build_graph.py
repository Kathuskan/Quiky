import zipfile
import math
import networkx as nx
from bs4 import BeautifulSoup

def get_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def interpolate_segment(lat1, lon1, lat2, lon2, dist, interval=5):
    # Breaks a long line into smaller segments every `interval` meters
    num_points = int(dist // interval)
    if num_points <= 1:
        return [(lat1, lon1), (lat2, lon2)]
    
    points = []
    for i in range(num_points + 1):
        fraction = i / num_points
        inter_lat = lat1 + (lat2 - lat1) * fraction
        inter_lon = lon1 + (lon2 - lon1) * fraction
        points.append((inter_lat, inter_lon))
    return points

def build_campus_graph(kmz_path):
    G = nx.Graph()
    with zipfile.ZipFile(kmz_path, 'r') as kmz:
        kml_file = [f for f in kmz.namelist() if f.endswith('.kml')][0]
        with kmz.open(kml_file, 'r') as f:
            soup = BeautifulSoup(f, 'xml')
            
    for line in soup.find_all('LineString'):
        coords_text = line.coordinates.text.strip()
        points = [tuple(map(float, p.split(',')[:2])) for p in coords_text.split()]
        
        for i in range(len(points)-1):
            lon1, lat1 = points[i]
            lon2, lat2 = points[i+1]
            total_dist = get_distance(lat1, lon1, lat2, lon2)
            
            # Densify the line: create a new node every 5 meters
            dense_points = interpolate_segment(lat1, lon1, lat2, lon2, total_dist, interval=5)
            
            for j in range(len(dense_points)-1):
                p1_lat, p1_lon = dense_points[j]
                p2_lat, p2_lon = dense_points[j+1]
                segment_dist = get_distance(p1_lat, p1_lon, p2_lat, p2_lon)
                G.add_edge((p1_lat, p1_lon), (p2_lat, p2_lon), weight=segment_dist)
    return G

def find_nearest_node(graph, target_lat, target_lon):
    nearest_node = None
    min_dist = float('inf')
    for node in graph.nodes():
        n_lat, n_lon = node
        dist = get_distance(target_lat, target_lon, n_lat, n_lon)
        if dist < min_dist:
            min_dist = dist
            nearest_node = node
    return nearest_node