from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient, Point, WriteOptions
import os

app = Flask(__name__)

# -----------------------------
# CONFIGURACIÓN INFLUX
# -----------------------------
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)
write_api = client.write_api(write_options=WriteOptions(batch_size=1))

# -----------------------------
# ENDPOINT PARA ESP32
# -----------------------------
@app.route("/sensordata", methods=["POST"])
def sensordata():
    data = request.json
    valor = data.get("valor")

    try:
        p = (
            Point("prueba_esp")   
            .field("valor", float(valor))
        )
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=p)

        return jsonify({"status": "OK", "valor": valor}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return "Servidor funcionando", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
