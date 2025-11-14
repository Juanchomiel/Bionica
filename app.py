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
@app.route('/sensordata', methods=['POST'])
def sensordata():
    try:
        data = request.get_json()

        print("📥 Datos recibidos desde ESP32:", data)

        # Extraer valores correctos según la ESP
        s1 = data.get("emg1")
        s2 = data.get("emg2")
        s3 = data.get("emg3")

        print(f"✔ emg1={s1}, emg2={s2}, emg3={s3}")

        # Convertir a números si vienen como strings
        s1 = float(s1)
        s2 = float(s2)
        s3 = float(s3)

        # Line protocol
        line = f"mioelectrico emg1={s1},emg2={s2},emg3={s3}"

        print("📤 Enviando a InfluxDB:", line)

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=line)

        return jsonify({"status": "ok", "msg": "Datos guardados"}), 200

    except Exception as e:
        print("🔥 ERROR EN /sensordata:", str(e))
        return jsonify({"status": "error", "msg": str(e)}), 500



@app.route("/", methods=["GET"])
def home():
    return "Servidor funcionando", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
