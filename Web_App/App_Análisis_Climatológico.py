#Librerías
from pathlib import Path
import altair as alt
import pandas as pd
import streamlit as st
import os
import psycopg
from dotenv import load_dotenv

#Configuración de la pestaña de la página
st.set_page_config(
    page_title="Análisis Climatológico",
    page_icon="🌦️",
    layout="wide"
)

#Variables de entorno
ruta_proyecto = Path(__file__).resolve().parent
ruta_env = ruta_proyecto / ".env"
load_dotenv(ruta_env)
DATABASE_URL = os.getenv("DATABASE_URL")

#Si no existe el URL de Neon para la BD
if not DATABASE_URL:
    st.error("No se encontró el URL para la Base de Datos.")
    st.stop()

#Función para cargar los datos
@st.cache_data(ttl = 300)
def cargar_datos():

    #Conexión con SQLite
    with psycopg.connect(DATABASE_URL) as conexion:
        with conexion.cursor() as cursor:
        
            #Query para selección de datos
            cursor.execute("""
                    SELECT
                        ciudad,
                        fecha_hora,
                        temperatura,
                        humedad,
                        precipitacion,
                        velocidad_viento
                    FROM clima
                    ORDER BY fecha_hora;
                """)

            #Guardando las filas de la consulta
            registros = cursor.fetchall()

            #Nombres de las columnas
            columnas = [
                descripcion.name
                for descripcion in cursor.description
            ]

    #Creación del DF
    df = pd.DataFrame(
        registros,
        columns = columnas
    )

    #Si hay registros, convertir la fecha y hora a tipo "datetime"
    if not df.empty:
        df["fecha_hora"] = pd.to_datetime(df["fecha_hora"])
    return df

#Función para gráficas de líneas
def grafica_linea(df, variable, titulo, unidad):

##Gráfica
    grafica = (
        alt.Chart(df).mark_line(point = True).encode(x = alt.X(
                "fecha_hora:T",
                title="Fecha y hora",
                axis = alt.Axis(
                    format = "%d %b %H:%M",
                    labelAngle = -35
                )
            ),

            #Eje Y
            y = alt.Y(
                f"{variable}:Q",
                title = f"{titulo} ({unidad})",
                scale = alt.Scale(
                    zero = False
                )),

            #Información que aparecerá al colocar el cursor en un punto
            tooltip = [
                alt.Tooltip(
                    "fecha_hora:T",
                    title = "Fecha",
                    format = "%d/%m/%Y %H:%M"
                ),
                alt.Tooltip(
                    f"{variable}:Q",
                    title = f"{titulo} ({unidad})",
                    format = ".1f"
                )
            ]
        ).properties(height = 280).interactive()
    )

    return grafica

#Función para las gráficas de barras
def grafica_barras_tiempo( df, variable, titulo, unidad):

    #Gráfico
    grafica = (alt.Chart(df).mark_bar().encode(
            x = alt.X(
                "fecha_hora:T",
                title = "Fecha y hora",
                axis = alt.Axis(
                    format = "%d %b %H:%M",
                    labelAngle = -35
                )
            ),

            #Eje Y
            y = alt.Y(
                f"{variable}:Q",
                title = f"{titulo} ({unidad})"
            ),

            #Información mostrada con el cursos
            tooltip = [
                alt.Tooltip(
                    "fecha_hora:T",
                    title = "Fecha",
                    format = "%d/%m/%Y %H:%M"
                ),
                alt.Tooltip(
                    f"{variable}:Q",
                    title=f"{titulo} ({unidad})",
                    format = ".1f"
                )
            ]
        ).properties(height = 280)
    )

    return grafica

#Función para las gráficas comparativas entre ciudades
def grafica_comparacion( df, variable, titulo, unidad):

#Gráfico
    grafica = (alt.Chart(df).mark_bar().encode(
            y = alt.Y(
                "ciudad:N",
                title = None,
                sort = "-x"
            ),

            #Eje X
            x = alt.X(
                f"{variable}:Q",
                title = f"{titulo} ({unidad})"
            ),

            #Información con el cursor
            tooltip=[
                alt.Tooltip(
                    "ciudad:N",
                    title = "Ciudad"
                ),
                alt.Tooltip(
                    f"{variable}:Q",
                    title = f"{titulo} ({unidad})",
                    format = ".1f"
                )
            ]
        ).properties(height = 260)
    )

    return grafica

#Variable para almacenar los datos
try:
    df = cargar_datos()

#En caso de error
except Exception as error:
    st.error("No fue posible conectar con la base de datos.")
    st.exception(error)
    st.stop()

#Si no hay registros:
if df.empty:
    st.warning("No hay datos disponibles.")
    st.stop()

#Obteniendo la fecha y hora más reciente
ultima_actualizacion = (
    df["fecha_hora"].max()
)

#Título de la página
st.title("🌦️ Dashboard de Análisis Climatológico")

#Descripción de la app
st.caption("Análisis de datos meteorológicos recopilados automáticamente mediante un pipeline ETL desarrollado con Python, API de Open-Meteo y SQLite."
)

