#Librerías
import logging
from pathlib import Path

#Funciones a llamar del ETL
from Código_Extracción import extraer_datos
from Código_Transformación import transformar_datos
from Código_Load import guardar_datos_postgres


#Ruta del archivo de logs
ruta_logs = (
    Path(__file__).resolve().parent/"logs"
)

ruta_logs.mkdir(
    parents = True,
    exist_ok = True
)

#Configuración de la visualización de los logs
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(
            ruta_logs / "pipeline.log",
            encoding="utf-8"
        )
    ]
)

logger = logging.getLogger(__name__)


#Función para ejecutar el Pipeline ETL
def ejecutar_pipeline():
    logger.info("Pipeline iniciado")
    
    try:

        #Extrayendo los datos
        registros = extraer_datos()

        #Info en los logs
        logger.info(
            "Extracción completada: %s registros",
            len(registros)
        )


        #Transformación de los datos
        df = transformar_datos(registros)

        #Info de los logs
        logger.info(
            "Transformación completada: %s registros",
            len(df)
        )


        #Carga de datos (Load) a PostreSQL
        registros_insertados = guardar_datos_postgres(df)

        #Info en los logs
        logger.info(
            "Registros nuevos guardados en PostgreSQL: %s",
            registros_insertados
        )

        # Calcular duplicados ignorados
        duplicados = (len(df) - registros_insertados)

        #Si la cantidad de duplicados es mayor a 0
        if duplicados > 0:

            #En los logs se muestra cuántos registros fueron ignorados
            logger.warning(
                "%s registros duplicados fueron ignorados",
                duplicados
            )

        #Leyenda de finalización en los logs
        logger.info(
            "Pipeline finalizado correctamente"
        )

    #En caso de error:
    except Exception as error:
        logger.exception(
            "El pipeline terminó con un error: %s",
            error
        )


# Evita que el pipeline se ejecute al importar este módulo
if __name__ == "__main__":
    ejecutar_pipeline()