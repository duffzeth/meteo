import streamlit as st
import requests
import datetime
import pandas as pd

# Configuración de aeropuertos
aeropuertos = {
    "GCLP - Gran Canaria": (27.9319, -15.3866),
    "GCXO - Tenerife Norte": (28.4827, -16.3415),
    "GCFV - Fuerteventura": (28.4527, -13.8638),
    "GCRR - Lanzarote": (28.9455, -13.6052),
    "GCLA - La Palma": (28.6265, -17.7556),
    "GCHI - El Hierro": (27.8148, -17.8871),
    "GCGM - La Gomera": (28.0296, -17.2146),
}

API_KEY = "Gqtw5BUEcQDIk4eb"
BASE_URL = "https://my.meteoblue.com/packages/basic-day"

# Streamlit UI
st.set_page_config(page_title="Meteo Aeropuertos Canarias", layout="centered")
st.title("🌦️ Consulta meteorológica - Aeropuertos de Canarias")

aeropuerto = st.selectbox("Selecciona un aeropuerto", list(aeropuertos.keys()))
fecha = st.date_input("Selecciona una fecha (máximo 3 días vista)", min_value=datetime.date.today(), max_value=datetime.date.today() + datetime.timedelta(days=3))
consultar = st.button("Consultar")

if consultar:
    lat, lon = aeropuertos[aeropuerto]
    url = f"{BASE_URL}?lat={lat}&lon={lon}&apikey={API_KEY}&format=json"
    
    st.write("URL:", url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["data_day"]

        # Procesar datos por fecha seleccionada
        df = pd.DataFrame({
            "FechaHora": data["time"],
            "Temperatura (°C)": data["temperature"],
            "Viento (km/h)": data["windspeed"],
            "Humedad (%)": data.get("relativehumidity", [None]*len(data["temperature"])),
            "Nubosidad (%)": data.get("cloudcover", [None]*len(data["temperature"]))
        })

        df["FechaHora"] = pd.to_datetime(df["FechaHora"])
        df = df[df["FechaHora"].dt.date == fecha]

        # Agregar columna alerta
        def alerta_color(temp):
            if temp >= 30:
                return "🔴"
            elif temp >= 25:
                return "🟡"
            else:
                return "🟢"

        df["Alerta"] = df["Temperatura (°C)"].apply(alerta_color)
        df["Origen"] = "Meteoblue"

        # Mostrar tabla bonita en HTML
        st.markdown(
            df.to_html(index=False, justify="center", escape=False), 
            unsafe_allow_html=True
        )

    else:
        st.error(f"Error al obtener datos: {response.status_code}")
