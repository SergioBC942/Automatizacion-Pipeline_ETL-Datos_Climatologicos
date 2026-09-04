#Librerías
import pandas as pd

#Columnas esperadas
columnas = [
    "ciudad",
    "fecha_hora",
    "temperatura",
    "humedad",
    "precipitacion",
    "velocidad_viento"
]

#Función para convertir los datos a un DataFrame
def transformar_datos(registros):

    #En caso de que no haya registros disponibles, 
    if not registros:
        raise ValueError(
            "No hay registros disponibles."
        )
    
    #Creación del DF
    df = pd.DataFrame(registros)
    
    #Si en la API llegaran a cambiar las columnas, esta parte nos dice exactamente qué columnas faltarían
    columnas_faltantes = set(columnas) - set(df.columns)
    if columnas_faltantes:
        raise ValueError(
            f"Faltan columnas: {columnas_faltantes}"
        )

    #Conversión de la fecha y hora al tipo to_datetime
    df["fecha_hora"] = pd.to_datetime(
        df["fecha_hora"]
    )

    #Obtención del DF
    return df