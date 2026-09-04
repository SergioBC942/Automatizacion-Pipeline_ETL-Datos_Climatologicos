#Librerías
import requests

#Endpoint
URL = "https://api.open-meteo.com/v1/forecast"


#Ciudades
ciudades = [
    {
        "ciudad": "Ciudad de México",
        "latitud": 19.4326,
        "longitud": -99.1332
    },
    {
        "ciudad": "Monterrey",
        "latitud": 25.6866,
        "longitud": -100.3161
    },
    {
        "ciudad": "Guadalajara",
        "latitud": 20.6597,
        "longitud": -103.3496
    },
    {
        "ciudad": "Cancún",
        "latitud": 21.1619,
        "longitud": -86.8515
    },
    {
        "ciudad": "Puebla",
        "latitud": 19.0477,
        "longitud": -98.2072
    }
]

#Función para obtener los datos climáticos
def obtener_clima(ciudad, latitud, longitud):

    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "timezone": "America/Mexico_City"
    }

    try:
        response = requests.get(
            URL,
            params=parametros,
            timeout=10
        )
        response.raise_for_status()
        
        #Si la conexión es exitosa almacena los datos
        datos = response.json()
        registro = {
            "ciudad": ciudad,
            "fecha_hora": datos["current"]["time"],
            "temperatura": datos["current"]["temperature_2m"],
            "humedad": datos["current"]["relative_humidity_2m"],
            "precipitacion": datos["current"]["precipitation"],
            "velocidad_viento": datos["current"]["wind_speed_10m"]
        }
        return registro

    #Si la conexión no es exitosa
    except requests.exceptions.RequestException as error:
        print(f"Error al consultar {ciudad}: {error}")
        return None

#Función para extraer las ciudades
def extraer_datos():

    registros = []

    for ciudad in ciudades:
        print(f"Consultando {ciudad['ciudad']}...")
        registro = obtener_clima(
            ciudad["ciudad"],
            ciudad["latitud"],
            ciudad["longitud"]
        )

        if registro is not None:
            registros.append(registro)

    return registros
