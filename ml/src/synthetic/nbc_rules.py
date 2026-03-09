"""
NBC 2016 (National Building Code India) rules encoded as Python logic.
Used to generate valid and invalid synthetic training graphs.
"""

NBC_RULES = {
    # Zone adjacency compatibility (True = allowed)
    "adjacency": {
        ("residential",  "residential"):  True,
        ("residential",  "commercial"):   True,
        ("residential",  "green_space"):  True,
        ("residential",  "road"):         True,
        ("residential",  "parking"):      True,
        ("residential",  "utility"):      False,
        ("residential",  "industrial"):   False,
        ("residential",  "setback"):      True,
        ("commercial",   "commercial"):   True,
        ("commercial",   "road"):         True,
        ("commercial",   "parking"):      True,
        ("commercial",   "green_space"):  True,
        ("commercial",   "utility"):      True,
        ("commercial",   "industrial"):   False,
        ("green_space",  "road"):         True,
        ("green_space",  "residential"):  True,
        ("green_space",  "industrial"):   False,
        ("road",         "road"):         True,
        ("road",         "parking"):      True,
        ("utility",      "road"):         True,
        ("utility",      "commercial"):   True,
        ("setback",      "residential"):  True,
        ("setback",      "road"):         True,
    },
    # Floor Area Ratio limits by use type
    "far_limits": {
        "personal_residence":  1.5,
        "commercial_complex":  2.5,
        "residential_complex": 2.0,
    },
    # Minimum setback from road boundary (metres)
    "setback_m": {
        "personal_residence":  3.0,
        "commercial_complex":  4.5,
        "residential_complex": 4.0,
    },
    # Minimum green space ratio (0-1)
    "min_green_ratio": 0.15,
    # Minimum road width (metres)
    "min_road_width":  6.0,
    # Minimum parking ratio (fraction of total area)
    "min_parking_ratio": 0.10,
}

def is_adjacent_valid(zone_a: str, zone_b: str) -> bool:
    key  = (zone_a, zone_b)
    rkey = (zone_b, zone_a)
    return NBC_RULES["adjacency"].get(key, NBC_RULES["adjacency"].get(rkey, True))

def compute_green_ratio(zones: list[dict]) -> float:
    total = sum(z["area"] for z in zones)
    green = sum(z["area"] for z in zones if z["type"] == "green_space")
    return green / total if total > 0 else 0.0

def validate_layout(zones: list[dict], edges: list[tuple]) -> dict:
    violations = []
    for a, b in edges:
        if not is_adjacent_valid(zones[a]["type"], zones[b]["type"]):
            violations.append(f"Invalid adjacency: {zones[a]['type']} ↔ {zones[b]['type']}")
    green_ratio = compute_green_ratio(zones)
    if green_ratio < NBC_RULES["min_green_ratio"]:
        violations.append(f"Insufficient green space: {green_ratio:.1%} < 15%")
    return {"valid": len(violations) == 0, "violations": violations}
