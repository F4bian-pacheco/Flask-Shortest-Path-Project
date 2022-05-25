import json
import haversine as hs

def load_data(file_name,verbose=True):
    with open("maule.geojson",'r',encoding="utf-8") as file:
        data=json.load(file)
    E=dict()
    V=dict()
    for row in data['features']:
        if row['geometry']['type']=='LineString':
            coords=row['geometry']['coordinates']
            path_len=0
            # for (loc1,loc2) in zip(coords[:-1],coords[1:]):
            for (loc1,loc2) in zip(coords[:-1],coords[1:]):
                lon1,lat1=loc1
                lon2,lat2=loc2
                
                loc1=(lat1,lon1)
                loc2=(lat2,lon2)
                dist=hs.haversine(loc1,loc2)
                V.update({hash(loc1):loc1})
                V.update({hash(loc2):loc2})
                E.update({(hash(loc1),hash(loc2)):dist})
                path_len+=dist
            # if verbose:
            #     print('path length : {}, linestring length : {}'.format(path_len,row['properties']['st_length_']/1000))
            #     print(loc1,loc2)
    return data,V,E
