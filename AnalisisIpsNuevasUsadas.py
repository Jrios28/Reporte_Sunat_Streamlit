import pandas as pd
import urllib3
import numpy as np
from datetime import datetime
from datetime import date
import requests
from requests.auth import HTTPBasicAuth
import json
import ipaddress
import ast
from Envio_Correo import enviar_correo

today = date.today()
fecha_actual = today.strftime("%Y/%m/%d")


def main():
    df_IpsNuevosUsados = pd.read_excel('ConsumoIPsUsado.xlsx')
    df_IpsNuevosUsados = df_IpsNuevosUsados.sort_values(by=['ID_N', 'FECHA'])
    nuevas_ips_por_id = []

    # Recorrer los IDs únicos
    for id_n in df_IpsNuevosUsados['ID_N'].unique():
        # Filtrar las filas correspondientes al ID actual
        df_id = df_IpsNuevosUsados[df_IpsNuevosUsados['ID_N'] == id_n]

        # Verificar si hay al menos dos filas para comparar
        if len(df_id) >= 1:
            # Obtener las dos últimas filas del grupo
            ultima_fila = df_id.iloc[-1]
            penultima_fila = df_id.iloc[-2] if len(df_id) > 1 else None

            address = ultima_fila['ADDRESS']
            nombre = ultima_fila['NOMBRE']

            ultima_fila_lst = ast.literal_eval(ultima_fila['IPS_USADAS'])
            ips_usadas_actual = ultima_fila_lst
            penultima_fila_lst = ast.literal_eval(penultima_fila['IPS_USADAS']) if penultima_fila is not None else []
            ips_usadas_anterior = penultima_fila_lst

            nuevas_ips = list(set(ips_usadas_actual) ^ set(ips_usadas_anterior))
            nuevas_ips_por_id.append({'ID_N': id_n,
                                      'ADDRESS': address,
                                      'NOMBRE': nombre,
                                      'Nuevas_IPS': nuevas_ips})
            # print("nuevas_ips:",type(nuevas_ips))
            # print("nuevas_ips:",nuevas_ips)
            df_resultado = pd.DataFrame(nuevas_ips_por_id)

    df_resultado.to_excel('IpsNuevasUsadas.xlsx')

    # Envio de correo
    # destinatario = ['ftafur@electrodata.com.pe','jrios@electrodata.com.pe']
    #destinatario = ['wmayorga@sunat.gob.pe', 'jbarbadillo@sunat.gob.pe', 'cposadas@sunat.gob.pe',
    #                'fsandoval@electrodata.com.pe', 'jrios@electrodata.com.pe', 'ftafur@electrodata.com.pe']
    #asunto = 'Reporte Nuevas IPs'
    #mensaje = f'Hola, Se ha generado el reporte de IPs Libres respecto a la fecha de {fecha_actual}.'
    #adjunto_path = '/home/pc_report/Reporte_Sunat_Streamlit/IpsNuevasUsadas.xlsx'
    #enviar_correo(destinatario, asunto, mensaje, adjunto_path)


if __name__ == '__main__':
    main()