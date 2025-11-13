from flask import Flask
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os

app = Flask(__name__)

# -----------------------------
# Cargar variables de entorno
# -----------------------------
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

# Cliente Influx
client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)

@app.route("/")
def home():
    return "Servidor minimal InfluxDB activo."

# -----------------------------
# Ruta para enviar un solo valor
# -----------------------------
@app.route("/simple")
def send_simple():
    try:
        point = Point("prueba_minima").field("valor", 100)
        write_api.write(bucket=INFLUX_BUCKET, record=point)
        return "Dato enviado a InfluxDB"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
