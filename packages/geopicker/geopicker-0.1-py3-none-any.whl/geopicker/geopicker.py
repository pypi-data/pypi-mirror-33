import os
import pandas as pd
from geopy.distance import great_circle
import geopandas as gpd # makes transformation between vector files and dataframes
from shapely.geometry import shape
from shapely.geometry import Point
import shapefile
from json import dumps

#### input example - a point and polygons

coords = (0.1, 51.1)

coords_json = {
               "coordinates": {
               "longitude": 0.1,
               "latitude": 51.1
                }
               }

maps = {
    "maps" : {
        "postcodes" : "./sources/Districts.json",
        "population" : "./sources/llsoa_wgs84_map.shp"

    }
}

#### functions

def make_point_geometry(coordinates):
    '''
    convert a pair of coordinates (long, lat) into a geometry

    the input format should be a tuple or a json:

    coords_list = [0.1, 51.1]

    coords_tuple = (0.1, 51.1)

    coords_json = {"coordinates": {"longitude": 0.1,
                                   "latitude": 51.1}}
    '''

    def make_coords_json(coords_tuple_or_list):
        '''
        makes a tuple in the shape (longitude, latitude) NOTICE THE ORDER, into a json file
        '''
        coords_json = {
            "coordinates": {"longitude": coords_tuple_or_list[0],
                            "latitude": coords_tuple_or_list[1]}}
        return coords_json

    if type(coordinates) != 'dict':
        coordinates = make_coords_json(coordinates)
    coords = (coordinates["coordinates"]["longitude"], coordinates["coordinates"]["latitude"])
    geometry = [Point(coords)]
    crs = {'init': 'epsg:4326'}
    df = pd.DataFrame()
    gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
    return gdf

def convert_shp_to_geojson(input_shp_path, output_json_path):
    '''converts an ESRI shapefile into a geojson'''
    # read the shapefile
    reader = shapefile.Reader(input_shp_path)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", geometry=geom, properties=atr))
    # write the GeoJSON file
    geojson = open(output_json_path, "w")
    geojson.write(dumps({"type": "FeatureCollection","features": buffer}, indent=2) + "\n")
    geojson.close()

def extract_properties_from_map(geodf, geojson_shp_path, desired_property):
    '''
    here we extract the properties from a geojson (or shp), and parse it into a json
    however, if the property is None, then the output is left as is and all the properties are included
    '''
    polygons_geoj = gpd.read_file(geojson_shp_path)
    point_property = gpd.sjoin(geodf, polygons_geoj, how="inner", op="within")
    if desired_property != None:
        point_property = point_property[desired_property]
        point_property = {desired_property : point_property[0]}
        print("Output parsed containing the desired property")
    else:
        print("No property specified: output will contain all the properties available")
    return point_property

def list_of_properties_in_map(geojson_shp_path):
    '''
    sometimes we do not know what properties we might have in our files, so it is nice to be abl to print all the fields
    '''
    polygons_geoj = gpd.read_file(geojson_shp_path)
    property_fields = polygons_geoj.columns
    return property_fields


# testing ##################

os.getcwd()
os.chdir('./geopicker')
pointypoint = make_point_geometry(coords_json)
list_of_properties_in_map(pol_file_json)
pointyproperty = extract_properties_from_map(pointypoint, pol_file_json, "name")
