
from datetime import datetime, timedelta

# Franja horaria seleccionada por el usuario
dia_seleccionado = "Lunes"
franja_seleccionada = "10H00"
region = "Canarias"

# Simulación del día seleccionado (hoy es domingo, por ejemplo)
dias_nombre = {
    "Lunes": 0, "Martes": 1, "Miércoles": 2,
    "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6
}
hoy = datetime.utcnow()
hoy_nombre = hoy.strftime("%A")
hoy_num = dias_nombre.get(hoy_nombre, hoy.weekday())

dia_consulta_idx = dias_nombre[dia_seleccionado]
delta_dias = (dia_consulta_idx - hoy_num) % 7
fecha_objetivo = hoy + timedelta(days=delta_dias)

# Convertir franja horaria tipo "10H00" a hora UTC
hora_objetivo = int(franja_seleccionada[:2])
fecha_hora_objetivo = fecha_objetivo.replace(hour=hora_objetivo, minute=0, second=0, microsecond=0)

# Comparar si está dentro de las próximas 24 horas
es_menor_24h = fecha_hora_objetivo <= (datetime.utcnow() + timedelta(hours=24))

if es_menor_24h:
    fuente = "TAFOR"
else:
    fuente = "AEMET/WINDY"

print(f"Consulta para: {fecha_hora_objetivo} UTC")
print(f"Fuente seleccionada: {fuente}")
