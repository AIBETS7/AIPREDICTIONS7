import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuración
SHEET_ID = '1kEeQt-8uj09wZNHYqd8KFzQ6Yn4RCh9psVYtBH3JBEE'
CREDENTIALS_FILE = 'suscripciones-ai-predictions-f37a5a661efb.json'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def log_payment(email, bot, fecha=None):
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.sheet1  # Primera hoja
    if fecha is None:
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Añadir fila: [fecha, email, bot]
    worksheet.append_row([fecha, email, bot], value_input_option='USER_ENTERED') 