'''this does three possible things:
- get properties from a map at a given point
- convert a file form shapefile to geojson
- properties (names of fields) available in a map'''

from .geopicker import *

def get_properties_from_point(map_input_path, coords_json, desired_property): # desired_property can be None
    # get the points geometry
    gdf_points = make_point_geometry(coords_json)
    # extract the values from the map
    properties = extract_properties_from_map(gdf_points, map_input_path, *desired_property)
    return properties

def convert(input_shp_path, output_json_path):
    convert_shp_to_geojson(input_shp_path, output_json_path)

def properties_in_map(geojson_path):
    return list_of_properties_in_map(geojson_path)
