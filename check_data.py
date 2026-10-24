import zipfile
import re
from bs4 import BeautifulSoup

with zipfile.ZipFile('SABRA.kmz-2', 'r') as kmz:
    kml_file = [f for f in kmz.namelist() if f.endswith('.kml')][0]
    with kmz.open(kml_file, 'r') as f:
        soup = BeautifulSoup(f, 'xml')
        
# Use regex to ignore XML namespaces
points = soup.find_all(re.compile('Point', re.IGNORECASE))
lines = soup.find_all(re.compile('LineString', re.IGNORECASE))
polygons = soup.find_all(re.compile('Polygon', re.IGNORECASE))

print(f"Markers (Points) found: {len(points)}")
print(f"Paths (Lines) found: {len(lines)}")
print(f"Shapes (Polygons) found: {len(polygons)}")