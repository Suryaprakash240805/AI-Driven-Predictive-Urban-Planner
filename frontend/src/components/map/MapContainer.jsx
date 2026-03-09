import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet-draw";

// India center (can geocode based on user city)
const DEFAULT_CENTER = [20.5937, 78.9629];
const DEFAULT_ZOOM = 13;

export default function MapContainer({ onPolygonDrawn }) {
    const mapRef = useRef(null);
    const mapInstance = useRef(null);

    useEffect(() => {
        if (mapInstance.current) return;

        const map = L.map(mapRef.current, {
            center: DEFAULT_CENTER,
            zoom: DEFAULT_ZOOM,
            zoomControl: true,
        });

        // Dark tile layer (CartoDB Dark Matter)
        L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
            attribution: '© OpenStreetMap © CartoDB',
            maxZoom: 19,
        }).addTo(map);

        // Satellite overlay via Esri (optional toggle)
        const satellite = L.tileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            { attribution: "Esri", maxZoom: 19 }
        );

        // Layer control
        L.control.layers({ "Dark Map": map._layers[Object.keys(map._layers)[0]], "Satellite": satellite }).addTo(map);

        // Draw controls
        const drawnItems = new L.FeatureGroup().addTo(map);
        const drawControl = new L.Control.Draw({
            draw: {
                polygon: { shapeOptions: { color: "#D4AF37", weight: 2, fillOpacity: 0.15, fillColor: "#D4AF37" } },
                polyline: false, rectangle: false, circle: false,
                circlemarker: false, marker: false,
            },
            edit: { featureGroup: drawnItems },
        });
        map.addControl(drawControl);

        map.on(L.Draw.Event.CREATED, (e) => {
            drawnItems.clearLayers();
            drawnItems.addLayer(e.layer);
            const geo = e.layer.toGeoJSON();
            onPolygonDrawn && onPolygonDrawn(geo);
        });

        mapInstance.current = map;
        return () => { map.remove(); mapInstance.current = null; };
    }, []);

    return <div ref={mapRef} style={{ width: "100%", height: "100%", borderRadius: "inherit" }} />;
}
