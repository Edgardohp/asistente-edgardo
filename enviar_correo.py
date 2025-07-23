import os
from email.mime.text import MIMEText
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 🔐 Permiso necesario: lectura y envío de correos
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = 'credentials.json'

def obtener_servicio_gmail():
    creds = None
    token_file = 'token.json'

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    servicio = build('gmail', 'v1', credentials=creds)
    return servicio

def crear_mensaje(destinatario, asunto, cuerpo):
    mensaje = MIMEText(cuerpo, "plain", "utf-8")
    mensaje['to'] = destinatario
    mensaje['subject'] = asunto
    mensaje = {'raw': base64.urlsafe_b64encode(mensaje.as_bytes()).decode('utf-8')}
    return mensaje

def enviar_mensaje(servicio, mensaje):
    resultado = servicio.users().messages().send(userId='me', body=mensaje).execute()
    print(f"✅ Correo enviado. ID del mensaje: {resultado['id']}")

# 💬 Aquí defines los datos del mensaje
destinatario = input("¿A quién deseas enviar el correo? (ejemplo@gmail.com): ")
asunto = input("¿Cuál es el asunto del correo?: ")
cuerpo = input("¿Qué deseas escribir en el cuerpo del mensaje?: ")

servicio = obtener_servicio_gmail()
mensaje = crear_mensaje(destinatario, asunto, cuerpo)
enviar_mensaje(servicio, mensaje)
