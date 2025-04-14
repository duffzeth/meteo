import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def fetch_tafor(airport="GCLP"):
    """
    Realiza la petición a la URL para obtener el mensaje TAF del aeropuerto.
    Se asume que existe un endpoint específico para cada aeropuerto.
    """
    url = f"https://metar-taf.com/taf/{airport}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error al obtener datos para {airport}: Status code {response.status_code}")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Se intenta buscar el TAF en un <pre> (o en su defecto, se busca cualquier texto que comience con "TAF")
    taf_element = soup.find("pre")
    if taf_element:
        taf_text = taf_element.get_text(strip=True)
    else:
        taf_candidates = soup.find_all(text=re.compile(r"^TAF\s+"))
        if taf_candidates:
            taf_text = taf_candidates[0].strip()
        else:
            print("No se encontró el TAF en la página")
            return None
    return taf_text

def parse_validity(taf_text):
    """
    Extrae el periodo de validez a partir del TAF.
    Se espera encontrar un grupo en formato ddhh/ddhh (por ejemplo, 0910/1012)
    """
    validity_regex = re.compile(r"\b(\d{4})/(\d{4})\b")
    match = validity_regex.search(taf_text)
    if not match:
        return None, None
    start_str, end_str = match.group(1), match.group(2)
    try:
        # Se utiliza la hora UTC actual para aproximar el mes/año
        now = datetime.utcnow()
        start_day = int(start_str[:2])
        start_hour = int(start_str[2:])
        end_day = int(end_str[:2])
        end_hour = int(end_str[2:])
        # Se construyen objetos datetime basados en el día y la hora extraídos
        start_date = now.replace(day=start_day, hour=start_hour, minute=0, second=0, microsecond=0)
        end_date = now.replace(day=end_day, hour=end_hour, minute=0, second=0, microsecond=0)
        # Ajuste simple para el cambio de mes (se asume que el TAF cubre pocos días)
        if start_date < now - timedelta(days=1):
            # Si el día de inicio ya pasó, se asume que es del mes siguiente
            next_month = (now.month % 12) + 1
            year = now.year + (1 if next_month == 1 else 0)
            start_date = start_date.replace(year=year, month=next_month)
        if end_date < now:
            next_month = (now.month % 12) + 1
            year = now.year + (1 if next_month == 1 else 0)
            end_date = end_date.replace(year=year, month=next_month)
        
        return start_date, end_date
    except Exception as e:
        print("Error al parsear la validez:", e)
        return None, None

def is_valid_tafor(taf_text):
    """
    Comprueba si el TAF:
      - Está en periodo de validez (la hora actual se encuentra entre inicio y fin)
      - El fin del periodo de validez no excede las 24 horas desde el momento actual
    """
    start_date, end_date = parse_validity(taf_text)
    if not start_date or not end_date:
        return False, "No se pudo determinar el periodo de validez."
    
    now = datetime.utcnow()
    if now < start_date or now > end_date:
        return False, "El TAF no está en periodo de validez actual."
    
    if end_date - now > timedelta(hours=24):
        return False, "El TAF supera las 24 horas a partir de la consulta."
    
    return True, (start_date, end_date)

def parse_taf_details(taf_text):
    """
    A partir del mensaje TAF extrae los siguientes detalles:
      - Visibilidad: se busca la palabra "CAVOK" o un número de 4 dígitos (en metros)
      - Techo de nubes: se busca patrones como BKNddd u OVCddd
      - Viento: se busca un token con 3 dígitos de dirección y 2 o 3 dígitos de velocidad seguido de "KT"
      - Lluvia: se busca la presencia de códigos comunes (RA, SHRA, DZ)
      - Temperatura: se busca el grupo temperatura/dewpoint (por ejemplo, 18/12 o M05/M10)
    """
    details = {}
    
    # Visibilidad
    if "CAVOK" in taf_text:
        details["visibilidad"] = "CAVOK"
    else:
        vis_match = re.search(r"\b(\d{4})\b", taf_text)
        details["visibilidad"] = vis_match.group(1) if vis_match else "No se encontró visibilidad"
    
    # Techo de nubes
    cc_match = re.search(r"\b(?:BKN|OVC)(\d{3})\b", taf_text)
    details["techo de nubes"] = cc_match.group(0) if cc_match else "No se encontró techo de nubes"
    
    # Viento (se espera un patrón de 5 o 6 caracteres, por ejemplo: 25010KT o 25010G15KT)
    wind_match = re.search(r"\b(\d{3}\d{2,3}(?:G\d{2})?KT)\b", taf_text)
    details["viento"] = wind_match.group(1) if wind_match else "No se encontró viento"
    
    # Lluvia (se buscan códigos comunes: RA, SHRA, DZ)
    rain_match = re.search(r"\b(SHRA|RA|DZ)\b", taf_text)
    details["lluvia"] = rain_match.group(1) if rain_match else "No se encontró lluvia"
    
    # Temperatura (buscamos el grupo temperatura/dewpoint, por ejemplo 18/12 o M05/M10)
    temp_match = re.search(r"\b(M?\d{2})/(M?\d{2})\b", taf_text)
    details["temperatura"] = temp_match.group(1) if temp_match else "No se encontró temperatura"
    
    return details

def main():
    airport = "GCLP"
    taf_text = fetch_tafor(airport)
    if not taf_text:
        return
    print("TAF obtenido:")
    print(taf_text)
    
    # Comprobación de la validez del TAF
    print("\nVerificando la validez del TAF...")
    valid, result = is_valid_tafor(taf_text)
    if not valid:
        print("El TAF no es válido:", result)
        return
    else:
        start_date, end_date = result
        print("Periodo de validez:", start_date, "hasta", end_date)
    
    # Extracción de parámetros
    print("\nExtrayendo detalles:")
    details = parse_taf_details(taf_text)
    for key, value in details.items():
        print(f"{key.capitalize()}: {value}")

if __name__ == "__main__":
    main()
