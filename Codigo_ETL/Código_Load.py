#Librerías
import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv


#Rutas de los archivos
ruta_proyecto = Path(__file__).resolve().parent
ruta_env = ruta_proyecto / ".env"

#Cargando el archivo.env 
load_dotenv(ruta_env)

#Ruta del string de conexión a NEON (PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")

#Si no está la URL
if not DATABASE_URL:
    raise ValueError(
        "No se encontró DATABASE_URL en el archivo .env"
    )


#Función para almacenar los archivos en PostgreSQL
def guardar_datos_postgres(df):

#Si no hay registros en el DF, retorna 0
    if df.empty:
        return 0

#Uso de la conexión con la BD
    with psycopg.connect(DATABASE_URL) as conexion:
        with conexion.cursor() as cursor:

            #Crear tabla si todavía no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clima (
                    ciudad TEXT NOT NULL,
                    fecha_hora TIMESTAMP NOT NULL,
                    temperatura REAL,
                    humedad REAL,
                    precipitacion REAL,
                    velocidad_viento REAL,
                    PRIMARY KEY (ciudad, fecha_hora)
                );
            """)

            #Preparar registros
            registros = []
            for fila in df.itertuples(index=False):
                registros.append(
                    (
                        fila.ciudad,
                        fila.fecha_hora.to_pydatetime(),
                        fila.temperatura,
                        fila.humedad,
                        fila.precipitacion,
                        fila.velocidad_viento
                    )
                )

            #Insertar registros
            cursor.executemany("""
                INSERT INTO clima (
                    ciudad,
                    fecha_hora,
                    temperatura,
                    humedad,
                    precipitacion,
                    velocidad_viento
                )
                VALUES (%s, %s, %s, %s, %s, %s)

                ON CONFLICT (ciudad, fecha_hora)
                DO NOTHING;
            """, registros)
            registros_insertados = cursor.rowcount
        conexion.commit()

    return registros_insertados
