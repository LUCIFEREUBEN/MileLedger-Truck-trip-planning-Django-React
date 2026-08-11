import { useEffect, useRef } from "react";
import maplibregl, { LngLatBounds, type Map as MapLibreMap, type Marker } from "maplibre-gl";
import { Crosshair, MapPin } from "lucide-react";
import type { TripPlan } from "../../types";

const mapStyle = {
  version: 8 as const,
  sources: {
    osm: { type: "raster" as const, tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"], tileSize: 256, attribution: "© OpenStreetMap contributors" },
  },
  layers: [
    { id: "paper", type: "background" as const, paint: { "background-color": "#e7e2d7" } },
    { id: "osm", type: "raster" as const, source: "osm", paint: { "raster-saturation": -0.78, "raster-contrast": 0.08, "raster-opacity": 0.82 } },
  ],
};

export function RouteMap({ plan, selectedEventId, onSelect }: { plan: TripPlan; selectedEventId: string | null; onSelect: (id: string) => void }) {
  const node = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Marker[]>([]);

  useEffect(() => {
    if (!node.current) return;
    const map = new maplibregl.Map({ container: node.current, style: mapStyle, center: plan.route.waypoints.pickup, zoom: 4, attributionControl: false });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");
    map.on("load", () => {
      map.addSource("trip-route", { type: "geojson", data: plan.route.geometry });
      map.addLayer({ id: "route-casing", type: "line", source: "trip-route", paint: { "line-color": "#fffaf1", "line-width": 8, "line-opacity": 0.9 } });
      map.addLayer({ id: "route-line", type: "line", source: "trip-route", paint: { "line-color": "#1b6e68", "line-width": 4, "line-opacity": 0.95 }, layout: { "line-cap": "round", "line-join": "round" } });
      const bounds = new LngLatBounds(); plan.route.geometry.coordinates.forEach(coord => bounds.extend(coord)); map.fitBounds(bounds, { padding: 64, maxZoom: 8, duration: 0 });
    });
    mapRef.current = map;
    return () => { markersRef.current.forEach(marker => marker.remove()); map.remove(); mapRef.current = null; };
  }, [plan]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    markersRef.current.forEach(marker => marker.remove()); markersRef.current = [];
    const stops = plan.events.filter(event => event.coordinates && event.status !== "DRIVING");
    for (const event of stops) {
      const button = document.createElement("button");
      button.className = `map-marker ${event.reason_code.toLowerCase()} ${selectedEventId === event.id ? "selected" : ""}`;
      button.type = "button"; button.title = event.remark; button.setAttribute("aria-label", `${event.remark}, ${event.location_label}`);
      button.addEventListener("click", () => onSelect(event.id)); button.addEventListener("mouseenter", () => onSelect(event.id));
      markersRef.current.push(new maplibregl.Marker({ element: button, anchor: "center" }).setLngLat(event.coordinates!).addTo(map));
    }
    for (const [key, label] of [["current", "Start"], ["pickup", "Pickup"], ["dropoff", "Drop-off"]] as const) {
      const marker = document.createElement("div"); marker.className = `waypoint-marker ${key}`; marker.textContent = label[0]; marker.title = label;
      markersRef.current.push(new maplibregl.Marker({ element: marker, anchor: "center" }).setLngLat(plan.route.waypoints[key]).addTo(map));
    }
  }, [plan, selectedEventId, onSelect]);

  const fit = () => { const map = mapRef.current; if (!map) return; const bounds = new LngLatBounds(); plan.route.geometry.coordinates.forEach(coord => bounds.extend(coord)); map.fitBounds(bounds, { padding: 64, maxZoom: 8, duration: 500 }); };
  return <div className="map-panel">
    <div className="map-caption"><div><p className="eyebrow">Route canvas</p><h2>{plan.route.addresses.pickup.split(",")[0]} <span>to</span> {plan.route.addresses.dropoff.split(",")[0]}</h2></div><button aria-label="Fit map to full route" onClick={fit}><Crosshair /> Fit route</button></div>
    <div ref={node} className="map-canvas" aria-label={`Route map from ${plan.route.addresses.current} through ${plan.route.addresses.pickup} to ${plan.route.addresses.dropoff}`} />
    <div className="map-legend"><span><i className="start" /> Start</span><span><i className="pickup" /> Pickup / drop-off</span><span><i className="rest" /> Break / rest</span><span><i className="fuel" /> Fuel</span></div>
    <details className="directions"><summary><MapPin /> Route instructions <span>{plan.route.segments.reduce((sum, segment) => sum + segment.instructions.length, 0)} steps</span></summary>{plan.route.segments.flatMap(segment => segment.instructions).map((step, index) => <p key={index}><b>{index + 1}</b>{step.instruction ?? "Continue on route"}<small>{step.distance_m ? `${Math.round(step.distance_m / 1609.344)} mi` : ""}</small></p>)}</details>
  </div>;
}

