from flask import Flask, request, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Archivo donde se almacenarán los datos
archivo_excel = "datos_sensores.xlsx"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        urls = request.form.getlist("urls")  # Capturar las URLs ingresadas

        if not urls:
            return render_template("index.html", mensaje="⚠️ Debes ingresar al menos una URL.")

        fecha_inicio = datetime.now()
        data_frames = []
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)  # Agregar tiempo de espera

                if response.status_code == 200:
                    json_data = response.json()
                    timestamps = json_data['data']['aHistoryPressure']['timestamp']
                    values = json_data['data']['aHistoryPressure']['values']
                    fechas = [fecha_inicio + timedelta(seconds=ts) for ts in timestamps]

                    df = pd.DataFrame({'FechaHora': fechas, 'Presión (bar)': values})
                    df['FechaHora'] = pd.to_datetime(df['FechaHora'])
                    data_frames.append(df)

                else:
                    return render_template("index.html", mensaje=f"⚠️ Error con {url}: {response.status_code}")

            except requests.exceptions.RequestException as e:
                return render_template("index.html", mensaje=f"❌ No se pudo obtener datos de {url}. Verifica la conexión.")

        # Guardar datos en Excel
        with pd.ExcelWriter(archivo_excel, mode="w") as writer:
            for i, df in enumerate(data_frames):
                df.to_excel(writer, sheet_name=f"Sensor_{i+1}", index=False)

        # Generar gráfica
        plt.figure(figsize=(12, 6))
        for df in data_frames:
            plt.plot(df["FechaHora"], df["Presión (bar)"], marker='o', linestyle='-')

        plt.title("Presión de Sensores Sick")
        plt.xlabel("Hora")
        plt.ylabel("Presión (bar)")
        plt.grid(True)
        plt.xticks(rotation=45)

        archivo_imagen = "static/grafica.png"
        plt.savefig(archivo_imagen)
        plt.close()

        return render_template("index.html", imagen=archivo_imagen, excel=archivo_excel, mensaje="✅ Gráfica generada correctamente.")

    return render_template("index.html")

@app.route("/descargar")
def descargar():
    return send_file(archivo_excel, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # Modificado a puerto 8080 y host abierto