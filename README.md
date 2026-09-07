# Pipeline ETL Automatizado de Datos Climatológicos

Proyecto end-to-end de automatización y análisis de datos meteorológicos desarrollado con **Python**, **PostgreSQL**, **GitHub Actions** y **Streamlit**.

El sistema recopila periódica y automáticamente información meteorológica de distintas ciudades de México mediante la API de **Open-Meteo**, valida y transforma los registros, almacena un histórico en una base de datos PostgreSQL en la nube y permite consultar los resultados mediante un dashboard interactivo.

## Objetivo

Diseñar e implementar un pipeline ETL automatizado capaz de:

- Extraer información meteorológica desde una API externa.
- Transformar y validar los registros obtenidos.
- Construir un histórico de observaciones climatológicas.
- Evitar la inserción de registros duplicados.
- Automatizar la ejecución del pipeline en la nube.
- Visualizar y comparar los datos mediante un dashboard interactivo.

## Arquitectura
Open-Meteo API -> Pipeline ETL -> Github Actions (ejecución programada) -> Neon PostgreSQL -> Streamlit Community Cloud -> Usuario
