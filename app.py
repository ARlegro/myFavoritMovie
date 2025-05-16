from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests, re, json
from flask.json.provider import JSONProvider
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb://root:pwd1234@localhost", 27018)
db = client.favoriteMovie


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


# 위에 정의되 custom encoder 를 사용하게끔 설정한다.
app.json = CustomJSONProvider(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/movies", methods=["GET"])
def getMovies():
    sortMode = request.args.get("sortMode", "likes")
    trashMode = request.args.get("trashMode", "false").lower() == "true"
    sortDirection = -1

    sortSpec = [(sortMode, sortDirection)]
    if sortMode == "date":
        sortSpec = [
            ("openYear", sortDirection),
            ("openMonth", sortDirection),
            ("openDay", sortDirection),
        ]
    print(f"sortMode: {sortMode}, trashed: {trashMode}")

    try:
        movies = list(db.movies.find({"trashed": trashMode}).sort(sortSpec))
        return jsonify({"result": "success", "movies": movies})

    except Exception as e:
        return jsonify({"result": "error", "message": str(e)})


@app.route("/movies/<id>/like", methods=["PATCH"])
def likeMovie(id):

    result = db.movies.update_one(
        {"_id": ObjectId(id)},
        {"$inc": {"likes": 1}},
    )

    if result.matched_count == 1:
        return jsonify({"result": "success"})
    else:
        return jsonify({"result": "error", "message": "Failed to like movie"})


@app.route("/movies/<id>/trash", methods=["PATCH"])
def trashMovie(id):

    result = db.movies.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"trashed": True}},
    )

    if result.matched_count == 1:
        return jsonify({"result": "success", "message": "Movie trashed"})

    else:
        return jsonify({"result": "error", "message": "Failed to trash movie"})


@app.route("/movies/<id>/restore", methods=["PATCH"])
def restoreMovie(id):

    print(f"restoreMovie: {id}")
    result = db.movies.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"trashed": False}},
    )

    if result.matched_count == 1:
        print("Movie restored")
        return jsonify({"result": "success", "message": "Movie trashed"})

    else:
        return jsonify({"result": "error", "message": "Failed to trash movie"})


@app.route("/movies/<id>", methods=["DELETE"])
def deleteMovie(id):
    print(f"deleteMovie: {id}")
    result = db.movies.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 1:
        return jsonify({"result": "success", "message": "Movie removed"})

    else:
        return jsonify({"result": "error", "message": "Failed to remove movie"})


if __name__ == "__main__":

    app.run(host="0.0.0.0", debug=True, port=5000)
