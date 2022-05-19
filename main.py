import pandas as pd
from flask import Flask, render_template, request,jsonify
from dotenv import load_dotenv
from load_graph_data import *

load_dotenv(".flaskenv")
app=Flask(__name__)

df_stops=pd.read_csv('stops.txt')
roads,vertex,edges=load_data('maule.geojson')

@app.route('/')
def root():
    initial_view=(df_stops['stop_lat'].median(),df_stops['stop_lon'].median())
    return render_template('index.html',initial_view=initial_view)

@app.route('/nearest_vertex', methods=['POST'])
def get_nearest_vertex():
    # try:
    #     latlng = request.args.get('latlng')
    #     return latlng
    # except:
    data = {
        "latInput":request.form['latInput'],
        "lngInput":request.form['lngInput'],
        "latTarget":request.form['latTarget'],
        "lngTarget":request.form['lngTarget']
    }

    puntos = [(data['latInput'],data['lngInput']),(data['latTarget'],data['lngTarget'])]
    print(puntos)
    return jsonify(data)   

@app.route('/stops', methods=['GET'])
def get_all_stops():
    stops = []
    for row in df_stops.iterrows():
        stops.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": (row[1]['stop_lon'],row[1]['stop_lat'])
            },
            "properties":{"name":row[1]['stop_name'],"lat":row[1]['stop_lat'],"lon":row[1]['stop_lon']}
        })
    json_data={"type": "FeatureCollection","features":stops}
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
