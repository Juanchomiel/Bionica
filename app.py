from flask import Flask, request, jsonify
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
import os

app = Flask(__name__)

# Leer configuración desde variables de entorno
token = os.environ.get("INFLUX_TOKEN")
org = os.environ.get("INFLUX_ORG")
bucket = os.environ.get("INFLUX_BUCKET")
url = os.environ.get("INFLUX_URL")  # ejemplo: https://us-east-1-1.aws.cloud2.influxdata.com

if not all([token, org, bucket, url]):
    raise RuntimeError("Faltan variables de entorno: INFLUX_TOKEN/INFLUX_ORG/INFLUX_BUCKET/INFLUX_URL")

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok"}), 200

@app.route("/data", methods=["POST"])
def recibir_datos():
    try:
        data = request.get_json(force=True)
        servoF = float(data.get("servoF", 0))
        servoE = float(data.get("servoE", 0))
        xe = float(data.get("xe", 0))
        xe2 = float(data.get("xe2", 0))

        point = (
            Point("sensores")
            .tag("dispositivo", "ESP32")
            .field("servoF", servoF)
            .field("servoE", servoE)
            .field("Xe", xe)
            .field("Xe2", xe2)
            .time(datetime.utcnow(), WritePrecision.NS)
        )

        write_api.write(bucket=bucket, org=org, record=point)
        print("✅ Dato enviado a InfluxDB:", data)  # <-- AGREGAR ESTO
        return jsonify({"status": "ok", "message": "Dato guardado"}), 200

    except Exception as e:
        print("❌ Error al guardar en InfluxDB:", str(e))  # <-- AGREGAR ESTO
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
