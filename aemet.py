
import streamlit as st
import requests
from datetime import datetime, timedelta

# Coordenadas del aeropuerto GCLP
aeropuertos = {
    "GCLP - Gran Canaria": {"lat": 27.9319, "lon": -15.3866}
}

# CLAVE API FIJA COMO STRING
api_key = "VM0G7IbYRsyppjgGdnhkaIQIhSjuNr5i"

# Función para consultar datos desde Windy API (solo parámetros compatibles)
def obtener_datos_windy(lat, lon, api_key):
    url = "https://api.windy.com/api/point-forecast/v2"
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }
    payload = {
        "lat": lat,
        "lon": lon,
        "model": "gfs",
        "parameters": ["wind", "temp", "precip"],
        "levels": ["surface"]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error Windy API: {response.status_code}")
        try:
            st.json(response.json())
        except:
            st.text(response.text)
        return None

# Función para mostrar la tabla
def mostrar_tabla_html(data):
    html = f""" 
    <style>
        .weather-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
            margin-top: 20px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .weather-table th {{
            background-color: #007acc;
            color: white;
            padding: 14px;
        }}
        .weather-table td {{
            background-color: #ffffff;
            padding: 14px;
            font-size: 16px;
        }}
        .footer {{
            margin-top: 10px;
            font-style: italic;
            text-align: center;
            color: #555;
            font-size: 14px;
        }}
    </style>

    <table class="weather-table">
        <tr>
            <th>💨 Viento</th>
            <th>🌧️ Lluvia</th>
            <th>🌡️ Temperatura</th>
        </tr>
        <tr>
            <td>{data['viento']}</td>
            <td>{data['lluvia']}</td>
            <td>{data['temperatura']}</td>
        </tr>
    </table>
    <div class="footer">🔎 Fuente: Windy API</div>
    """
    st.markdown(html, unsafe_allow_html=True)

# Streamlit UI
st.title("🌤️ Consulta Meteorológica para Aeropuertos")

aeropuerto = st.selectbox("Selecciona un aeropuerto", list(aeropuertos.keys()))
dia = st.date_input("Selecciona el día", min_value=datetime.today(), max_value=datetime.today() + timedelta(days=3))

if st.button("Consultar"):
    coords = aeropuertos[aeropuerto]
    datos = obtener_datos_windy(coords["lat"], coords["lon"], api_key)

    if datos and "wind" in datos["forecast"]:
        idx = 0  # índice simple (puede ajustarse para precisión por hora)
        viento = datos["forecast"]["wind"]["surface"]["u"]["values"][idx]
        temperatura = datos["forecast"]["temp"]["surface"]["values"][idx]
        lluvia = datos["forecast"]["precip"]["surface"]["values"][idx]

        info = {
            "viento": f"{int(viento)} km/h",
            "lluvia": "Sí" if lluvia > 0 else "No",
            "temperatura": f"{temperatura:.1f}°C"
        }
        mostrar_tabla_html(info)
    else:
        st.error("No se pudieron obtener los datos de Windy.")
