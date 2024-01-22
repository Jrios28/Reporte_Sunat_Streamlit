import pandas as pd
import urllib3
import numpy as np
from datetime import datetime
from datetime import date
import requests
from requests.auth import HTTPBasicAuth
import json
import ipaddress
import os

urllib3.disable_warnings()
from Envio_Correo import enviar_correo

today = datetime.now()
fecha_actual = today.strftime("%Y/%m/%d %H:%M")


def main():
    df_consolidado = pd.read_csv('Consolidado_Segmentos_Red_SUNAT.csv')

    df_consolidado['Size'] = df_consolidado['Size'].map(lambda x: int(x) if (isinstance(x, float) and not np.isnan(x)) else x)
    df_consolidado['Size'] = df_consolidado['Size'].astype(str)
    df_consolidado['Size'] = df_consolidado.apply(lambda x: np.nan if len(x['Size']) > 8 else x['Size'], axis=1)
    df_consolidado['Size'] = df_consolidado['Size'].astype(float).astype('Int64')
    df_consolidado['Id_N'] = df_consolidado['Id_N'].astype('Int64')

    valores_a_excluir = [37898, 37901, 37904, 37907, 26116]

    df_consolidado_modificado = df_consolidado[~df_consolidado["Id_N"].isin(valores_a_excluir)]

    data_list = []

    for index, row in df_consolidado_modificado.iterrows():
        id_n = row["Id_N"]
        address = row["Address"]
        nombre_n = row["Nombre_N"]
        nro_ips_totales = row["Size"]
        nro_ips_libres = 0

        url = f"https://10.10.129.41/rest/v1/networks/{id_n}/free_addresses?limit=-1"
        # url = f"https://172.17.1.18/rest/v1/networks/{id_n}/free_addresses?limit=-1"
        # Making a get request to All networks ID's
        response = requests.get(url,
                                verify=False,
                                auth=HTTPBasicAuth('admin', 'password'))

        porcentaje_ips_libres = 0
        if response.status_code == 200:
            try:
                # Obtener las IPs libres desde la respuesta JSON
                ips_libres = json.loads(response.text)
                # obtengo el numero de ips libres
                nro_ips_libres = len(ips_libres)
                # Convertir la dirección de red en un objeto ipaddress.IPv4Network
                red = ipaddress.IPv4Network(address, strict=False)
                # Obtener todas las IPs en el rango de la red
                todas_ips = [str(ip) for ip in red]
                # Filtrar las IPs usadas eliminando las IPs libres
                ips_usadas = [ip for ip in todas_ips if ip not in ips_libres]
                print(f"{index} Las IPs usadas en la red {id_n},{address} son: {len(ips_usadas)}")
            except json.JSONDecodeError:
                print(f"La respuesta para {address} no es un JSON válido.")
        else:
            print(f"Error al obtener datos {address}. Código de estado: {response.status_code}")

        data_list.append({"ID_N": id_n,
                          "ADDRESS": address,
                          "NOMBRE": nombre_n,
                          "NRO_IPS_TOTALES": nro_ips_totales,
                          "NRO_IPS_LIBRES": nro_ips_libres,
                          "NRO_IPS_USADAS": len(ips_usadas),
                          "IPS_USADAS": ips_usadas,
                          "FECHA": fecha_actual
                          })
        df_IpUsado = pd.DataFrame(data_list)

    nombre_archivo_excel = 'ConsumoIPsUsado.xlsx'

    if not os.path.exists(nombre_archivo_excel):

        with pd.ExcelWriter(nombre_archivo_excel, engine='openpyxl', mode='w') as writer:
            df_IpUsado.to_excel(writer, index=False)

    else:
        df_existente = pd.read_excel(nombre_archivo_excel)

        # Concatenar los nuevos datos al DataFrame existente
        df_existente = pd.concat([df_existente, df_IpUsado], ignore_index=True)

        with pd.ExcelWriter(nombre_archivo_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_existente.to_excel(writer, index=False)


if __name__ == '__main__':
    main()



