from fastapi import FastAPI
import requests
import uvicorn
import os

app = FastAPI()

# ==========================================
# Azure App Registration
# ==========================================

CLIENT_ID = "255aa5ef-a176-4c97-ab87-3161190fc46c"
CLIENT_SECRET = "YNN8Q~BilYhDkR19_8FexXlx5cemr.X.dOwl8aIy"
TENANT_ID = "1c057d6e-b484-4389-9806-e7ee92872103"

# Sender mailbox
SENDER_EMAIL = "sanket.gardi@cotmac.io"

# Recipient mailbox
RECIPIENT_EMAIL = "cepl.neo@cotmac.io"

TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

GRAPH_URL = f"https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail"


@app.get("/")
def home():
    return {
        "status": "Server Running",
        "endpoint": "/send-mail"
    }


def get_access_token():

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default"
    }

    response = requests.post(TOKEN_URL, data=payload)

    print("========== TOKEN RESPONSE ==========")
    print(response.status_code)
    print(response.text)

    token = response.json()

    if "access_token" not in token:
        return None, token

    return token["access_token"], None


@app.get("/send-mail")
def send_mail():

    access_token, error = get_access_token()

    if error:
        return {
            "status": "Token Generation Failed",
            "details": error
        }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "message": {
            "subject": "Mail from Microsoft Graph",
            "body": {
                "contentType": "Text",
                "content": "Hello! This email was sent using Microsoft Graph Application Permission from Render."
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": RECIPIENT_EMAIL
                    }
                }
            ]
        },
        "saveToSentItems": True
    }

    response = requests.post(
        GRAPH_URL,
        headers=headers,
        json=body
    )

    print("========== SEND MAIL ==========")
    print(response.status_code)
    print(response.text)

    if response.status_code == 202:
        return {
            "status": "Success",
            "message": "Mail Sent Successfully"
        }

    return {
        "status": "Failed",
        "status_code": response.status_code,
        "response": response.text
    }


if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
