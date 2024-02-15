from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = 'hazel-champion-260900-45b15d119d31.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

async def update_google_sheet(self) -> None:
    SPREADSHEET_ID = '1yRn4JSI0O-lmI2Mklw_PJn2yb7SK0XKjYv2CuKLcVBE'
    RANGE_NAME = 'Sheet1!A2:B' 
    values = []
    for uid, choice in self.user_choices.items():
        user = self.client.get_user(uid) 
        if user:
            values.append([user.display_name, choice])

    body = {'values': values}

    batch_update_body = {
        'valueInputOption': 'RAW',
        'data': [
            {'range': RANGE_NAME, 'values': values}
        ]
    }

    service.spreadsheets().values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=batch_update_body).execute()