st.caption(
    f"🕒 Última actualización: "
    f"{ultima_actualizacion:%d/%m/%Y %H:%M}"
)

# Menú lateral

#Título
st.sidebar.header("🔎 Filtros")

#Filtros por ciudad
ciudad_seleccionada = (
    st.sidebar.selectbox(
        "Ciudad",
        sorted(
            df["ciudad"].unique()
        )
    )
)

#Fecha más antigua
fecha_min = (df["fecha_hora"].min().date())
#Fecha más reciente
fecha_max = (df["fecha_hora"].max().date())

#Fecha de inicio del rango
fecha_inicio = st.sidebar.date_input(
    "Fecha de inicio",
    value = fecha_min,
    min_value = fecha_min,
    max_value = fecha_max,
    format = "DD/MM/YYYY"
)

#Fecha final del rango
fecha_fin = st.sidebar.date_input(
    "Fecha de fin",
    value = fecha_max,
    min_value = fecha_inicio,
    max_value = fecha_max,
    format = "DD/MM/YYYY"
)

#Si la fecha seleccionada de inicio es más reciente que la de fin
if fecha_inicio > fecha_fin:
    st.sidebar.error(
        "La fecha inicial no puede ser posterior a la fecha final."
    )
    st.stop()

#Creando un DF con los registros que coinciden con el rango especificado
df_rango = df[(df["fecha_hora"].dt.date >= fecha_inicio) & (df["fecha_hora"].dt.date <= fecha_fin)].copy()

#Si no hay ningún registro en el rango seleccionado:
if df_rango.empty:
    st.warning("No hay registros disponibles en este lapso.")
    st.stop()

#Creando un df con los registros que corresponden a la ciudad seleccionada
df_ciudad = df_rango[df_rango["ciudad"] == ciudad_seleccionada].copy()

#Ordenando datos por fecha y hora
df_ciudad = (df_ciudad.sort_values("fecha_hora"))

#Si no hay registros de la ciudad seleccionada:
if df_ciudad.empty:
    st.warning("No hay registros de esta ciudad en este lapso.")
    st.stop()

#Último registro guardado
ultimo_registro = (df_ciudad.iloc[-1])


#Títulos de las tabs
tab_ciudad, tab_comparacion = (
    st.tabs(
        [
            "📍 Análisis por ciudad",
            "🌎 Comparación entre ciudades"
        ]
    )
)

#Tab 1: Análisis por ciudad
with tab_ciudad:
    st.header(f"📍 {ciudad_seleccionada}")
    st.caption(
        f"Último registro disponible: "
        f"{ultimo_registro['fecha_hora']:%d/%m/%Y %H:%M}"
    )

    #Columnas
    col1, col2, col3, col4 = (
        st.columns(4)
    )

    #Temperatura
    with col1:
        st.metric(
            "🌡️ Temperatura",
            f"{ultimo_registro['temperatura']:.1f} °C"
        )

    #Humedad
    with col2:
        st.metric(
            "💧 Humedad",
            f"{ultimo_registro['humedad']:.0f} %"
        )

    #Precipitación
    with col3:
        st.metric(
            "🌧️ Precipitación",
            f"{ultimo_registro['precipitacion']:.1f} mm"
        )

    #Velocidad del viento
    with col4:
        st.metric(
            "💨 Velocidad del viento",
            f"{ultimo_registro['velocidad_viento']:.1f} km/h"
        )
    st.divider()


    #En la primera fila van las gráficas de temperatura y de humedad
    col_temp, col_humedad = (st.columns(2))

    #Temperatura
    with col_temp:
        st.subheader("🌡️ Temperatura")
        #Llamando a la función de gráfica de líneas
        st.altair_chart(grafica_linea(
                df_ciudad,
                "temperatura",
                "Temperatura",
                "°C"
            ),
            use_container_width=True
        )

    #Humedad
    with col_humedad:
        st.subheader("💧 Humedad")
        #Gráfico de línea
        st.altair_chart(grafica_linea(
                df_ciudad,
                "humedad",
                "Humedad",
                "%"
            ),
            use_container_width=True
        )


    #Seguna fila de gráficas
    col_lluvia, col_viento = (st.columns(2))

    #Precipitación
    with col_lluvia:
        st.subheader("🌧️ Precipitación")
        #Gráfico de barras
        st.altair_chart(grafica_barras_tiempo(
                df_ciudad,
                "precipitacion",
                "Precipitación",
                "mm"
            ),
            use_container_width=True
        )

    #Velocidad del viento
    with col_viento:
        st.subheader("💨 Velocidad del viento")
        #Gráfico
        st.altair_chart(
            grafica_linea(
                df_ciudad,
                "velocidad_viento",
                "Velocidad del viento",
                "km/h"
            ),
            use_container_width=True
        )


    #Mostrar el DF con los datos
    with st.expander("📋 Ver datos históricos"):
        st.dataframe(
            df_ciudad[
                [
                    "fecha_hora",
                    "temperatura",
                    "humedad",
                    "precipitacion",
                    "velocidad_viento"
                ]
            ],
            use_container_width = True,
            hide_index = True,
            column_config = {
                "fecha_hora":
                    st.column_config.DatetimeColumn(
                        "Fecha y hora",
                        format = "DD/MM/YYYY HH:mm"
                    ),
                "temperatura":
                    st.column_config.NumberColumn(
                        "Temperatura",
                        format = "%.1f °C"
                    ),
                "humedad":
                    st.column_config.NumberColumn(
                        "Humedad",
                        format = "%.0f %%"
                    ),
                "precipitacion":
                    st.column_config.NumberColumn(
                        "Precipitación",
                        format = "%.1f mm"
                    ),
                "velocidad_viento":
                    st.column_config.NumberColumn(
                        "Viento",
                        format = "%.1f km/h"
                    )
            }
        )


