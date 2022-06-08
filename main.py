import pandas as pd
import networkx as nx
from time import time

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from load_graph_data import *
from scipy import spatial
from os import environ 

load_dotenv(".flaskenv")
app = Flask(__name__)

df_stops = pd.read_csv('stops.txt')
roads, vertex, edges = load_data('maule.geojson',verbose=False)

puerto = environ.get('FLASK_RUN_PORT')

grafo = nx.Graph()
grafo.add_weighted_edges_from([(u,v,w) for ((u,v),w) in edges.items()])
max_subgrafo = max(nx.connected_components(grafo),key=len)

sub_grafo = grafo.subgraph(max_subgrafo)
node_data = [t for k,t in vertex.items() if k in sub_grafo]
tree = spatial.KDTree(node_data)

@app.route('/')
def root():
    initial_view = (df_stops['stop_lat'].median(),
                    df_stops['stop_lon'].median())
    return render_template('index.html', initial_view=initial_view,puerto=puerto)


@app.route('/nearest_vertex',methods=['POST',"GET"])
def get_nearest_vertex():
    select = request.form['selected']
    print(select)

    data = {
        "latInput": request.form['latInput'],
        "lngInput": request.form['lngInput'],
        "latTarget": request.form['latTarget'],
        "lngTarget": request.form['lngTarget']
    }

    puntos = [(float(data['latInput']), float(data['lngInput'])),
            (float(data['latTarget']), float(data['lngTarget']))]

    #!desde aca se hace el proceso
    
    _, ii1 = tree.query(puntos[0],1)
    _, ii2 = tree.query(puntos[1],1)


    inicio = hash(tuple(tree.data[ii1].tolist()))
    fin = hash(tuple(tree.data[ii2].tolist()))
    if select == "Dijkstra":
        start = time()
        path = nx.dijkstra_path(grafo,source=inicio,target=fin,weight='weight')
        fin = time() - start
    else:
        start = time()
        _,path = nx.single_source_bellman_ford(grafo,source=inicio,target=fin,weight='weight')
        fin = time() - start

    tiempo = fin
    coordinates = [ [vertex[p][1],vertex[p][0]] for p in path]
    # print(coordinates)

    geom_path = {"type":"Feature","geometry":{"type":"LineString","coordinates":coordinates}}

    json_data = {"type":"FeatureCollection","features":[geom_path]}
    return jsonify([json_data,tiempo])


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


# if __name__ == '__main__':
#     app.run(port=puerto, debug=True)
