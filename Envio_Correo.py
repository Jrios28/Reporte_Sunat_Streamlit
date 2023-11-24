import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def enviar_correo(destinatario, asunto, mensaje, adjunto_path):
    # Configuración del servidor SMTP
    smtp_server = 'smtp.gmail.com'
    puerto = 587  # Puerto para TLS

    # Credenciales del remitente
    remitente = 'jrios@electrodata.com.pe'
    contraseña = 'lpyj omag zfqi vocq'

    # Configuración del mensaje
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto

    # Cuerpo del mensaje
    msg.attach(MIMEText(mensaje, 'plain'))

    # Adjuntar el archivo Excel
    with open(adjunto_path, 'rb') as adjunto:
        part = MIMEApplication(adjunto.read())
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(adjunto_path)}"')
        msg.attach(part)

    # Conectar al servidor SMTP y enviar el correo
    with smtplib.SMTP(smtp_server, puerto) as server:
        server.starttls()
        server.login(remitente, contraseña)
        server.sendmail(remitente, destinatario, msg.as_string())

# Ejemplo de uso
destinatario = 'washingtonmayorga@hotmail.com'
asunto = 'Reporte IPAM'
mensaje = 'Hola, adjunto el reporte IPAM correspondiente al dia 23-11-2023.'
adjunto_path = 'D:/Electrodata/11.SUNAT/SunatAPI/ReporteCorreo.xlsx'

enviar_correo(destinatario, asunto, mensaje, adjunto_path)


