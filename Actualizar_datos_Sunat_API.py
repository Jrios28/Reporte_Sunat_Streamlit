import pandas as pd
from Apis.Api_Segmento_Red import obtener_datos_de_segmento_red, obtener_datos_de_cdc

def main():
    
    df_origen = pd.read_csv("Consolidado_Segmentos_Red_SUNAT.csv", sep=',')
    #df_nuevo = obtener_datos_de_segmento_red()
    df_nuevo = pd.read_csv('Consolidado_Segmentos_Red_SUNAT_NUEVO.csv', sep=',')

    df_final, df_eliminados = obtener_datos_de_cdc(df_origen,df_nuevo)

    df_final.to_csv("Consolidado_Segmentos_Red_SUNAT.csv",index=False)
    df_eliminados.to_csv("Consolidado_Segmentos_Red_SUNAT_ELIMINADOS.csv",index=False)

if __name__ == '__main__':
    main()
