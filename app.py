import os
from flask import Flask, Response, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)
mongo_db_url = os.environ.get("mongodb://localhost:27017/Integradora/plantitas")

client = MongoClient(mongo_db_url)
db = client['Integradora']

# Mensaje de conexión a la base de datos
print("Conexión a la base de datos establecida.")

# Ruta de prueba para confirmar que el servidor está en funcionamiento
@app.route("/api/test", methods=['GET'])
def test_connection():
    return "Servidor en funcionamiento y conexión a la base de datos establecida."

# Obtener datos de plantitas almacenados en la base de datos
@app.route("/api/plantita", methods=['GET'])
def get_plant_data():
    try:
        plant_data = list(db.plantitas.find())
        response = Response(response=dumps(plant_data), status=200, mimetype="application/json")
    except Exception as e:
        response = Response(response=f"Error: {e}", status=500)
    return response

# Agregar datos de plantitas a la base de datos
@app.route("/api/plantitas", methods=['POST'])
def add_plant_data():
    try:
        _json = request.json
        db.plantitas.insert_one(_json)
        resp = jsonify({"message": "Plant data added successfully"})
        resp.status_code = 200
    except Exception as e:
        resp = jsonify({"message": f"Error: {e}"})
        resp.status_code = 500
    return resp

# ...

# Actualizar la humedad de un dato existente en la base de datos
@app.route("/api/plantitas/update_humidity", methods=['PATCH'])
def update_plant_humidity():
    try:
        _json = request.json
        new_humidity = _json.get("humedad")

        db.plantitas.update_one({}, {"$set": {"humedad": new_humidity}})

        resp = jsonify({"message": "Plant humidity updated successfully"})
        resp.status_code = 200
    except Exception as e:
        resp = jsonify({"message": f"Error: {e}"})
        resp.status_code = 500
    return resp


# ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)