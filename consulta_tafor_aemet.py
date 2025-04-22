import streamlit as st
import requests
import datetime
import pandas as pd

# === Configuración de aeropuertos ===
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

# === Configuración visual ===
st.set_page_config(page_title="Meteo Aeropuertos Canarias", layout="centered")
st.title("🌦️ Consulta meteorológica - Aeropuertos de Canarias")

aeropuerto = st.selectbox("✈️ Selecciona un aeropuerto", list(aeropuertos.keys()))
fecha = st.date_input(
    "📅 Selecciona una fecha (máximo 3 días vista)",
    min_value=datetime.date.today(),
    max_value=datetime.date.today() + datetime.timedelta(days=3)
)
consultar = st.button("🔍 Consultar")

# === Función para icono climático ===
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

# === Consultar API ===
if consultar:
    lat, lon = aeropuertos[aeropuerto]
    url = (
        f"{BASE_URL}?lat={lat}&lon={lon}"
        f"&apikey={API_KEY}&format=json"
        f"&windspeed=kn&winddirection=degree"
        f"&visibility=m"
    )

    st.write("URL:", url)
    response = requests.get(url)
    if response.status_code == 200:
        response_json = response.json()

        if "data_day" in response_json and "data_1h" in response_json:
            data_day = response_json["data_day"]
            data_1h = response_json["data_1h"]
            fecha_str = fecha.strftime("%Y-%m-%d")

            # Extraer dirección de viento a las 12:00 UTC del día seleccionado
            df_hourly = pd.DataFrame({
                "FechaHora": pd.to_datetime(data_1h["time"]),
                "winddirection": data_1h.get("winddirection", [None]*len(data_1h["time"]))
            })
            winddir = df_hourly[df_hourly["FechaHora"].dt.strftime("%Y-%m-%d %H:%M") == f"{fecha_str} 12:00"]
            direccion_viento = winddir["winddirection"].values[0] if not winddir.empty else "N/D"

            # Crear DataFrame diario
            df = pd.DataFrame({
                "Fecha": data_day["time"],
                "🌡️ Máx (°C)": data_day["temperature_max"],
                "🌡️ Mín (°C)": data_day["temperature_min"],
                "🌬️ Viento medio (kt)": data_day["windspeed_mean"],  # ya en kt por parámetro
                "🧭 Dirección (°)": [direccion_viento if t == fecha_str else "—" for t in data_day["time"]],
                "☁️ Nubosidad (%)": data_day.get("cloudcover", ["—"] * len(data_day["time"])),
                "☁️ Techo nubes (m)": data_day.get("cloudbase_mean", ["—"] * len(data_day["time"])),
                "🌧️ Precipitación (mm)": data_day["precipitation"],
                "👁️ Visibilidad (m)": data_day["visibility_mean"],
                #"👁️ Visibilidad (m)": data_day.get("visibility", ["—"] * len(data_day["time"])),
                "💧 Humedad (%)": data_day["relativehumidity_mean"],
                "🌂 Prob. lluvia (%)": data_day["precipitation_probability"],
                "Icono": [pictocode_to_emoji(c) for c in data_day["pictocode"]],
            })

            # Filtrar solo el día elegido
            df = df[df["Fecha"] == fecha_str]

            if df.empty:
                st.warning("⚠️ No hay datos para la fecha seleccionada.")
            else:
                def alerta(temp):
                    if temp >= 30:
                        return "🔴"
                    elif temp >= 25:
                        return "🟡"
                    else:
                        return "🟢"

                df["🚨 Alerta"] = df["🌡️ Máx (°C)"].apply(alerta)
                df["📡 Origen"] = "Meteoblue"

                st.markdown(
                    df.to_html(index=False, justify="center", escape=False),
                    unsafe_allow_html=True
                )
        else:
            st.error("❌ La respuesta no contiene los datos esperados ('data_day' y 'data_1h').")
    else:
        st.error(f"❌ Error al contactar con la API: {response.status_code}")
