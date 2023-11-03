import geopandas as gpd
from shapely.geometry import Point, Polygon
from pyproj import CRS
import time
import rdflib
from rdflib import URIRef, Literal, RDF, XSD
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def divide_polygon(cell: Polygon, resolution: int = 100) -> list:
    """Divide extracted grid cells into 100x100m resolution cells"""

    x_min, y_min, x_max, y_max = cell.bounds
    smaller_polygons = []
    for x in range(int(x_min), int(x_max), resolution):
        for y in range(int(y_min), int(y_max), resolution):
            small_x_min, small_y_min, small_x_max, small_y_max = x, y, x + \
                resolution, y + resolution
            small_polygon = Polygon([(small_x_min, small_y_min), (small_x_max, small_y_min),
                                     (small_x_max, small_y_max), (small_x_min, small_y_max)])
            if small_polygon.intersects(cell):
                smaller_polygons.append(small_polygon)

    return smaller_polygons


def find_neighbors(gdf: gpd.GeoDataFrame, target_index: int) -> gpd.GeoDataFrame:
    """Find neighboring squares in a GeoDataFrame based on a target square."""

    target_polygon = gdf.geometry.iloc[target_index]

    # Use the spatial index to find neighboring squares efficiently
    gdf_sindex = gdf.sindex
    possible_matches_index = list(
        gdf_sindex.intersection(target_polygon.bounds))

    # Exclude the target square from the list of neighbors
    neighbors = gdf.iloc[possible_matches_index]
    neighbors = neighbors[neighbors.index != target_index]

    return neighbors


def convert_fire_cells_to_rdf(fire_cells: gpd.GeoDataFrame) -> rdflib.Graph:
    """create a rdf graph from the fire cells, storing geometry, certain cell attribues and neighbor relations"""

    g = rdflib.Graph()

    geo_ns = rdflib.Namespace("http://www.opengis.net/ont/geosparql#")
    sf_ns = rdflib.Namespace("http://www.opengis.net/ont/sf#")
    fire_aut_ns = rdflib.Namespace("http://example.org/fire_austria_ns#")

    g.bind("fire_austria", fire_aut_ns)

    # Iterate over GeoDataFrame rows and create RDF triples
    for idx, row in fire_cells.iterrows():

        geom = row["geometry"].wkt
        ent_cell = URIRef(fire_aut_ns[f"Cell_{idx}"])
        ent_cell_geom = URIRef(fire_aut_ns[f"Geom_Cell_{idx}"])
        ent_has_neighbor = URIRef(fire_aut_ns["hasNeighbor"])
        ent_fire = URIRef(fire_aut_ns["fire"])
        ent_date = URIRef(fire_aut_ns["date"])

        g.add((ent_cell, RDF.type, URIRef(fire_aut_ns["Cell"])))

        if not np.isnan(row["fire"]):
            g.add((ent_cell, ent_fire, Literal(
                bool(row['fire']), datatype=XSD.boolean)))
            g.add((ent_cell, ent_date, Literal(
                str(row['Datum']), datatype=XSD.date)))

        g.add((ent_cell, geo_ns.hasGeometry, ent_cell_geom))
        g.add((ent_cell_geom, RDF.type, sf_ns.Geometry))
        g.add((ent_cell_geom, geo_ns.asWKT, Literal(
            geom, datatype=geo_ns.wktLiteral)))

        for neighb_id, row in find_neighbors(fire_cells, idx).iterrows():
            ent_neighbor_cell = URIRef(fire_aut_ns[f"Cell_{neighb_id}"])
            g.add((ent_cell, ent_has_neighbor, ent_neighbor_cell))

    return g


if __name__ == "__main__":

    # directories to data
    path_to_fire_non_fire_points = "../../data/fire_data_subset/fire_points_aoi.shp"
    path_to_grid_1000m = "../../data/fire_data_subset/grid_1000m_aoi.shp"
    path_to_turtle_file = "../../data/fire_data_subset/fire_cells.ttl"

    # read data
    fire_nonfire_points = gpd.read_file(path_to_fire_non_fire_points)
    grid_1000m = gpd.read_file(path_to_grid_1000m)

    # create buffers (in meter) for points
    buffer_radius = 500
    point_buffers = fire_nonfire_points.buffer(buffer_radius)

    # intersect buffers with grid cells
    grid_1000m_selected = grid_1000m[grid_1000m.intersects(
        point_buffers.unary_union)]

    # divide 1000x1000 meter polygons into 100x100 meter polygons and create GeoDataFrame
    grid_100m = grid_1000m_selected.copy()
    grid_100m['geometry'] = grid_100m['geometry'].apply(divide_polygon)
    grid_100m = grid_100m.explode('geometry')
    grid_100m = gpd.GeoDataFrame(grid_100m)
    grid_100m.set_crs("EPSG:31287", inplace=True)

    # Join 100x100m grid cells with fire-non-fire points
    grid_100m_point_joined = gpd.sjoin(
        grid_100m, fire_nonfire_points, how='left', op='intersects')

    # select only the grid cells which intersect with the buffers
    grid_100m_buffer_selection = grid_100m_point_joined[grid_100m_point_joined.intersects(
        point_buffers.unary_union)]

    # Transform grid cells to 4326
    grid_100m_buffer_selection_4326 = grid_100m_buffer_selection.to_crs(
        epsg=4326)
    grid_100m_buffer_selection_4326.reset_index(inplace=True)

    # Convert fire cells to RDF and save as turtle file
    graph = convert_fire_cells_to_rdf(grid_100m_buffer_selection_4326)
    graph.serialize(destination=path_to_turtle_file, format="turtle")
