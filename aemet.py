import streamlit as st
import requests
import datetime
import pandas as pd

# Coordenadas de los aeropuertos
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
BASE_URL = "https://my.meteoblue.com/packages/basic-1h_basic-day_clouds-1h_clouds-day"

# Configuración visual
st.set_page_config(page_title="Meteo Aeropuertos Canarias", layout="centered")
st.title("🌦️ Consulta meteorológica - Aeropuertos de Canarias")

# UI
aeropuerto = st.selectbox("✈️ Selecciona un aeropuerto", list(aeropuertos.keys()))
fecha = st.date_input(
    "📅 Selecciona una fecha (máx. 3 días vista)",
    min_value=datetime.date.today(),
    max_value=datetime.date.today() + datetime.timedelta(days=3)
)
consultar = st.button("🔍 Consultar")

# Función para convertir pictocode a emoji
def pictocode_to_emoji(code):
    if code == 1:
        return "☀️"
    elif code == 2:
        return "🌤️"
    elif code in [3, 4]:
        return "☁️"
    elif code in [5, 6]:
        return "🌧️"
    else:
        return "⛈️"

if consultar:
    lat, lon = aeropuertos[aeropuerto]
    url = f"{BASE_URL}?lat={lat}&lon={lon}&apikey={API_KEY}&format=json"

    response = requests.get(url)
    if response.status_code == 200:
        response_json = response.json()

        if "data_day" in response_json:
            data = response_json["data_day"]

            # Campo seguro
            def get_field(name, default=0):
                return data[name] if name in data else [default] * len(data["time"])

            df = pd.DataFrame({
                "Fecha": data["time"],
                "🌡️ Máx (°C)": data["temperature_max"],
                "🌡️ Mín (°C)": data["temperature_min"],
                "🌬️ Viento medio (kt)": [round(v * 1.94384, 1) for v in data["windspeed_mean"]],
                "🧭 Dirección (°)": get_field("winddirection"),
                "☁️ Nubosidad (%)": get_field("cloudcover"),
                "☁️ Techo nubes (m)": get_field("cloudbase_mean"),
                "🌧️ Precipitación (mm)": data["precipitation"],
                "💧 Humedad (%)": data["relativehumidity_mean"],
                "🌂 Prob. lluvia (%)": data["precipitation_probability"],
                "Icono": [pictocode_to_emoji(c) for c in get_field("pictocode")]
            })

            df = df[df["Fecha"] == fecha.strftime("%Y-%m-%d")]

            if df.empty:
                st.warning("⚠️ No hay datos para la fecha seleccionada.")
            else:
                # Añadir alerta visual
                def alerta(temp):
                    if temp >= 30:
                        return "🔴"
                    elif temp >= 25:
                        return "🟡"
                    else:
                        return "🟢"

                df["🚨 Alerta"] = df["🌡️ Máx (°C)"].apply(alerta)
                df["📡 Origen"] = "Meteoblue"

                # Mostrar tabla HTML
                st.markdown(
                    df.to_html(index=False, justify="center", escape=False),
                    unsafe_allow_html=True
                )
        else:
            st.error("❌ No se encontraron datos en 'data_day'.")
    else:
        st.error(f"❌ Error al contactar con la API: {response.status_code}")
