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
