# =================================Importación de Librerías=================================
import json
import pandas as pd
import ssl
import plotly.offline
import urllib3
from urllib.request import urlopen

from treelib import Node, Tree
import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import asyncio

import requests
from requests.auth import HTTPBasicAuth

import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import datetime
from datetime import datetime

# =================================Importación de Librerías IMG=====================================
from PIL import Image
# ================Importación de Librería apgrid customización de tabla==============================
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, ColumnsAutoSizeMode, JsCode, GridOptionsBuilder
from st_aggrid.grid_options_builder import GridOptionsBuilder

# from Apis.Api_Segmento_Red import obtener_datos_de_segmento_red
from Envio_Correo import enviar_correo


# Obtencion datos Api_Red

async def main():
    img = Image.open('gf.png')
    imgbarchart = Image.open('bar-chart.png')

    # emojis : https://www.webfx.com/tools/emoji-cheat-sheet/
    st.set_page_config(page_title="Dashboard Sunat IP's",
                       page_icon=img
                       # initial_sidebar_state="expanded"
                       )

    # ======================================MAINPAGE=======================================#
    st.title("📊 Reportes solución IPAM")
    st.markdown("##")

    # ===================================Tabla Consolidada ================================

    # dfConsolidado = obtener_datos_de_segmento_red()
    dfConsolidado = pd.read_csv('Consolidado_Segmentos_Red_SUNAT.csv', sep=',')

    # Convertir en nulo aquellos pesos (size) que sean mayores a la longitud 8
    # dfConsolidado['Size'] = dfConsolidado['Size'].map(lambda x : int(x) if isinstance(x,float) else x)
    dfConsolidado['Size'] = dfConsolidado['Size'].map(
        lambda x: int(x) if (isinstance(x, float) and not np.isnan(x)) else x)
    dfConsolidado['Size'] = dfConsolidado['Size'].astype(str)
    dfConsolidado['Size'] = dfConsolidado.apply(lambda x: np.nan if len(x['Size']) > 8 else x['Size'], axis=1)
    dfConsolidado['Size'] = dfConsolidado['Size'].astype(float).astype('Int64')
    dfConsolidado['Id_H'] = dfConsolidado['Id_H'].astype('Int64')
    dfConsolidado['Id_N'] = dfConsolidado['Id_N'].astype('Int64')
    dfConsolidado['Id_P'] = dfConsolidado['Id_P'].astype('Int64')

    # ====================================================SIDEBAR=======================================#
    # st.sidebar.header("Filtros:")
    # nt = st.sidebar.multiselect(
    #    "Selecciona el tipo de red:",
    #     options=dfConsolidado["Tipo_N"].unique(),
    #     default=dfConsolidado["Tipo_N"].unique()
    # )

    # nz = st.sidebar.multiselect(
    #    "Selecciona tamaño de red:",
    #    options=dfConsolidado["Size"].unique(),
    #    default=dfConsolidado["Size"].unique()
    # )
    # df_seleccion = dfConsolidado[(dfConsolidado["Tipo_N"].isin(nt) & dfConsolidado["Size"].isin(nz))]

    total_Ips = int(len(dfConsolidado["Address"]))
    totalTipoSupernet = int(len(dfConsolidado[dfConsolidado["Tipo_P"] == "supernet"]))
    totalTipoLan = int(len(dfConsolidado[dfConsolidado["Tipo_P"] == "lan"]))

    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        st.subheader("Total Segmentos:")
        st.subheader(total_Ips)
    with middle_column:
        st.subheader("LAN:")
        st.subheader(totalTipoLan)
    with right_column:
        st.subheader("Supernet:")
        st.subheader(totalTipoSupernet)
    st.markdown("---")

    # ================================ARBOL JERARQUICO=======================================#

    # Título de la aplicación
    st.header("1. Disponibilidad Jerarquica de Segmentos")
    with st.expander("Ver"):

        # Crear una estructura de árbol jerárquico
        tree = Tree()
        tree.create_node("Root", "root")  # Nodo raíz

        # Diccionario para mapear los nodos en el árbol
        node_mapping = {"root": "Root"}

        # Función para agregar nodos con espaciado a la derecha
        def add_node_with_spacing(node_id, parent_id, label, spacing):
            parent = tree.get_node(parent_id)
            tag = " - - " * spacing + label
            tree.create_node(tag=tag, identifier=node_id, parent=parent_id)

        # Iterar a través de los datos y agregar nodos al árbol
        for index, row in dfConsolidado.iterrows():
            id_sp = str(row["Id_super_padre"])
            id_p = str(row["Id_P"])
            id_h = str(row["Id_H"])
            id_n = str(row["Id_N"])
            # nombre_n = "ID : " + str(row["Id_N"]) + " Nombre:  " + row["Nombre_N"] + " IP : " + str(row["Address"])
            nombre_n = f"ID: {row['Id_N']} Nombre: {str(row['Nombre_N'])} IP: {str(row['Address'])}"

            if id_sp not in node_mapping:
                tree.create_node(row["Super_Padre_Name"], id_sp, parent="root")
                node_mapping[id_sp] = row["Super_Padre_Name"]

            # aqui muestro el padre
            if id_p not in node_mapping:
                add_node_with_spacing(id_p, id_sp, str(row["Nombre_P"]) + "/  ID: " + str(row["Id_P"]), spacing=2)
                node_mapping[id_p] = str(row["Nombre_P"])
            # aqui muestro el hijo
            if id_h not in node_mapping:
                add_node_with_spacing(id_h, id_p, str(row["Nombre_H"]) + "/  ID: " + str(row["Id_H"]), spacing=4)
                node_mapping[id_h] = str(row["Nombre_H"])
            # aqui muestro el nieto
            if id_n not in node_mapping:
                add_node_with_spacing(id_n, id_h, nombre_n, spacing=6)
                node_mapping[id_n] = nombre_n

        # Función para mostrar el árbol de manera interactiva
        def display_tree(node_id):
            children = tree.children(node_id)
            if children:
                for child in children:
                    unique_key = f"{node_id}-{child.tag}"  # Genera una clave única basada en la jerarquía
                    if st.checkbox(child.tag, key=unique_key):
                        display_tree(child.identifier)
                        # st.dataframe(bisnietos_df)

        # Mostrar la estructura jerárquica en Streamlit
        display_tree("root")

        # ===================================Consulta Segmentos Libres================================
        st.subheader("Consulta Porcentaje IP's libres por segmento")
        #file_path = "/home/pc_report/Reporte_Sunat_Streamlit/ConsumoIPsLibre.xlsx"
        file_path = "D:/Electrodata/11.SUNAT/SunatAPI/ConsumoIPsLibre.xlsx"
        df_IpLibre = pd.read_excel(file_path)

        # Mostrar el DataFrame resultante
        gd = GridOptionsBuilder.from_dataframe(df_IpLibre)
        # Definir código JavaScript para personalizar los encabezados de las columnas
        custom_header_code = JsCode("""
        function(params) {
            var columnFieldMapping = {
                'ID_N': 'Id',
                'ADDRESS': 'Address',
                'NOMBRE': 'Nombre',
                'NRO_IPS_TOTALES': 'Total',
                'NRO_IPS_LIBRES': 'Libres',
                'PORCENTAJE_IPS_LIBRES': 'Porcentaje'
            };
            return columnFieldMapping[params.colDef.field];
        }
        """)

        # Aplicar la función de JavaScript para personalizar los encabezados de las columnas
        for col in df_IpLibre.columns:
            gd.configure_column(col, headerValueGetter=custom_header_code)

        gd.configure_pagination(enabled=True)
        gd.configure_default_column(editable=True, groupable=True)

        sel_mode = st.radio('Tipo de Selección', options=['Uno', 'Multiple'])
        gd.configure_selection(selection_mode=sel_mode, use_checkbox=True)
        gridoptions = gd.build()
        grid_table = AgGrid(df_IpLibre,
                            gridOptions=gridoptions,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            height=500,
                            allow_unsafe_jscode=True,
                            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
                            custom_css={
                                "#gridToolBar": {
                                    "padding-bottom": "0px !important",
                                }
                            }
                            )

        sel_row = grid_table["selected_rows"]
        st.write(sel_row)

        ## SECCION ENVIO CORREO
        show_expander = st.checkbox("Enviar Correo Ips Libres")

        if show_expander:
            destinatarios = st.text_area("Destinatarios (separados por coma)", "")
            asunto = st.text_input("Asunto del Correo", "")
            mensaje = st.text_area("Cuerpo del Correo", "")

            if st.button("Enviar Correo"):
                # Verificar si los campos obligatorios están llenos
                if not destinatarios or not asunto or not mensaje:
                    st.warning("Por favor, complete todos los campos obligatorios.")
                else:
                    # Convertir la cadena de destinatarios en una lista
                    destinatarios = [correo.strip() for correo in destinatarios.split(",")]

                    try:
                        # Intentar enviar el correo
                        enviar_correo(destinatarios, asunto, mensaje, file_path)

                        # Mostrar mensaje de éxito
                        st.success("Correo electrónico enviado exitosamente.")
                    except Exception as e:
                        # Mostrar mensaje de error si hay un problema
                        st.error(f"Error al enviar el correo: {str(e)}")

                        # Título de la aplicación
    st.header("2. Consolidado de Segmentos de Red")
    # Reportes Detallados
    with st.expander("Ver"):

        st.subheader("Segmentos Nuevos")
        #file_path_segmento = "/home/pc_report/Reporte_Sunat_Streamlit/Consolidado_Segmentos_Red_SUNAT_NUEVOS.csv"
        file_path_segmento = "D:/Electrodata/11.SUNAT/SunatAPI/Consolidado_Segmentos_Red_SUNAT_NUEVOS.csv"
        df_Segmento = pd.read_csv(file_path_segmento)

        df_SegmentoNuevo = df_Segmento[['Id_N', 'Nombre_N', 'Tipo_N', 'Address', 'Size', 'fecha_nuevo']]

        # Mostrar el DataFrame resultante
        gd = GridOptionsBuilder.from_dataframe(df_SegmentoNuevo)
        # Definir código JavaScript para personalizar los encabezados de las columnas
        custom_header_code = JsCode("""
        function(params) {
            var columnFieldMapping = {
                'Id_N': 'Id',
                'Nombre_N': 'Nombre',
                'Tipo_N': 'Tipo',
                'Address': 'Address',
                'Size': 'Size',
                'fecha_nuevo': 'Fecha'
            };
            return columnFieldMapping[params.colDef.field];
        }
        """)

        # Aplicar la función de JavaScript para personalizar los encabezados de las columnas
        for col in df_SegmentoNuevo.columns:
            gd.configure_column(col, headerValueGetter=custom_header_code)

        gd.configure_pagination(enabled=True)
        gd.configure_default_column(editable=True, groupable=True)

        sel_mode = st.radio('Tipo', options=['Uno', 'Multiple'])
        gd.configure_selection(selection_mode=sel_mode, use_checkbox=True)
        gridoptions = gd.build()
        grid_table = AgGrid(df_SegmentoNuevo,
                            gridOptions=gridoptions,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            height=400,
                            allow_unsafe_jscode=True,
                            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
                            custom_css={
                                "#gridToolBar": {
                                    "padding-bottom": "0px !important",
                                }
                            }
                            )

        sel_row = grid_table["selected_rows"]
        st.write(sel_row)

        ## SECCION ENVIO CORREO
        show_expander = st.checkbox("Enviar Correo Segmentos de Red")

        if show_expander:
            destinatarios = st.text_area("Destinatarios (separados por coma)", "")
            asunto = st.text_input("Asunto del Correo", "")
            mensaje = st.text_area("Cuerpo del Correo", "")

            if st.button("Enviar Correo"):
                # Verificar si los campos obligatorios están llenos
                if not destinatarios or not asunto or not mensaje:
                    st.warning("Por favor, complete todos los campos obligatorios.")
                else:
                    # Convertir la cadena de destinatarios en una lista
                    destinatarios = [correo.strip() for correo in destinatarios.split(",")]

                    try:
                        # Intentar enviar el correo
                        enviar_correo(destinatarios, asunto, mensaje, file_path_segmento)

                        # Mostrar mensaje de éxito
                        st.success("Correo electrónico enviado exitosamente.")
                    except Exception as e:
                        # Mostrar mensaje de error si hay un problema
                        st.error(f"Error al enviar el correo: {str(e)}")

                        # =================================Grafico Barra tipos de red================================

    st.header("3. Reportes de Ips Nuevas Usadas")
    with st.expander("Ver"):

        st.subheader("Ips Usadas")
        #file_path_usado = "/home/pc_report/Reporte_Sunat_Streamlit/ConsumoIPsUsado.xlsx"
        file_path_usado = "D:/Electrodata/11.SUNAT/SunatAPI/IpsNuevasUsadas.xlsx"
        df_IpUsado = pd.read_excel(file_path_usado)

        fecha_actual = datetime.now()
        mindate = fecha_actual
        maxdate = fecha_actual

        # Filtrar
        #fecha_inicio_ip = st.date_input("Fecha de Inicio", value=mindate)
        #fecha_fin_ip = st.date_input("Fecha de Fin", max_value=maxdate)

        direcciones_unicas = df_IpUsado['ADDRESS'].unique()

        direccion_ip = st.selectbox('Seleccione la Direccion IP', direcciones_unicas)

        #df_filtrado = df_IpUsado[(df_IpUsado['FECHA'] >= fecha_inicio_ip.strftime('%Y/%m/%d')) & (df_IpUsado['FECHA'] <= fecha_fin_ip.strftime('%Y/%m/%d'))]

        if direccion_ip:
            df_filtrado = df_IpUsado[df_IpUsado['ADDRESS'] == direccion_ip]

        st.write(df_filtrado[['ADDRESS', 'NOMBRE', 'Nuevas_IPS']])

        show_expander = st.checkbox("Enviar Correo Ips Usadas")

        if show_expander:
            destinatarios = st.text_area("Destinatarios (separados por coma)", "")
            asunto = st.text_input("Asunto del Correo", "")
            mensaje = st.text_area("Cuerpo del Correo", "")

            if st.button("Enviar Correo de Ips Usadas"):
                # Verificar si los campos obligatorios están llenos
                if not destinatarios or not asunto or not mensaje:
                    st.warning("Por favor, complete todos los campos obligatorios.")
                else:
                    # Convertir la cadena de destinatarios en una lista
                    destinatarios = [correo.strip() for correo in destinatarios.split(",")]

                    try:
                        # Intentar enviar el correo
                        enviar_correo(destinatarios, asunto, mensaje, file_path_usado)

                        # Mostrar mensaje de éxito
                        st.success("Correo electrónico enviado exitosamente.")
                    except Exception as e:
                        # Mostrar mensaje de error si hay un problema
                        st.error(f"Error al enviar el correo: {str(e)}")

    st.header("4. Consolidado por Fechas")
    with st.expander("Ver"):
        # -----------------------------------------Fechas-----------------------------------------------
        fechaActual = datetime.now()

        min_date = fechaActual
        max_date = fechaActual

        start_date = st.date_input('Fecha de inicio', value=min_date)
        end_date = st.date_input('Fecha de fin', max_value=max_date)

        # dfConsolidado['DATE'] = pd.to_datetime(dfConsolidado['DATE'],format='%d/%m/%Y')

        # Filtrar el DataFrame según el rango de fechas seleccionado
        #linux
        #filtered_df = dfConsolidado[(dfConsolidado['DATE'] >= start_date.strftime('%Y/%m/%d')) & (dfConsolidado['DATE'] <= end_date.strftime('%Y/%m/%d'))]
        #windows
        filtered_df = dfConsolidado[(dfConsolidado['DATE'] >= start_date.strftime('%d/%m/%Y')) & (dfConsolidado['DATE'] <= end_date.strftime('%d/%m/%Y'))]

        # Mostrar los datos filtrados
        st.subheader('Información filtrada:')
        st.write(filtered_df)
        # df_seleccion_arbol.info()

    ####################===================================================================#################


if __name__ == '__main__':
    # Crea un nuevo bucle de eventos asincrónicos
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

