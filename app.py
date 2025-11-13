from flask import Flask, request, jsonify
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
import os

app = Flask(__name__)

# ===========================
# Variables de entorno Render
# ===========================
token = os.environ.get("INFLUX_TOKEN")
org = os.environ.get("INFLUX_ORG")
bucket = os.environ.get("INFLUX_BUCKET")
url = os.environ.get("INFLUX_URL")

print("=== VARIABLES DE ENTORNO ===")
print("URL:", url)
print("ORG:", org)
print("BUCKET:", bucket)
print("TOKEN existe:", token is not None)

# Cliente Influx
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api()

@app.route("/", methods=["GET"])
def home():
    return "Servidor funcionando", 200

@app.route("/test", methods=["POST"])
def test():
    """
    Recibe un solo valor 'valor' y lo guarda en InfluxDB.
    """
    try:
        data = request.get_json()

        if not data or "valor" not in data:
            return jsonify({"error": "JSON debe contener 'valor'"}), 400

        valor = float(data["valor"])

        # Crear punto
        p = (
            Point("test_measurement")
            .field("valor", valor)
            .time(datetime.utcnow(), WritePrecision.NS)
        )

        write_api.write(bucket=bucket, org=org, record=p)

        print("Dato enviado a Influx:", data)

        return jsonify({"status": "ok", "enviado": valor}), 200

    except Exception as e:
        print("ERROR Influx:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


# Ejecutar
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
