import React, { useState, useRef } from 'react';
import Map, { Source, Layer, NavigationControl, Popup } from 'react-map-gl/maplibre';
import type { MapRef } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

interface MapViewProps {
  selectedLayers: string[];
}

const MapView: React.FC<MapViewProps> = ({ selectedLayers }) => {
  const mapRef = useRef<MapRef>(null);
  const [hoverInfo, setHoverInfo] = useState<any>(null);
  const [selectedFeature, setSelectedFeature] = useState<any>(null);

  const initialViewState = {
    longitude: 79.905,
    latitude: 6.955,
    zoom: 13,
    pitch: 45,
    bearing: 0
  };

  // Layer Styles (MapLibre Style Specs)
  const layerStyles: Record<string, any> = {
    buildings: {
        id: 'buildings-layer',
        type: 'fill-extrusion',
        source: 'buildings',
        'source-layer': 'buildings',
        paint: {
            'fill-extrusion-color': '#f59e0b',
            'fill-extrusion-height': 15,
            'fill-extrusion-base': 0,
            'fill-extrusion-opacity': 0.8
        }
    },
    buildingsHighlight: {
        id: 'buildings-highlight',
        type: 'fill-extrusion',
        source: 'buildings',
        'source-layer': 'buildings',
        paint: {
            'fill-extrusion-color': '#ffffff',
            'fill-extrusion-height': 16,
            'fill-extrusion-base': 0,
            'fill-extrusion-opacity': 0.9
        },
        filter: ['==', ['get', 'id'], selectedFeature?.properties?.id || '']
    },
    roads: {
        id: 'roads-layer',
        type: 'line',
        source: 'roads',
        'source-layer': 'roads',
        layout: {
            'line-join': 'round',
            'line-cap': 'round'
        },
        paint: {
            'line-color': '#ffffff',
            'line-width': 2,
            'line-opacity': 0.8
        }
    },
    flood: {
        id: 'flood-layer',
        type: 'fill',
        source: 'flood',
        'source-layer': 'flood',
        paint: {
            'fill-color': [
                'case',
                ['==', ['downcase', ['get', 'risk_level']], 'high'], '#ef4444',
                ['==', ['downcase', ['get', 'risk_level']], 'medium'], '#f97316',
                '#3b82f6'
            ],
            'fill-opacity': 0.7
        }
    },
    floodHighlight: {
        id: 'flood-highlight',
        type: 'line',
        source: 'flood',
        'source-layer': 'flood',
        paint: {
            'line-color': '#ffffff',
            'line-width': 4,
            'line-opacity': 1
        },
        filter: ['==', ['get', 'id'], selectedFeature?.properties?.id || '']
    }
  };

  const onHover = (event: any) => {
    const feature = event.features && event.features[0];
    if (feature) {
      setHoverInfo({
        longitude: event.lngLat.lng,
        latitude: event.lngLat.lat,
        properties: feature.properties
      });
    } else {
      setHoverInfo(null);
    }
  };

  const onClick = (event: any) => {
    const feature = event.features && event.features[0];
    if (feature) {
      setSelectedFeature({
        longitude: event.lngLat.lng,
        latitude: event.lngLat.lat,
        properties: feature.properties
      });
    } else {
      setSelectedFeature(null);
    }
  };

  return (
    <div className="w-full h-full relative bg-[#020617]">
      <Map
        ref={mapRef}
        initialViewState={initialViewState}
        style={{ width: '100%', height: '100%' }}
        mapStyle={{
          version: 8,
          sources: {
            'google-satellite': {
              type: 'raster',
              tiles: ['https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'],
              tileSize: 256,
              attribution: '&copy; Google'
            }
          },
          layers: [
            {
              id: 'google-satellite-layer',
              type: 'raster',
              source: 'google-satellite',
              minzoom: 0,
              maxzoom: 22
            }
          ]
        }}
        interactiveLayerIds={['buildings-layer', 'roads-layer', 'flood-layer']}
        onMouseMove={onHover}
        onClick={onClick}
      >
        <NavigationControl position="bottom-right" />

        {/* Buildings Vector Source */}
        {selectedLayers.includes('buildings') && (
            <Source 
                id="buildings" 
                type="vector" 
                tiles={['/api/spatial/tiles/buildings/{z}/{x}/{y}']}
            >
                <Layer {...layerStyles.buildings} />
                <Layer {...layerStyles.buildingsHighlight} />
            </Source>
        )}

        {/* Roads Vector Source */}
        {selectedLayers.includes('roads') && (
            <Source 
                id="roads" 
                type="vector" 
                tiles={['/api/spatial/tiles/roads/{z}/{x}/{y}']}
            >
                <Layer {...layerStyles.roads} />
            </Source>
        )}

        {/* Flood Vector Source */}
        {selectedLayers.includes('flood') && (
            <Source 
                id="flood" 
                type="vector" 
                tiles={['/api/spatial/tiles/flood/{z}/{x}/{y}']}
            >
                <Layer {...layerStyles.flood} />
                <Layer {...layerStyles.floodHighlight} />
            </Source>
        )}

        {(selectedFeature || hoverInfo) && (
          <Popup
            longitude={(selectedFeature || hoverInfo).longitude}
            latitude={(selectedFeature || hoverInfo).latitude}
            closeButton={!!selectedFeature}
            onClose={() => setSelectedFeature(null)}
            className="premium-popup"
            offset={15}
          >
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl min-w-[200px]">
              <div className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2 border-b border-slate-800 pb-1 flex justify-between items-center">
                <span>{selectedFeature ? 'Selected_Feature' : 'Hover_Metadata'}</span>
                {selectedFeature && <span className="text-[8px] bg-amber-500/20 text-amber-500 px-1 rounded">ACTIVE</span>}
              </div>
              {Object.entries((selectedFeature || hoverInfo).properties).map(([key, val]) => (
                <div key={key} className="flex justify-between gap-4 mb-1">
                  <span className="text-[10px] text-slate-400 font-bold uppercase">{key}</span>
                  <span className="text-[10px] font-black text-white italic truncate max-w-[120px]">{String(val)}</span>
                </div>
              ))}
            </div>
          </Popup>
        )}
      </Map>

      {/* Map Legend */}
      <div className="absolute bottom-8 left-8 z-[1000] glass-panel p-4 rounded-2xl border border-blue-500/20">
        <div className="text-[9px] font-black uppercase tracking-widest text-slate-500 mb-3">Map Legend</div>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">HIGH RISK ZONE</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">NORMAL HYDRAULIC</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-sm bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">3D BUILDING</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapView;
