import shapely.wkt
from shapely.geometry import shape, Polygon
import pyproj
from functools import partial
from shapely.ops import transform

def calculate_area(geojson):
    # Calculate area in square meters using a projected coordinate system
    try:
        geom = shape(geojson['geometry'] if 'geometry' in geojson else geojson)
        
        # Project to a local UTM zone or just use a basic spherical approximation if needed
        # For simplicity in this restoration, using a standard equal-area projection logic
        project = partial(
            pyproj.transform,
            pyproj.Proj('EPSG:4326'), # source: WGS84
            pyproj.Proj('EPSG:3857')  # dest: Web Mercator (not strictly equal-area but common for web)
        )
        geom_projected = transform(project, geom)
        return geom_projected.area
    except Exception:
        return 0.0

def analyze_land_features(geojson):
    area = calculate_area(geojson)
    
    # Mock analysis for local development based on geometry
    # In a real app, these would come from GEE or Raster data
    return {
        "area_sqm": area,
        "ndvi": 0.45, # Mock value
        "flood_risk": area > 5000, # Mock logic
        "is_heritage": False,
        "soil_type": "Alluvial",
        "city": "Lucknow"
    }
