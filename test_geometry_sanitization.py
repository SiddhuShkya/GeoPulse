import json

def remove_z_coordinates(geometry):
    """Recursively remove Z coordinates from geometry coordinates."""
    if 'coordinates' in geometry:
        geometry['coordinates'] = _remove_z_recurse(geometry['coordinates'])
    return geometry

def _remove_z_recurse(coords):
    if not coords:
        return coords
    
    # Check if this is a coordinate point (list of numbers)
    if isinstance(coords[0], (int, float)):
        return coords[:2]  # Keep only x, y
    
    # Otherwise, it's a list of lists (or list of list of lists...)
    return [_remove_z_recurse(c) for c in coords]

geojson = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "FID": 0.0,
        "plot": 6.0,
        "elev_m": 162.5,
        "area_ha": 0.25
      },
      "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
          [
            [
              [
                -54.96773810280422,
                -3.025102981638353,
                0.0
              ],
              [
                -54.96729337458394,
                -3.025036104821649,
                0.0
              ]
            ]
          ]
        ]
      }
    }
  ]
}

def test_sanitization():
    print("Original coordinates:")
    print(geojson['features'][0]['geometry']['coordinates'][0][0][0])
    
    sanitized_geom = remove_z_coordinates(geojson['features'][0]['geometry'])
    
    print("\nSanitized coordinates:")
    print(sanitized_geom['coordinates'][0][0][0])
    
    assert len(sanitized_geom['coordinates'][0][0][0]) == 2
    print("\n✅ Sanitization successful")

if __name__ == "__main__":
    test_sanitization()