#Comparación entre ciudades
with tab_comparacion:
    st.header("🌎 Comparación entre ciudades")
    st.caption("La comparación utiliza la observación más reciente disponible de cada ciudad dentro del rango seleccionado.")

    #Ordenando los registros por fecha y hora
    df_comparacion = (df_rango.sort_values("fecha_hora"))

    #Obteniendo el registro más reciente
    ultimos_registros = (df_comparacion.groupby("ciudad", as_index = False).tail(1).copy())


    #KPIs comparativos
    #Mayor temperatura
    ciudad_mas_calida = (ultimos_registros.loc[ultimos_registros["temperatura"].idxmax()])

    #Mayor humedad
    ciudad_mas_humeda = (ultimos_registros.loc[ultimos_registros["humedad"].idxmax()])

    #Velocidad del viento más
    ciudad_mas_ventosa = (ultimos_registros.loc[ultimos_registros["velocidad_viento"].idxmax()])

    #Creando 3 columnas
    col1, col2, col3 = (
        st.columns(3)
    )

    #Ciudad con la mayor temperatura
    with col1:
        st.metric(
            "🔥 Mayor temperatura",
            f"{ciudad_mas_calida['temperatura']:.1f} °C"
        )
        st.caption(
            ciudad_mas_calida["ciudad"]
        )

    #Ciudad con la mayor humedad
    with col2:
        st.metric(
            "💧 Mayor humedad",
            f"{ciudad_mas_humeda['humedad']:.0f} %"
        )
        st.caption(
            ciudad_mas_humeda["ciudad"]
        )

    #Ciudad con más viento
    with col3:
        st.metric(
            "💨 Mayor velocidad del viento",
            f"{ciudad_mas_ventosa['velocidad_viento']:.1f} km/h"
        )
        st.caption(
            ciudad_mas_ventosa["ciudad"]
        )

    st.divider()


    #Primera fila comparativa
    col_temp, col_humedad = (
        st.columns(2)
    )

    #Gráficos
    #Temperatura
    with col_temp:
        st.subheader("🌡️ Temperatura por ciudad")
        st.altair_chart(
            grafica_comparacion(
                ultimos_registros,
                "temperatura",
                "Temperatura",
                "°C"
            ),
            use_container_width=True
        )

    #Humedad
    with col_humedad:
        st.subheader("💧 Humedad por ciudad")
        st.altair_chart(
            grafica_comparacion(
                ultimos_registros,
                "humedad",
                "Humedad",
                "%"
            ),
            use_container_width=True
        )

    #Segunda fila
    col_lluvia, col_viento = (st.columns(2))

    #Precipitación
    with col_lluvia:
        st.subheader("🌧️ Precipitación por ciudad")
        st.altair_chart(
            grafica_comparacion(
                ultimos_registros,
                "precipitacion",
                "Precipitación",
                "mm"
            ),
            use_container_width=True
        )

    #Velocidad del viento
    with col_viento:
        st.subheader("💨 Viento por ciudad")
        st.altair_chart(
            grafica_comparacion(
                ultimos_registros,
                "velocidad_viento",
                "Velocidad del viento",
                "km/h"
            ),
            use_container_width=True
        )

    #Tabla con los últimos registros por ciuedad
    with st.expander("📋 Ver últimas observaciones por ciudad"):
        st.dataframe(
            ultimos_registros[
                [
                    "ciudad",
                    "fecha_hora",
                    "temperatura",
                    "humedad",
                    "precipitacion",
                    "velocidad_viento"
                ]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "ciudad":
                    "Ciudad",
                "fecha_hora":
                    st.column_config.DatetimeColumn(
                        "Fecha y hora",
                        format="DD/MM/YYYY HH:mm"
                    ),
                "temperatura":
                    st.column_config.NumberColumn(
                        "Temperatura",
                        format="%.1f °C"
                    ),
                "humedad":
                    st.column_config.NumberColumn(
                        "Humedad",
                        format="%.0f %%"
                    ),
                "precipitacion":
                    st.column_config.NumberColumn(
                        "Precipitación",
                        format="%.1f mm"
                    ),
                "velocidad_viento":
                    st.column_config.NumberColumn(
                        "Viento",
                        format="%.1f km/h"
                    )
            }
        )