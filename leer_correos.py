import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import OpenAI

load_dotenv()

GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

creds = Credentials(
    token=None,
    refresh_token=GOOGLE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scopes=SCOPES
)

service = build('gmail', 'v1', credentials=creds)

results = service.users().messages().list(userId='me', maxResults=5).execute()
messages = results.get('messages', [])

cuerpos = []
for message in messages:
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    payload = msg['payload']
    parts = payload.get('parts', [])
    data = ""

    if 'data' in payload['body'] and payload['body']['data']:
        data = payload['body']['data']
    elif parts:
        for part in parts:
            if 'body' in part and 'data' in part['body']:
                data = part['body']['data']
                break

    if data:
        try:
            cuerpo = base64.urlsafe_b64decode(data).decode('utf-8')
            cuerpos.append(cuerpo)
        except:
            cuerpos.append("(No se pudo decodificar el mensaje)")

prompt = "Resume los siguientes correos:\n\n" + "\n\n".join(cuerpos)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

print("Resumen de correos:")
print(response.choices[0].message.content)
