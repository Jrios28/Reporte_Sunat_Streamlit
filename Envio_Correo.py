import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from datetime import date


def enviar_correo(destinatario, asunto, mensaje, adjunto_path):
    # Configuración del servidor SMTP
    # smtp_server = 'smtp.gmail.com'
    # puerto = 587  # Puerto para TLS

    smtp_server = '192.168.65.183'
    puerto = 25  # Puerto para TLS

    # Credenciales del remitente
    # remitente = 'jrios@electrodata.com.pe'
    # contraseña = 'lpyj omag zfqi vocq'
    remitente = 'infinityreports@sunat.gob.pe'
    contraseña = ''

    # Configuración del mensaje
    message = MIMEMultipart()
    message['From'] = remitente
    message['To'] = ', '.join(destinatario)
    message['Subject'] = asunto

    # Cuerpo del mensaje
    message.attach(MIMEText(mensaje, 'plain'))

    # Adjuntar el archivo Excel
    with open(adjunto_path, 'rb') as adjunto:
        part = MIMEApplication(adjunto.read())
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(adjunto_path)}"')
        message.attach(part)

    # Conectar al servidor SMTP y enviar el correo
    with smtplib.SMTP(smtp_server, puerto) as server:
        # server.starttls()
        # server.login(remitente, contraseña)
        server.sendmail(remitente, destinatario, message.as_string())
    print('Correo electrónico con archivo adjunto enviado exitosamente.')
