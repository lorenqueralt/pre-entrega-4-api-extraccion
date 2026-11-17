# Pre-entrega · Extracción y Almacenamiento Seguro de Datos vía API

**Curso:** Data Science II — Coderhouse

Script en Python que consume una **API pública de Fórmula 1** (Ergast / Jolpica), procesa
la respuesta JSON y la persiste en archivos estructurados (JSON y CSV), aplicando buenas
prácticas de seguridad (variables de entorno) y manejo de errores.

## Qué hace

Extrae la **tabla de posiciones de pilotos** de una temporada de F1, aplana el JSON
anidado y guarda una versión limpia con los campos relevantes: posición, piloto,
nacionalidad, equipo, puntos y victorias.

## Fuente de datos

API Ergast (vía el mirror mantenido **Jolpica**), de uso público y **sin API Key**:

- Endpoint: `https://api.jolpi.ca/ergast/f1/{temporada}/driverStandings.json`
- Ejemplo: https://api.jolpi.ca/ergast/f1/2024/driverStandings.json

## Estructura del repositorio

```
preentrega4-api-extraccion/
├── src/
│   └── extraer_datos.py     # script de extracción
├── data_extracted.json      # salida (JSON)
├── data_extracted.csv       # salida (CSV)
├── .env.example             # plantilla de configuración (sin secretos)
├── .gitignore               # ignora .env, __pycache__, venv
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.9+

## Instalación

```bash
# 1. (opcional) entorno virtual
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. dependencias
pip install -r requirements.txt

# 3. configuración: copiar la plantilla y ajustar si hace falta
cp .env.example .env              # Windows: copy .env.example .env
```

El archivo `.env` define:

| Variable       | Descripción                                   | Default                          |
|----------------|-----------------------------------------------|----------------------------------|
| `API_BASE_URL` | URL base de la API                            | `https://api.jolpi.ca/ergast/f1` |
| `SEASON`       | Temporada a consultar                         | `2024`                           |
| `API_KEY`      | Clave de API (esta API no la requiere; vacía) | *(vacío)*                        |

## Ejecución

```bash
python src/extraer_datos.py
```

Genera/actualiza `data_extracted.json` y `data_extracted.csv` en la raíz del repo.

## Seguridad y manejo de errores

- **Sin hardcoding:** ninguna credencial está escrita en el código; la configuración y
  cualquier eventual API Key se leen desde `.env` con `python-dotenv`.
- **`.env` fuera del control de versiones:** está listado en `.gitignore`; se versiona
  solo `.env.example`.
- **Manejo de errores:** el script captura timeouts, errores de conexión y códigos HTTP
  (incluidos **404** y **500**) con mensajes claros, y valida que la respuesta sea un JSON
  con la estructura esperada. Ante un fallo, termina de forma controlada en lugar de
  romperse con un traceback.

## Librerías

| Librería       | Uso                                  |
|----------------|--------------------------------------|
| requests       | peticiones HTTP GET a la API         |
| python-dotenv  | carga de variables de entorno        |
