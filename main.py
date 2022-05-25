import pandas as pd
import networkx as nx

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from load_graph_data import *
from scipy.spatial.kdtree import KDTree

load_dotenv(".flaskenv")
app = Flask(__name__)

df_stops = pd.read_csv('stops.txt')
roads, vertex, edges = load_data('maule.geojson')


@app.route('/')
def root():
    initial_view = (df_stops['stop_lat'].median(),
                    df_stops['stop_lon'].median())
    return render_template('index.html', initial_view=initial_view)


@app.route('/nearest_vertex', methods=['POST'])
def get_nearest_vertex():
    # try:
    #     latlng = request.args.get('latlng')
    #     return latlng
    # except:
    data = {
        "latInput": request.form['latInput'],
        "lngInput": request.form['lngInput'],
        "latTarget": request.form['latTarget'],
        "lngTarget": request.form['lngTarget']
    }

    puntos = [(float(data['latInput']), float(data['lngInput'])),
            (float(data['latTarget']), float(data['lngTarget']))]

    #!desde aca se hace el proceso

    grafo = nx.Graph()
    grafo.add_weighted_edges_from([(u,v,w) for ((u,v),w) in edges.items()])
    # len_subgrafos = [len(c) for c in sorted(nx.connected_components(grafo), key=len, reverse=True)]
    max_subgrafo = max(nx.connected_components(grafo),key=len)

    sub_grafo = grafo.subgraph(max_subgrafo)

    
    tree = KDTree(list(sub_grafo.edges))
    
    dd1,ii1 = tree.query(puntos[0],1)
    dd2,ii2 = tree.query(puntos[1],1)

    inicio = hash(tuple(tree.data[ii1].tolist()))
    fin = hash(tuple(tree.data[ii2].tolist()))
    #TODO Saber que grafo usar
    # path = nx.shortest_path(sub_grafo,source=inicio,target=fin,weight='weight')
    coordinates = [ [vertex[p][1],vertex[p][0]] for p in path]

    geom_path = {"type": "Feature","geometry":{"type":"LineString","coordinates":coordinates}}

    json_data = {"type":"FeatureCollection","features":[geom_path]}
    return jsonify(json_data)


@app.route('/stops', methods=['GET'])
def get_all_stops():
    stops = []
    for row in df_stops.iterrows():
        stops.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": (row[1]['stop_lon'], row[1]['stop_lat'])
            },
            "properties": {"name": row[1]['stop_name'], "lat": row[1]['stop_lat'], "lon": row[1]['stop_lon']}
        })
    json_data = {"type": "FeatureCollection", "features": stops}
    return jsonify(json_data)


@app.route('/roads', methods=['GET'])
def get_all_roads():
    road_list = []
    for row in roads['features']:
        road_list.append({
            "type": "Feature",
            "geometry": row['geometry']
        })
    return jsonify(roads['features'])


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)
