import ee
import json
from app.config import settings

def init_gee():
    """Initialize Google Earth Engine with service account credentials."""
    try:
        credentials = ee.ServiceAccountCredentials(
            settings.GEE_SERVICE_ACCOUNT,
            settings.GEE_KEY_FILE
        )
        ee.Initialize(credentials)
    except Exception as e:
        print(f"[GEE] Initialization failed: {e}. Using mock mode.")

async def analyze_land_polygon(geojson: dict) -> dict:
    """
    Analyze a land polygon using Sentinel-2 satellite data.
    Returns NDVI, NDBI, elevation, slope, flood risk, heritage flags.
    """
    try:
        coords = geojson["geometry"]["coordinates"]
        aoi    = ee.Geometry.Polygon(coords)

        # Sentinel-2 Surface Reflectance (cloud < 20%)
        s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterBounds(aoi)
              .filterDate("2023-01-01", "2024-01-01")
              .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
              .median())

        # NDVI: (B8 - B4) / (B8 + B4)
        ndvi = s2.normalizedDifference(["B8", "B4"]).rename("NDVI")
        # NDBI: (B11 - B8) / (B11 + B8)
        ndbi = s2.normalizedDifference(["B11", "B8"]).rename("NDBI")

        ndvi_val = ndvi.reduceRegion(ee.Reducer.mean(), aoi, 10).getInfo().get("NDVI", 0)
        ndbi_val = ndbi.reduceRegion(ee.Reducer.mean(), aoi, 10).getInfo().get("NDBI", 0)

        # SRTM Elevation
        dem   = ee.Image("USGS/SRTMGL1_003")
        slope = ee.Terrain.slope(dem)
        elev_val  = dem.reduceRegion(ee.Reducer.mean(), aoi, 30).getInfo().get("elevation", 0)
        slope_val = slope.reduceRegion(ee.Reducer.mean(), aoi, 30).getInfo().get("slope", 0)

        # Area in sqm via projection
        area_sqm = aoi.area(1).getInfo()

        return {
            "area_sqm":         round(area_sqm, 2),
            "ndvi":             round(ndvi_val or 0, 4),
            "ndbi":             round(ndbi_val or 0, 4),
            "elevation_m":      round(elev_val or 0, 2),
            "slope_deg":        round(slope_val or 0, 2),
            "groundwater_depth": 5.0,   # placeholder; integrate CGWB API
            "flood_risk":       1 if (slope_val or 0) < 1.0 else 0,
            "is_heritage":      0,       # integrate ASI/state heritage DB
            "centroid":         str(aoi.centroid(1).coordinates().getInfo()),
        }
    except Exception:
        # Mock fallback for development without GEE credentials
        return _mock_land_info()

def _mock_land_info() -> dict:
    return {
        "area_sqm": 1250.0, "ndvi": 0.32, "ndbi": 0.15,
        "elevation_m": 412.0, "slope_deg": 3.2,
        "groundwater_depth": 8.5, "flood_risk": 0,
        "is_heritage": 0, "centroid": "[78.9, 20.5]",
    }
