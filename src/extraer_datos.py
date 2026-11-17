"""
extraer_datos.py
----------------
Extrae la tabla de posiciones de pilotos de una temporada de Fórmula 1 desde la
API pública Ergast / Jolpica (sin API key), la transforma a una estructura limpia
y la persiste en data_extracted.json y data_extracted.csv.

Buenas prácticas aplicadas:
  - Configuración vía variables de entorno (.env) con python-dotenv. No hay
    credenciales hardcodeadas; si la API requiriera una API Key, se toma de .env.
  - Manejo de errores HTTP (404, 500, timeouts, problemas de conexión).
  - Transformación: se aplana el JSON anidado y se conservan solo los campos útiles.

Uso:
    python extraer_datos.py
"""
import os
import sys
import csv
import json

import requests
from dotenv import load_dotenv

# --- 1. Configuración desde variables de entorno (.env) ---
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.jolpi.ca/ergast/f1")
SEASON = os.getenv("SEASON", "2024")
API_KEY = os.getenv("API_KEY")  # No es necesaria para esta API; el mecanismo queda listo.

TIMEOUT = 20  # segundos


def construir_url() -> str:
    """Arma el endpoint de la tabla de posiciones de pilotos para la temporada."""
    return f"{API_BASE_URL}/{SEASON}/driverStandings.json"


def extraer(url: str) -> dict:
    """
    Realiza la petición GET y devuelve el JSON crudo.
    Maneja errores de red y códigos de estado HTTP sin romper el script.
    """
    headers = {}
    if API_KEY:  # Si existiera una API Key, se envía en el header (nunca hardcodeada).
        headers["Authorization"] = f"Bearer {API_KEY}"

    try:
        respuesta = requests.get(url, headers=headers, timeout=TIMEOUT)
        respuesta.raise_for_status()  # Lanza excepción para 4xx y 5xx
    except requests.exceptions.HTTPError as e:
        codigo = e.response.status_code if e.response is not None else "desconocido"
        print(f"[ERROR] La API respondió con un código HTTP {codigo}.")
        if codigo == 404:
            print("        Verificá la temporada solicitada (variable SEASON en .env).")
        elif codigo == 500:
            print("        Error interno del servidor; reintentá más tarde.")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"[ERROR] La API no respondió en {TIMEOUT} segundos (timeout).")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se pudo conectar con la API. ¿Hay conexión a internet / la API está caída?")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Falló la petición: {e}")
        sys.exit(1)

    try:
        return respuesta.json()
    except ValueError:
        print("[ERROR] La respuesta no es un JSON válido.")
        sys.exit(1)


def transformar(data: dict) -> list[dict]:
    """
    Aplana el JSON anidado de Ergast y conserva solo los campos relevantes.
    Estructura de origen:
      MRData -> StandingsTable -> StandingsLists[0] -> DriverStandings[]
    """
    try:
        listas = data["MRData"]["StandingsTable"]["StandingsLists"]
    except (KeyError, TypeError):
        print("[ERROR] El JSON no tiene la estructura esperada.")
        sys.exit(1)

    if not listas:
        print("[AVISO] No hay datos de posiciones para la temporada solicitada.")
        return []

    standings = listas[0]["DriverStandings"]
    limpios = []
    for item in standings:
        piloto = item["Driver"]
        equipo = item["Constructors"][0]["name"] if item.get("Constructors") else None
        limpios.append({
            "posicion": int(item["position"]),
            "piloto": f"{piloto['givenName']} {piloto['familyName']}",
            "nacionalidad": piloto["nationality"],
            "equipo": equipo,
            "puntos": float(item["points"]),
            "victorias": int(item["wins"]),
        })
    return limpios


def guardar(registros: list[dict], base_dir: str) -> None:
    """Persiste los datos limpios en JSON y CSV en la raíz del repositorio."""
    ruta_json = os.path.join(base_dir, "data_extracted.json")
    ruta_csv = os.path.join(base_dir, "data_extracted.csv")

    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)

    if registros:
        with open(ruta_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(registros[0].keys()))
            writer.writeheader()
            writer.writerows(registros)

    print(f"[OK] Guardados {len(registros)} registros en:")
    print(f"     - {ruta_json}")
    print(f"     - {ruta_csv}")


def main():
    # La salida se guarda en la raíz del repo (un nivel arriba de /src)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    url = construir_url()
    print(f"[INFO] Consultando: {url}")
    data = extraer(url)
    registros = transformar(data)
    guardar(registros, base_dir)


if __name__ == "__main__":
    main()
