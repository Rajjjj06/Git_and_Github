from flask import Flask, jsonify, redirect, render_template, request, url_for
import pymongo
from dotenv import load_dotenv
import os
import json


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

file_path = 'data.json'

client = pymongo.MongoClient(MONGO_URI)


db = client.test
collection = db.test_collection
todo_collection = db.todo_items

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/api')
@app.route('/data')
def read_data():
    with open('data.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    age = request.form.get("age", "").strip()
    city = request.form.get("city", "").strip()

    try:
        if not name or not age or not city:
            raise ValueError("All fields are required.")

        data = {
            "name": name,
            "age": int(age),
            "city": city
        }

        result = collection.insert_one(data)
        data["_id"] = str(result.inserted_id)

        with open(file_path, "r") as f:
            existing_data = json.load(f)
        existing_data.append(data)
        with open(file_path, "w") as f:
            json.dump(existing_data, f)

        return redirect(url_for("success"))
    except (pymongo.errors.PyMongoError, OSError, ValueError) as error:
        return render_template("index.html", error=f"Unable to submit data: {error}"), 400


@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    json_payload = request.get_json()
    if json_payload is None:
        payload = request.form
    elif isinstance(json_payload, dict):
        payload = json_payload
    else:
        return jsonify({"error": "Request body must be a JSON object."}), 400

    item_name = payload.get("itemName")
    item_description = payload.get("itemDescription")

    if (
        not isinstance(item_name, str)
        or not isinstance(item_description, str)
        or not item_name.strip()
        or not item_description.strip()
    ):
        return jsonify({
            "error": "itemName and itemDescription are required."
        }), 400
    item_name = item_name.strip()
    item_description = item_description.strip()

    try:
        result = todo_collection.insert_one({
            "itemName": item_name,
            "itemDescription": item_description
        })
    except pymongo.errors.PyMongoError as error:
        return jsonify({"error": f"Unable to save todo item: {error}"}), 500

    return jsonify({
        "message": "Todo item saved successfully.",
        "id": str(result.inserted_id)
    }), 201


@app.route("/success")
def success():
    return render_template("success.html")




app.run(debug=True)
