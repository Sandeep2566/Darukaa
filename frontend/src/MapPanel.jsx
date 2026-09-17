import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import 'mapbox-gl/dist/mapbox-gl.css';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';

function markerPosition(site) {
  const geometry = site.boundary;
  const ring = geometry?.type === 'Polygon' ? geometry.coordinates[0] : geometry?.coordinates?.[0]?.[0];
  if (ring?.length) {
    const total = ring.reduce((value, point) => [value[0] + point[0], value[1] + point[1]], [0, 0]);
    return [total[0] / ring.length, total[1] / ring.length];
  }
  return [78 + site.position[0] / 5, 12 + site.position[1] / 5];
}

export default function MapPanel({ sites, onSelect, onPolygon }) {
  const mapNode = useRef(null);
  const mapRef = useRef(null);

  useEffect(() => {
    const token = import.meta.env.VITE_MAPBOX_TOKEN;
    if (!token || !mapNode.current || mapRef.current) return undefined;
    mapboxgl.accessToken = token;
    const map = new mapboxgl.Map({ container: mapNode.current, style: 'mapbox://styles/mapbox/satellite-streets-v12', center: [78.96, 22.59], zoom: 4.3 });
    map.addControl(new mapboxgl.NavigationControl(), 'bottom-right');
    const draw = new MapboxDraw({ displayControlsDefault: false, controls: { polygon: true, trash: true } });
    map.addControl(draw, 'top-left');
    map.on('draw.create', (event) => onPolygon(event.features[0].geometry));
    map.on('load', () => {
      sites.forEach((site) => {
        if (site.boundary) {
          map.addSource(`site-${site.id}`, { type: 'geojson', data: { type: 'Feature', properties: {}, geometry: site.boundary } });
          map.addLayer({ id: `site-fill-${site.id}`, type: 'fill', source: `site-${site.id}`, paint: { 'fill-color': site.color, 'fill-opacity': 0.32 } });
          map.addLayer({ id: `site-line-${site.id}`, type: 'line', source: `site-${site.id}`, paint: { 'line-color': site.color, 'line-width': 2 } });
        }
        const marker = new mapboxgl.Marker({ color: site.color })
          .setLngLat(markerPosition(site))
          .setPopup(new mapboxgl.Popup().setHTML(`<strong>${site.name}</strong><br/>${site.hectares.toLocaleString()} ha`))
          .addTo(map);
        marker.getElement().addEventListener('click', () => onSelect(site));
      });
    });
    mapRef.current = map;
    return () => map.remove();
  }, [onPolygon, onSelect, sites]);

  return <div ref={mapNode} className="mapbox-map" aria-label="Interactive Mapbox map" />;
}
