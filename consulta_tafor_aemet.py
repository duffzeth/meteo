
import streamlit as st
from datetime import datetime, timedelta

def extraer_datos_tafor(taf):
    import re

    visibilidad = "-"
    viento = "-"
    techo = "-"
    lluvia = "No"

    vis_match = re.search(r"\s(\d{4})\s", taf)
    if vis_match:
        vis_metros = int(vis_match.group(1))
        visibilidad = f"{vis_metros} m" if vis_metros < 9999 else "+10 km"

    viento_match = re.search(r"\s(\d{3})(\d{2})KT", taf)
    if viento_match:
        dir_viento = viento_match.group(1)
        vel_viento = viento_match.group(2)
        viento = f"{vel_viento} kt ({dir_viento}°)"

    techo_match = re.search(r"(BKN|OVC)(\d{3})", taf)
    if techo_match:
        altura_ft = int(techo_match.group(2)) * 100
        techo = f"{altura_ft} ft"

    if "RA" in taf or "SHRA" in taf:
        lluvia = "Sí"

    return visibilidad, techo, viento, lluvia


import requests
from bs4 import BeautifulSoup

def obtener_tafor_ogimet(icao):
    url = f"https://ogimet.com/display_metars2.php?lang=en&lugar={icao}&tipo=TAF&ord=REV&nil=NO&fmt=raw"
    response = requests.get(url)
    if response.status_code != 200:
        return f"❌ Error accediendo a OGIMET: {response.status_code}"
    soup = BeautifulSoup(response.text, "html.parser")
    pre_tag = soup.find("pre")
    return pre_tag.text.strip() if pre_tag else "⚠️ No se encontró mensaje TAFOR."


st.set_page_config(page_title="Consulta Meteorológica", layout="centered")
st.title("🌤️ Consulta Meteorológica - Inicio")
hora_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f"**Fecha y hora actual (Zulu):** {hora_utc}")

dias_validos = [(datetime.utcnow() + timedelta(days=i)).strftime("%A") for i in range(4)]
dias_trad = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}
dias_disponibles = [dias_trad[d] for d in dias_validos]

regiones = ["", "Canarias", "Península", "África", "Funchal", "Madrid"]
region = st.selectbox("Selecciona la región", regiones)
dia = st.selectbox("Selecciona el día de la semana", [""] + dias_disponibles)

aeropuertos_fijos = {
    "Madrid": ["LEMD"],
    "Funchal": ["LPMA", "LPPS", "LPPD"],
    "Canarias": ["GCLP", "GCXO", "GCTS", "GCFV", "GCRR", "GCLA", "GCHI", "GCFM"]
}
franjas_estandar = ["06H00", "10H00", "14H00", "18H00", "22H00"]

datos_embebidos = {
    "África": {
        "Lunes": [("GMMH", "06H00"), ("GQNN", "10H00")],
        "Martes": [("GOBD", "06H00")],
        "Miércoles": [("GMMX", "08H00")],
        "Jueves": [("GMML", "09H00")],
        "Viernes": [("GMMX", "08H00"), ("GMAG", "12H00")],
        "Sábado": [("GMMH", "06H00")],
        "Domingo": [("GMMH", "06H00")]
    },
    "Península": {
        "Lunes": [("LEAS", "06H00"), ("LEBZ", "10H00")],
        "Martes": [("LEMI", "08H00")],
        "Miércoles": [("LEBA", "09H00")],
        "Jueves": [("LEGR", "10H00"), ("LEXJ", "12H00")],
        "Viernes": [("LEJR", "08H00"), ("LECO", "14H00")],
        "Sábado": [("LEPA", "06H00")],
        "Domingo": [("LEVC", "06H00")]
    }
}

def mostrar_tabla_html(aeropuerto, horas):
    st.markdown(f"<h4 style='margin-top: 2rem;'>✈️ {aeropuerto}</h4>", unsafe_allow_html=True)
    html = """
    <style>
        table.custom-table {
            width: 100%;
            border-collapse: collapse;
            background-color: transparent;
            color: white;
            text-align: center;
        }
        .custom-table th, .custom-table td {
            border: 1px solid #555;
            padding: 8px;
        }
        .custom-table th {
            background-color: #222;
        }
    </style>
    <table class='custom-table'>
        <thead>
            <tr>
                <th>Hora</th>
                <th>Visibilidad</th>
                <th>Techo de nubes</th>
                <th>Dirección</th>
                <th>Viento</th>
                <th>Lluvia</th>
                <th>Temperatura</th>
                <th>Alerta</th>
            </tr>
        </thead>
        <tbody>
    """
    datos_prueba = {
        "06H00": ("10 km", "5000 ft", "045°", "15 kt", "No", "21°C", "🟢"),
        "10H00": ("12 km", "6000 ft", "090°", "18 kt", "No", "24°C", "🟢"),
        "14H00": ("15 km", "7000 ft", "135°", "20 kt", "No", "26°C", "🟢"),
        "18H00": ("12 km", "5000 ft", "180°", "17 kt", "No", "22°C", "🟢"),
        "22H00": ("8 km", "4000 ft", "225°", "12 kt", "No", "19°C", "🟢")
    }
    for hora in horas:
        vis, techo, dir_viento, viento, lluvia, temp, alerta = datos_prueba.get(hora, ("-", "-", "-", "-", "-", "-", "🟢"))
        html += f"<tr><td>{hora}</td><td>{vis}</td><td>{techo}</td><td>{dir_viento}</td><td>{viento}</td><td>{lluvia}</td><td>{temp}</td><td>{alerta}</td></tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


