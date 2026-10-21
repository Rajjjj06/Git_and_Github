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


@app.route("/success")
def success():
    return render_template("success.html")




app.run(debug=True)

