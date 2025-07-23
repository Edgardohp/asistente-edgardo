import os
import logging
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

# Configuración de permisos y archivos
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_TELEGRAM = "8095873682:AAFK41nyNGjq4NGJkoj-vrf2E3aGpNHrOQM"

# Estados del flujo de conversación
DESTINATARIO, ASUNTO, CUERPO = range(3)

# Configuración de logs
logging.basicConfig(level=logging.INFO)

# Función para autenticar Gmail
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
    return build('gmail', 'v1', credentials=creds)

# Crear mensaje MIME
def crear_mensaje(destinatario, asunto, cuerpo):
    mensaje = MIMEText(cuerpo, "plain", "utf-8")
    mensaje['to'] = destinatario
    mensaje['subject'] = asunto
    mensaje = {'raw': base64.urlsafe_b64encode(mensaje.as_bytes()).decode('utf-8')}
    return mensaje

# Enviar mensaje
def enviar_mensaje(servicio, mensaje):
    servicio.users().messages().send(userId='me', body=mensaje).execute()

# Comandos del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola Edgardo. ¿A quién deseas enviar el correo?")
    return DESTINATARIO

async def recibir_destinatario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['destinatario'] = update.message.text
    await update.message.reply_text("¿Cuál es el asunto del correo?")
    return ASUNTO

async def recibir_asunto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['asunto'] = update.message.text
    await update.message.reply_text("¿Qué quieres escribir en el cuerpo del mensaje?")
    return CUERPO

async def recibir_cuerpo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    destinatario = context.user_data['destinatario']
    asunto = context.user_data['asunto']
    cuerpo = update.message.text

    servicio = obtener_servicio_gmail()
    mensaje = crear_mensaje(destinatario, asunto, cuerpo)
    enviar_mensaje(servicio, mensaje)

    await update.message.reply_text("✅ Correo enviado correctamente.")
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelado.")
    return ConversationHandler.END

# Ejecutar el bot
def main():
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DESTINATARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_destinatario)],
            ASUNTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_asunto)],
            CUERPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_cuerpo)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