# Mostrar TAFOR si dentro de 24h
dias_nombre = {
    "Lunes": 0, "Martes": 1, "Miércoles": 2,
    "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6
}
hoy = datetime.utcnow()
hoy_idx = hoy.weekday()
dia_idx = dias_nombre[dia]
delta_dias = (dia_idx - hoy_idx) % 7
fecha_base = hoy + timedelta(days=delta_dias)


def mostrar_tafor_si_corresponde(icao, horas):
    datos_tafor = {}
    for hora_str in horas:
        hora = int(hora_str[:2])
        fecha_consulta = fecha_base.replace(hour=hora, minute=0, second=0, microsecond=0)
        if fecha_consulta <= (datetime.utcnow() + timedelta(hours=24)):
            st.markdown(f"### 🛫 TAFOR {icao} - {hora_str}")
            tafor = obtener_tafor_ogimet(icao)
            st.code(tafor, language='text')
            vis, techo, viento, lluvia = extraer_datos_tafor(tafor)
            datos_tafor[hora_str] = {
                'vis': vis,
                'techo': techo,
                'viento': viento,
                'lluvia': lluvia,
                'temp': '-',
                'alerta': '🟢',
                'fuente': 'OGIMET/TAFOR'
            }
    return datos_tafor

    for hora_str in horas:
        hora = int(hora_str[:2])
        fecha_consulta = fecha_base.replace(hour=hora, minute=0, second=0, microsecond=0)
        if fecha_consulta <= (datetime.utcnow() + timedelta(hours=24)):
            st.markdown(f"### 🛫 TAFOR {icao} - {hora_str}")
            tafor = obtener_tafor_ogimet(icao)
            st.code(tafor, language='text')
            break

if region and dia:
    st.markdown("## Resultados")
    if region in ["Madrid", "Funchal", "Canarias"]:
        for aeropuerto in aeropuertos_fijos[region]:
            mostrar_tafor_si_corresponde(aeropuerto, franjas_estandar)
            mostrar_tabla_html(aeropuerto, franjas_estandar)
    elif region in ["África", "Península"]:
        lista = datos_embebidos.get(region, {}).get(dia, [])
        tabla_agrupada = {}
        for aeropuerto, hora in lista:
            tabla_agrupada.setdefault(aeropuerto, []).append(hora)

        st.markdown(f"<h4 style='margin-top: 2rem;'>✈️ Aeropuertos programados para {region}</h4>", unsafe_allow_html=True)
        html = """
        <style>
            table.custom-table {
                width: 100%;
                border-collapse: collapse;
                background-color: transparent;
                color: white;
                text-align: center;
            }
            .custom-table th, .custom-table td {
                border: 1px solid #555;
                padding: 8px;
            }
            .custom-table th {
                background-color: #222;
            }
        </style>
        <table class='custom-table'>
            <thead>
                <tr>
                    <th>Aeropuerto</th>
                    <th>Hora</th>
                    <th>Visibilidad</th>
                    <th>Techo de nubes</th>
                    <th>Dirección</th>
                    <th>Viento</th>
                    <th>Lluvia</th>
                    <th>Temperatura</th>
                    <th>Alerta</th>
                </tr>
            </thead>
            <tbody>
        """
        for aeropuerto, horas in tabla_agrupada.items():
            mostrar_tafor_si_corresponde(aeropuerto, horas)
            for hora in horas:
                vis, techo, dir_viento, viento, lluvia, temp, alerta = datos_prueba.get(hora, ("-", "-", "-", "-", "-", "-", "🟢"))
                html += f"<tr><td>{aeropuerto}</td><td>{hora}</td><td>{vis}</td><td>{techo}</td><td>{dir_viento}</td><td>{viento}</td><td>{lluvia}</td><td>{temp}</td><td>{alerta}</td></tr>"
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)

# Botón y firma
st.markdown("<div style='position: fixed; bottom: 10px; left: 20px;'>"
            "<form action='.' method='get'>"
            "<button style='background-color:#444;padding:6px 12px;border:none;border-radius:5px;color:white;'>🔄 Volver al inicio</button>"
            "</form></div>", unsafe_allow_html=True)
st.markdown("<div style='position: fixed; bottom: 10px; right: 20px; color: gray;'>by ludovick v0.1</div>", unsafe_allow_html=True)
