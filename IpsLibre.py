import pandas as pd
import urllib3
import numpy as np
from datetime import datetime
from datetime import date
import requests
from requests.auth import HTTPBasicAuth
import json

urllib3.disable_warnings()

def main():
    df_consolidado = pd.read_csv('Consolidado_Segmentos_Red_SUNAT.csv')
    data_list = []
    for index, row in df_consolidado.iterrows():
        address = row["Address"]
        id_n = row["Id_N"]
        nombre_n = row["Nombre_N"]
        nro_ips_totales = int(row["Size"])

        url = f"https://10.10.129.41/rest/v1/networks/{id_n}/free_addresses"
        # url = f'https://172.17.1.18/rest/v1/networks/{id_n}/free_addresses'
        # Making a get request to All networks ID's
        response = requests.get(url,
                                verify=False,
                                auth=HTTPBasicAuth('admin', 'password'))
        response
        datos_free = json.loads(response.text)
        # obtengo el numero de ips libres
        nro_ips_libres = len(datos_free)

        # Calcular el porcentaje
        porcentaje_ips_libres = (nro_ips_libres / nro_ips_totales) * 100

        # Imprimir el resultado
        print(f"El {porcentaje_ips_libres:.2f}% de las IPs correspondiente al segmento de red {address} están libres.")
        data_list.append({"ID_N": id_n,
                          "ADDRESS": address,
                          "NOMBRE": nombre_n,
                          "NRO_IPS_TOTALES": nro_ips_totales,
                          "NRO_IPS_LIBRES": nro_ips_libres,
                          "PORCENTAJE_IPS_LIBRES": round(porcentaje_ips_libres, 2)
                          })
        df_IpLibres = pd.DataFrame(data_list)

    # Agregar el símbolo de porcentaje a la columna 'Porcentaje'
    df_IpLibres['PORCENTAJE_IPS_LIBRES'] = df_IpLibres['PORCENTAJE_IPS_LIBRES'].astype(str) + '%'
    #df_IpLibres

    #Obtengo Formato para colocar el nombre en el sheet
    today = date.today()
    fechaFormat = today.strftime("%Y%m%d")
    #print(fechaFormat)

    # Nombre del archivo Excel
    nombre_archivo_excel = 'ConsumoIPsLibre.xlsx'
    sheet1 = f'IpsLibres_{fechaFormat}'

    df_existente = pd.DataFrame()
    df_existente.to_excel(nombre_archivo_excel, sheet_name=sheet1, index=False)

    # Concatenar los nuevos datos al DataFrame existente
    df_existente = pd.concat([df_existente, df_IpLibres], ignore_index=True)

    # Guardar el DataFrame actualizado en el Sheet1 del archivo Excel
    with pd.ExcelWriter(nombre_archivo_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_existente.to_excel(writer, sheet_name=sheet1, index=False)


if __name__ == '__main__':
    main()