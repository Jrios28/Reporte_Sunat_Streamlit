from datetime import datetime
from datetime import date

from Envio_Correo import enviar_correo

today = date.today()
fecha_actual = today.strftime("%Y/%m/%d")





destinatario = ['wmayorga@sunat.gob.pe','jbarbadillo@sunat.gob.pe','cposadas@sunat.gob.pe','fsandoval@electrodata.com.pe','jrios@electrodata.com.pe','ftafur@electrodata.com.pe']
asunto = 'Reporte Segmentos Nuevos'
mensaje = f'Hola, Se ha generado el reporte de Segmentos Nuevos a la fecha de {fecha_actual}.'
adjunto_path = '/home/pc_report/Reporte_Sunat_Streamlit/Consolidado_Segmentos_Red_SUNAT_NUEVOS.csv'
enviar_correo(destinatario, asunto, mensaje, adjunto_path) 



destinatario = ['wmayorga@sunat.gob.pe','jbarbadillo@sunat.gob.pe','cposadas@sunat.gob.pe','fsandoval@electrodata.com.pe','jrios@electrodata.com.pe','ftafur@electrodata.com.pe']
asunto = 'Reporte IPs Libres'
mensaje = f'Hola, Se ha generado el reporte de IPs Libres respecto a la fecha de {fecha_actual}.'
adjunto_path = '/home/pc_report/Reporte_Sunat_Streamlit/ConsumoIPsLibre.xlsx'
enviar_correo(destinatario, asunto, mensaje, adjunto_path) 

#destinatario = 'jrios@electrodata.com.pe,ftafur@electrodata.com.pe,fsandoval@electrodata.com.pe'   
#destinatario = 'jbarbadillo@sunat.gob.pe'
#destinatario = 'jrios@electrodata.com.pe,washingtonmayorga@hotmail.com,ftafur@electrodata.com.pe,fsandoval@electrodata.com.pe,jbarbadillo@sunat.gob.pe,cposadas@sunat.gob.pe'   