# import statements for web server
from flask import Flask
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request

# import statements for data science packages
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.metrics.cluster import normalized_mutual_info_score
from sklearn.metrics.cluster import adjusted_rand_score
from itertools import combinations
import uuid

app = Flask(__name__)

app.secret_key = "secretkey"

app.config['MONGO_URI'] = "mongodb+srv://jomtrace:jomtrace123@cluster0.gvczc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

mongo = PyMongo(app)


@app.route('/', methods=['GET'])
def get_centrality():
    if request.method == 'GET':
        data = pd.read_csv("covid-19 transmission.csv")
        graph = nx.from_pandas_edgelist(data, source="From", target="To")
        centrality = nx.degree_centrality(graph)
        type(centrality)
        all_values = centrality.values()
        max_value = max(all_values)
        centrality_items = list(centrality.items())

        resp = jsonify(centrality_items)
        resp.status_code = 200

        return resp
    else:
        return not_found()


@app.route("/createUser", methods=['POST'])
def add_user():
    _json = request.json
    _uid = _json['uid']

    if _uid and request.method == 'POST':
        id = mongo.db.user.insert_one({'uid': _uid, 'uuid': str(uuid.uuid4())})
        resp = jsonify("User added successfully")
        resp.status_code = 200
        return resp
    else:
        not_found()


@app.route("/uploadContactDetails", methods=['PATCH'])
def upload_details():
    _json = request.json
    _uuid = _json['uuid']
    _closeContact = _json['closeContact']
    _locationVisited = _json['locationVisited']

    if _uuid and _closeContact and _locationVisited and request.method == 'PATCH':
        id = mongo.db.user.find_one_and_update({'uuid': _uuid}, {
                                               "$set": {"closeContact": _closeContact, "locationVisited": _locationVisited}})
        resp = jsonify("User added successfully")
        resp.status_code = 200
        return resp
    else:
        not_found()


@app.route("/createLocation", methods=['POST'])
def create_location():
    _json = request.json
    _locationName = _json['locationName']
    _capacity = _json['capacity']

    if _locationName and _capacity and request.method == 'POST':
        id = mongo.db.location.insert_one(
            {'locationName': _locationName, 'capacity': _capacity, 'visitorsCount': 0})
        resp = jsonify("Location created")
        resp.status_code = 200
        return resp
    else:
        not_found()


@app.route("/getLocations", methods=['GET'])
def get_locations():
    locations = mongo.db.location.find()
    resp = dumps(locations)
    return resp


@app.route("/checkIn", methods=['POST'])
def check_in():
    _json = request.json
    _location = _json['location']
    if _location and request.method == 'POST':
        id = mongo.db.location.find_one_and_update(
            {'_id': ObjectId(_location)}, {"$inc": {"visitorsCount": 1}})
        resp = jsonify("Checked in to location")
        resp.status_code = 200
        return resp
    else:
        not_found()


@app.route("/checkOut", methods=['POST'])
def check_out():
    _json = request.json
    _location = _json['location']
    if _location and request.method == 'POST':
        id = mongo.db.location.find_one_and_update(
            {'_id': ObjectId(_location)}, {"$inc": {"visitorsCount": -1}})
        resp = jsonify("Checked out from location")
        resp.status_code = 200
        return resp
    else:
        not_found()


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found' + request.url
    }

    resp = jsonify(message)

    resp.status_code = 404

    return resp


if __name__ == "__main__":
    app.run(debug=True)
