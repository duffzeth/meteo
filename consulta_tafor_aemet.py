
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import streamlit as st

def obtener_tafor_ogimet(icao):
    url = f"https://ogimet.com/display_metars2.php?lang=en&lugar={icao}&tipo=TAF&ord=REV&nil=NO&fmt=raw"
    response = requests.get(url)
    if response.status_code != 200:
        return f"❌ Error accediendo a OGIMET: {response.status_code}"
    soup = BeautifulSoup(response.text, "html.parser")
    pre_tag = soup.find("pre")
    return pre_tag.text.strip() if pre_tag else "⚠️ No se encontró mensaje TAFOR."

# === INTERFAZ DE USUARIO ===
st.title("Consulta Meteorológica - TAFOR desde OGIMET")

icao = st.selectbox("Selecciona aeropuerto (ICAO)", ["GCLP", "GCXO", "GCTS", "GCRR", "GCFV", "GCLA"])
dia = st.selectbox("Selecciona día de la semana", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
franja = st.selectbox("Selecciona franja horaria", ["06H00", "10H00", "14H00", "18H00", "22H00"])

# Calcular si la consulta es dentro de las próximas 24h
dias_nombre = {
    "Lunes": 0, "Martes": 1, "Miércoles": 2,
    "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6
}
hoy = datetime.utcnow()
hoy_idx = hoy.weekday()
consulta_idx = dias_nombre[dia]
delta_dias = (consulta_idx - hoy_idx) % 7
fecha_consulta = hoy + timedelta(days=delta_dias)
hora_obj = int(franja[:2])
fecha_hora_consulta = fecha_consulta.replace(hour=hora_obj, minute=0, second=0, microsecond=0)

st.markdown(f"📅 Consulta para: `{fecha_hora_consulta.strftime('%Y-%m-%d %H:%M')} UTC`")

if fecha_hora_consulta <= (datetime.utcnow() + timedelta(hours=24)):
    st.success("✅ Usando TAFOR (OGIMET) para esta franja horaria")
    tafor_texto = obtener_tafor_ogimet(icao)
    st.code(tafor_texto, language='text')
else:
    st.info("ℹ️ Consulta fuera de 24h. Aquí se usará AEMET/WINDY en la app principal.")
