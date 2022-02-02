# import statements for web server
from flask import Flask
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request
import requests
import json
from pyfcm import FCMNotification


# import statements for data science packages
import pandas as pd
import networkx as nx
import pandas as pd
import uuid

app = Flask(__name__)

app.secret_key = "secretkey"

app.config['MONGO_URI'] = "mongodb+srv://jomtrace:jomtrace123@cluster0.gvczc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

mongo = PyMongo(app)

push_service = FCMNotification(
    api_key="AAAAxHy9O20:APA91bEFbzTh-DuDjwpsVxQI157V_LB7xiENnIKxLdJ0kpIdfQnH9RBi-DHTWwBcGPGpBWeNk7n3n4-5CD5gu0A4TSWKSdcaiPYOb6KZZILF76Vju9uAYSbBiX6lNZWzGt_HBLnnGxli")


@app.route('/getCentrality', methods=['POST'])
def get_centrality():
    _json = request.json
    _closeContact = _json['closeContact']
    _userID = _json['uuid']
    if _closeContact and _userID and request.method == 'POST':
        contactID = []
        for contact in _closeContact:
            contactID.append(contact['_uuid'])

        d = {"To": contactID}
        data = pd.DataFrame(d)
        data['From'] = _userID
        graph = nx.from_pandas_edgelist(data, source="From", target="To")
        centrality = nx.degree_centrality(graph)
        type(centrality)
        all_values = centrality.values()
        max_value = max(all_values)
        centrality_items = list(centrality.items())

        resp = jsonify(centrality_items[1][1])
        resp.status_code = 200

        return resp
    else:
        return not_found()


@app.route("/createUser", methods=['POST'])
def add_user():
    _json = request.json
    _uid = _json['uid']
    _username = _json['username']
    _mobile = _json['HpNo']
    _vaccinated = _json['vaccinated']
    _deviceToken = _json['deviceToken']
    _uuid = str(uuid.uuid4())

    if _uid and request.method == 'POST':
        id = mongo.db.user.insert_one({'uid': _uid, 'uuid': _uuid, 'username': _username, 'mobile': _mobile,
                                      'vaccinated': _vaccinated, 'deviceToken': _deviceToken, 'status': 'negative'})
        resp = jsonify(_uuid)
        resp.status_code = 200
        return resp
    else:
        not_found()


@app.route("/getUser/<id>", methods=['GET'])
def fetch_user(id):

    if id and request.method == 'GET':
        id = mongo.db.user.find({'uid': id})
        resp = dumps(id)

        return resp
    else:
        not_found()


@app.route("/pushnotification", methods=['POST'])
def push_exposure():

    registration_ids = ["deavjCAHS5CBPNCZ1kzt9Y:APA91bEsLcCPSJs6Ix_RtH3NKcGgG3AygWxsO7B5WiOk-JGPWSVOD5nVEg-4r5XTjjXf-ItR3XAn9tPEgHzD7L8OkUo6uyZKM_LFOxBeOXftsGYix5aMGWZas2qbPrkIrV_2swcxPztt",
                        "e8BzvAMjRTeAUeZYdZty0V:APA91bEtuCZNdKi_p5s0CImmxvsowafdY8UgxuvobXMIuszTjU3epDEQuliHbHM5aThQgvEUb4Qg8_HkEAbHMW5Cj1ftNceDL-1ne8XDvlj19ylsD0gjX1-vdSHOWk0Is1RZ-5PD3wmG"]
    message_title = "Jom tracing"
    message_body = "Please wear a mask"
    result = push_service.notify_multiple_devices(
        registration_ids=registration_ids, message_title=message_title, message_body=message_body)
    return(jsonify(result.json()))


@app.route("/uploadContactDetails", methods=['POST'])
def upload_details():
    _json = request.json
    _uuid = _json['uuid']
    _closeContact = _json['closeContact']
    _locationVisited = _json['locationVisited']

    if _uuid and _closeContact and _locationVisited and request.method == 'POST':
        id = mongo.db.user.find_one_and_update({'uuid': _uuid}, {
                                               "$set": {"closeContact": json.loads(_closeContact), "locationVisited": json.loads(_locationVisited), "status": 'Positive'}})
        notifyUsers = []

        for contact in _closeContact:
            notifyUsers.append(contact._uuid)

        suspectedIndividuals = mongo.db.user.find(
            {"uuid": {"$in": notifyUsers}})

        updateStatus = mongo.db.user.update_many(
            {"uuid": {"$in": notifyUsers}}, {"$set": {"status": "Suspected"}})

        suspectedDeviceToken = []
        print(suspectedIndividuals[0])
        for individuals in suspectedIndividuals:
            suspectedDeviceToken.append(individuals['deviceToken'])

        message_title = "Exposure Notification"
        message_body = "You have been suspected, please upload your details"
        result = push_service.notify_multiple_devices(
            registration_ids=suspectedDeviceToken, message_title=message_title, message_body=message_body)

        resp = jsonify("Contact details added")
        resp.status_code = 200
        return resp
    else:
        not_found()


@app.route("/pushExposure", methods=['POST'])
def pushExposureNotification():
    _json = request.json
    _closeContact = _json['closeContact']
    _message_title = _json['messageTitle']
    _message_body = _json['messageBody']

    if _closeContact and _message_title and _message_body and request.method == 'POST':
        result = push_service.notify_multiple_devices(
            registration_ids=_closeContact, message_title=_message_title, message_body=_message_body)
        resp = jsonify("Contact details added")
        resp.status_code = 200
        return resp
    else:
        not_found()


@app.route("/getPatients", methods=['GET'])
def getCovidUsers():
    if request.method == 'GET':
        infectedIndividuals = mongo.db.user.find(
            {"status": {"$eq": 'Positive'}})
        resp = dumps(infectedIndividuals)
        return resp


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
