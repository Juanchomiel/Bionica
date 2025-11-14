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
def recibir_sensores():
    try:
        data = request.get_json(force=True)
        
        emg1 = float(data.get("emg1", 0))
        emg2 = float(data.get("emg2", 0))
        emg3 = float(data.get("emg3", 0))

        print("📥 Datos recibidos:", data)

        point = (
            Point("emg")
            .tag("device", "ESP32")
            .field("emg1", emg1)
            .field("emg2", emg2)
            .field("emg3", emg3)
            .time(datetime.utcnow(), WritePrecision.NS)
        )

        write_api.write(bucket=bucket, org=org, record=point)
        print("✅ Guardado en InfluxDB")

        return jsonify({"status":"ok"}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"status":"error", "message": str(e)}), 400



@app.route("/", methods=["GET"])
def home():
    return "Servidor funcionando", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
