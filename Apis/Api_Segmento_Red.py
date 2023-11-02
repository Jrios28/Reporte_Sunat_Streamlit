import json
import pandas as pd
import ssl
import urllib3
from urllib.request import urlopen
import requests
from requests.auth import HTTPBasicAuth
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
from datetime import date
import streamlit as st

url_padre = "https://10.10.129.41/rest/v1/networks"


@st.cache(allow_output_mutation=True)
def obtener_datos_de_segmento_red():
    response = requests.get(url_padre,
                            verify=False,
                            auth=HTTPBasicAuth('admin', 'password'))
    datos = json.loads(response.text)
    datos_segmento_red = [t["network"] for t in datos]
    filtered_data = [d for d in datos_segmento_red if d['network_location'] == '506' or d['network_location'] == '-1']
    df = pd.DataFrame(filtered_data)
    df1 = df[['network_id', 'network_name', 'network_location', 'network_type']]
    # Obtener los valores de la primera fila
    primer_fila = df1.iloc[0]
    # Crear las columnas ID_SUPER_PADRE y SUPER_PADRE_NAME
    df1['ID_SUPER_PADRE'] = primer_fila['network_id']
    df1['SUPER_PADRE_NAME'] = primer_fila['network_name']
    # Renombrar las columnas para cumplir con la estructura requerida
    df1 = df1.rename(columns={'network_id': 'ID_PADRE', 'network_name': 'NAME', 'network_type': 'TYPE'})
    nuevo_orden = ['ID_SUPER_PADRE', 'SUPER_PADRE_NAME', 'ID_PADRE', 'NAME', 'network_location', 'TYPE']
    df2 = df1[nuevo_orden]
    df2 = df2.drop(0, axis=0)

    today = date.today()
    df_padre = df2[['ID_SUPER_PADRE','SUPER_PADRE_NAME','ID_PADRE','NAME','TYPE']]
    df_padre["DATE"] = today.strftime("%Y/%m/%d")

    # Crear DataFrames temporales para el nivel de hijo y nieto
    df_hijo = pd.DataFrame()
    df_nieto = pd.DataFrame()

    # Iterar a través de los registros del nivel de padre
    for index, row in df_padre.iterrows():
        id_padre = row['ID_PADRE']
        # Obtener datos de nivel de hijo para el ID_PADRE actual
        url_hijo = f'https://10.10.129.41/rest/v1/networks/{id_padre}/children'
        response_hijo = requests.get(url_hijo,
                                     verify=False,
                                     auth=HTTPBasicAuth('admin', 'password'))
        data_hijo = response_hijo.json()
        data_hijo2 = [t["network"] for t in data_hijo]
        df_hijo_temp = pd.DataFrame({"ID_HIJO": [t["network_id"] for t in data_hijo2],
                                     "NAME_CHILD": [t["network_name"] for t in data_hijo2],
                                     "LOCATION": [t["network_location"] for t in data_hijo2],
                                     "FAMILY": [t["network_family"] for t in data_hijo2],
                                     "TYPE": [t["network_type"] for t in data_hijo2],
                                     "SIZE": [t["network_size"] for t in data_hijo2]
                                     })
        #df_hijo = df_hijo.append(df_hijo_temp, ignore_index=True)
        # Agregar los datos al DataFrame df_hijo
        df_hijo = pd.concat([df_hijo, df_hijo_temp], ignore_index=True)
        # Iterar a través de los registros del nivel de hijo
        for index_hijo, row_hijo in df_hijo_temp.iterrows():
            id_hijo = row_hijo["ID_HIJO"]

            # Obtener datos del nivel de nieto para el ID_HIJO actual
            url_nieto = f'https://10.10.129.41/rest/v1/networks/{id_hijo}/children'
            response_nieto = requests.get(url_nieto,
                                          verify=False,
                                          auth=HTTPBasicAuth('admin', 'password'))

            data_nieto = response_nieto.json()
            data_nieto = [item for item in data_nieto if 'id' in item and 'network' in item]
            data_nieto2 = [t["network"] for t in data_nieto]
            df_nieto_temp = pd.DataFrame({"ID_NIETO": [t["network_id"] for t in data_nieto2],
                                          "NAME_CHILD": [t["network_name"] for t in data_nieto2],
                                          "LOCATION": [t["network_location"] for t in data_nieto2],
                                          "FAMILY": [t["network_family"] for t in data_nieto2],
                                          "TYPE": [t["network_type"] for t in data_nieto2],
                                          "SIZE": [t["network_size"] for t in data_nieto2],
                                          "ADDRESS": [t["network_address"] for t in data_nieto2]
                                          })
            #df_nieto = df_nieto.append(df_nieto_temp, ignore_index=True)
            df_nieto = pd.concat([df_nieto, df_nieto_temp], ignore_index=True)

    df_hijo['LOCATION'] = df_hijo['LOCATION'].astype(int)
    df_hijo = df_hijo.rename(columns={
        "LOCATION": "ID_FK_PADRE"
    })

    df_nieto['ID_NIETO'] = df_nieto['ID_NIETO'].astype(int)
    df_nieto['LOCATION'] = df_nieto['LOCATION'].astype(int)
    df_nieto = df_nieto.rename(columns={
        "LOCATION": "ID_FK_HIJO"
    })


    df_consolidado = df_nieto.merge(df_hijo, left_on="ID_FK_HIJO", right_on="ID_HIJO", how="inner")
    # Renombra las columnas para mayor claridad
    df_consolidado = df_consolidado.rename(columns={
        "NAME_CHILD_x": "NAME_NIETO",
        "FAMILY_x": "FAMILY_NIETO",
        "TYPE_x": "TYPE_NIETO",
        "SIZE_x": "SIZE_NIETO",
        "NAME_CHILD_y": "NAME_HIJO",
        "FAMILY_y": "FAMILY_HIJO",
        "TYPE_y": "TYPE_HIJO",
        "SIZE_y": "SIZE_HIJO",
    })
    df_consolidado_general = df_consolidado.merge(df_padre, left_on="ID_FK_PADRE", right_on="ID_PADRE", how="inner")

    df_consolidado_jerarquico = df_consolidado_general[['ID_SUPER_PADRE','SUPER_PADRE_NAME','ID_PADRE','NAME','TYPE','ID_HIJO','NAME_HIJO','TYPE_HIJO','ID_NIETO','NAME_NIETO','TYPE_NIETO', 'ADDRESS','SIZE_NIETO','DATE']]

    df_consolidado_jerarquico = df_consolidado_jerarquico.rename(columns={
        "ID_SUPER_PADRE":"Id_super_padre",
        "SUPER_PADRE_NAME":"Super_Padre_Name",
        "ID_PADRE": "Id_P",
        "NAME": "Nombre_P",
        "TYPE": "Tipo_P",
        "ID_HIJO": "Id_H",
        "NAME_HIJO": "Nombre_H",
        "TYPE_HIJO": "Tipo_H",
        "ID_NIETO": "Id_N",
        "NAME_NIETO": "Nombre_N",
        "TYPE_NIETO": "Tipo_N",
        "ADDRESS": "Address",
        "SIZE_NIETO": "Size"
    })

    # Obtener la fecha y hora actual
    #now = datetime.now()
    # Formatear la fecha y hora en el formato deseado
    #fecha_hora_actual = now.strftime('%d/%m/%Y %H:%M:%S')
    #df_consolidado_jerarquico["DATE_TIME"] = fecha_hora_actual
    df_consolidado_jerarquico.to_csv("Consolidado_Segmentos_Red_SUNAT.csv", index=False)

    return df_consolidado_jerarquico