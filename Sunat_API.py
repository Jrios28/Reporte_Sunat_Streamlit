#=================================Importación de Librerías=================================
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
import plotly.express as px #pip install plotly-express
import streamlit as st #pip install streamlit
import asyncio

import requests
from requests.auth import HTTPBasicAuth

import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import datetime
from datetime import datetime

#=================================Importación de Librerías IMG=====================================
from PIL import Image
#================Importación de Librería apgrid customización de tabla==============================
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, ColumnsAutoSizeMode, JsCode, GridOptionsBuilder
from st_aggrid.grid_options_builder import GridOptionsBuilder

from Apis.Api_Segmento_Red import obtener_datos_de_segmento_red




#Obtencion datos Api_Red

async def main():
    img = Image.open('gf.png')
    imgbarchart = Image.open('bar-chart.png')

    # emojis : https://www.webfx.com/tools/emoji-cheat-sheet/
    st.set_page_config(page_title="Dashboard Sunat IP's",
                       page_icon= img
                       #initial_sidebar_state="expanded"
    )

    #======================================MAINPAGE=======================================#
    st.title("📊 Reportes solución IPAM")
    st.markdown("##")

    # ===================================Tabla Consolidada ================================

    #dfConsolidado = obtener_datos_de_segmento_red()
    dfConsolidado = pd.read_csv('Consolidado_Segmentos_Red_SUNAT.csv', sep=',')

    #Convertir en nulo aquellos pesos (size) que sean mayores a la longitud 8
    #dfConsolidado['Size'] = dfConsolidado['Size'].map(lambda x : int(x) if isinstance(x,float) else x)
    dfConsolidado['Size'] = dfConsolidado['Size'].map(lambda x: int(x) if (isinstance(x, float) and not np.isnan(x)) else x)
    dfConsolidado['Size'] = dfConsolidado['Size'].astype(str)
    dfConsolidado['Size'] = dfConsolidado.apply(lambda x: np.nan if len(x['Size']) > 8 else x['Size'], axis=1)
    dfConsolidado['Size'] = dfConsolidado['Size'].astype(float).astype('Int64')
    dfConsolidado['Id_H'] = dfConsolidado['Id_H'].astype('Int64')
    dfConsolidado['Id_N'] = dfConsolidado['Id_N'].astype('Int64')
    dfConsolidado['Id_P'] = dfConsolidado['Id_P'].astype('Int64')



    #==========================================SIDEBAR============================================#
    #st.sidebar.header("Filtros:")
    #nt = st.sidebar.multiselect(
    #    "Selecciona el tipo de red:",
    #     options=dfConsolidado["Tipo_N"].unique(),
    #     default=dfConsolidado["Tipo_N"].unique()
    #)

    #nz = st.sidebar.multiselect(
    #    "Selecciona tamaño de red:",
    #    options=dfConsolidado["Size"].unique(),
    #    default=dfConsolidado["Size"].unique()
    #)
    #df_seleccion = dfConsolidado[(dfConsolidado["Tipo_N"].isin(nt) & dfConsolidado["Size"].isin(nz))]

    #-----------------------------------------Fechas-----------------------------------------------
    fechaActual = datetime.now()

    # Sidebar para seleccionar el rango de fechas
    st.sidebar.header('Filtro de Fechas')

    min_date = fechaActual
    max_date = fechaActual

    start_date = st.sidebar.date_input('Fecha de inicio', value=min_date)
    end_date = st.sidebar.date_input('Fecha de fin', max_value=max_date)

    #--------------------------------------------------------------------------------------------------

    total_Ips = int(len(dfConsolidado["Address"]))
    totalTipoSupernet = int(len(dfConsolidado[dfConsolidado["Tipo_P"]=="supernet"]))
    totalTipoLan= int(len(dfConsolidado[dfConsolidado["Tipo_P"]=="lan"]))

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

        data_list = []

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

            data_dict = {
                "ID": row["Id_N"],
                "Nombre": row["Nombre_N"],
                "IP": row["Address"]
            }
            data_list.append(data_dict)
            df_nombre_n = pd.DataFrame(data_list)

            nombre_n = f"ID: {row['Id_N']} Nombre: {str(row['Nombre_N'])} IP: {str(row['Address'])}"

            if id_sp not in node_mapping:
                tree.create_node(row["Super_Padre_Name"], id_sp, parent="root")
                node_mapping[id_sp] = row["Super_Padre_Name"]
            #aqui muestro el padre
            if id_p not in node_mapping:
                add_node_with_spacing(id_p, id_sp, row["Nombre_P"] + "/  ID: " + str(row["Id_P"]), spacing=2)
                node_mapping[id_p] = row["Nombre_P"]
            # aqui muestro el hijo
            if id_h not in node_mapping:
                add_node_with_spacing(id_h, id_p, row["Nombre_H"] + "/  ID: " + str(row["Id_H"]), spacing=4)
                node_mapping[id_h] = row["Nombre_H"]
            # aqui muestro el nieto
            if id_n not in node_mapping:
                add_node_with_spacing(id_n, id_h, nombre_n, spacing=6)
                #add_node_with_spacing(id_n, id_h, df_nombre_n, spacing=6)
                node_mapping[id_n] = nombre_n
                #node_mapping[id_n] = st.write(df_nombre_n)



        # Función para mostrar el árbol de manera interactiva
        def display_tree(node_id):
            children = tree.children(node_id)
            if children:
                for child in children:
                    unique_key = f"{node_id}-{child.tag}"  # Genera una clave única basada en la jerarquía
                    if st.checkbox(child.tag , key=unique_key):
                        display_tree(child.identifier)
                        #st.dataframe(bisnietos_df)

        # Mostrar la estructura jerárquica en Streamlit
        display_tree("root")



    # ===================================Consulta Segmentos Libres================================
        st.subheader("Consulta Porcentaje IP's libres por segmento")
        file_path = "D:/Electrodata/11.SUNAT/SunatAPI/ConsumoIPsLibre.xlsx"
        df_IpLibre = pd.read_excel(file_path)

        # --------------------------------Sidebar Filtro Segementos libres-----------------------------------
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
        gd.configure_default_column(editable=True,groupable=True)

        sel_mode = st.radio('Tipo de Selección', options=['Uno','Multiple'])
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




        #id_nieto_input = st.text_input("Ingrese id Segmento de red")
        #st.write(id_nieto_input)

        #if st.button("Consultar API"):
        #    if id_nieto_input:
        #        # Realiza una solicitud a la API con el ID_N ingresado
        #        #url_api = f'https://172.17.1.18/rest/v1/networks/{id_nieto_input}/free_addresses'
        #        url_api = f'https://10.10.129.41/rest/v1/networks/{id_nieto_input}/free_addresses'
        #        response = requests.get(url_api,
        #                                verify=False,
        #                                auth=HTTPBasicAuth('admin', 'password'))
        #        if response.status_code == 200:
        #            data_api = response.json()
        #            # Muestra los datos de la API
        #            st.write("Datos de la API para ID_N (ID_NIETO) =", id_nieto_input)
        #            st.json(data_api)
        #        else:
        #            st.error("No se encontraron datos para el segmento ID_N ingresado.")
        #    else:
        #        st.warning("Ingresa un Segmento ID_N antes de consultar la API.")

    # Título de la aplicación
    st.header("2. Consolidado de Redes con Subredes")
    # Reportes Detallados
    with st.expander("Ver"):

        #df_seleccion_arbol = dfConsolidado.copy()

        # Filtrar registros únicos por Id_N y Address
        redes_padre = dfConsolidado.drop_duplicates(subset=["Id_N", "Address"])[
            ["Id_P", "Nombre_P", "Id_N", "Nombre_N", "Address"]]
        redes_padre.reset_index(drop=True, inplace=True)

        # Título de la aplicación
        #st.title("Redes con Subredes")

        # Crear un menú desplegable para seleccionar una red padre (Id_P)
        selected_red_padre = st.selectbox("Selecciona una red padre (Id_P):", redes_padre["Id_P"].unique())

        # Filtrar registros hijas (Id_H) según la red padre seleccionada
        redes_hijas = dfConsolidado[dfConsolidado["Id_P"] == selected_red_padre].drop_duplicates(
            subset=["Id_H", "Nombre_H"])[
            ["Id_H", "Nombre_H"]]
        redes_hijas.reset_index(drop=True, inplace=True)

        # Crear un menú desplegable para seleccionar una red hija (Id_H)
        selected_red_hija = st.selectbox("Selecciona una red hija (Id_H):", redes_hijas["Id_H"])

        # Filtrar registros nietas (Id_N) según la red hija seleccionada
        redes_nietas = dfConsolidado[
            (dfConsolidado["Id_P"] == selected_red_padre) & (dfConsolidado["Id_H"] == selected_red_hija)][
            ["Id_N", "Nombre_N", "Address"]]
        redes_nietas.reset_index(drop=True, inplace=True)

        # Mostrar la información de la red padre, hija y nieta seleccionada
        if not redes_nietas.empty:
            st.subheader(f"Información de la red padre (Id_P): {selected_red_padre}")
            st.write(redes_padre[redes_padre["Id_P"] == selected_red_padre])

            st.subheader(f"Información de la red hija (Id_H): {selected_red_hija}")
            st.write(redes_hijas[redes_hijas["Id_H"] == selected_red_hija])

            st.subheader("Información de las redes nietas:")
            st.write(redes_nietas)
        else:
            st.warning("No se encontraron redes hijas o nietas para la selección actual.")

        # Exportación de Datos
        st.subheader("Exportación de Datos")
        if st.button("Exportar Datos a CSV"):
            dfConsolidado.to_csv("datos_exportados.csv", index=False)





    #=================================Grafico Barra tipos de red================================

    st.header("3. Reportes de Segmento de Redes")
    with st.expander("Ver"):
        # Distribución de Tipos de Red
        st.subheader("Distribución de Tipos de Red")
        tipo_red_counts = dfConsolidado['Tipo_P'].value_counts()
        st.bar_chart(tipo_red_counts)

        #=================================Grafico mapa de calord================================

        # Relación entre Proveedores y Hardware (Mapa de Calor)
        st.subheader("Relación entre Segmentos de Red padre y sus Hijos")
        plt.figure(figsize=(10, 6))  # Establece el tamaño de la figura
        proveedor_hardware_counts = dfConsolidado.groupby(['Nombre_P', 'Nombre_H']).size().unstack().fillna(0)
        sns.heatmap(proveedor_hardware_counts, cmap="YlGnBu", annot=True, linewidths=0.5)
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot()

    st.header("4. Consolidado por Fechas")
    with st.expander("Ver"):

        #dfConsolidado['DATE'] = pd.to_datetime(dfConsolidado['DATE'],format='%d/%m/%Y')

        # Filtrar el DataFrame según el rango de fechas seleccionado
        filtered_df = dfConsolidado[(dfConsolidado['DATE'] >= start_date.strftime('%Y/%m/%d')) & (dfConsolidado['DATE'] <= end_date.strftime('%Y/%m/%d'))]


        # Mostrar los datos filtrados
        st.subheader('Información filtrada:')
        st.write(filtered_df)
        #df_seleccion_arbol.info()

    ####################===================================================================#################



if __name__ == '__main__':
    # Crea un nuevo bucle de eventos asincrónicos
   loop = asyncio.new_event_loop()
   asyncio.set_event_loop(loop)
   loop.run_until_complete(main())

