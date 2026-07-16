from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import requests
import uvicorn
import os

app = FastAPI()

# ==========================
# Azure App Registration
# ==========================

CLIENT_ID = "255aa5ef-a176-4c97-ab87-3161190fc46c"
CLIENT_SECRET = "YNN8Q~BilYhDkR19_8FexXlx5cemr.X.dOwl8aIy"
TENANT_ID = "1c057d6e-b484-4389-9806-e7ee92872103"

REDIRECT_URI = "https://mail-sender-i1l3.onrender.com/auth/callback"

SCOPES = [
    "openid",
    "profile",
    "offline_access",
    "User.Read",
    "Mail.Send"
]

AUTH_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
GRAPH_URL = "https://graph.microsoft.com/v1.0/me/sendMail"

access_token = None
refresh_token = None


@app.get("/")
def home():
    return {
        "status": "Server Running"
    }


@app.get("/login")
def login():

    scope = " ".join(SCOPES)

    url = (
        f"{AUTH_URL}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_mode=query"
        f"&scope={scope}"
    )

    return RedirectResponse(url)


@app.get("/auth/callback")
def callback(code: str):

    global access_token
    global refresh_token

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES)
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(
        TOKEN_URL,
        data=payload,
        headers=headers
    )

    print("\n========== TOKEN RESPONSE ==========\n")
    print(response.text)

    token = response.json()

    # Authentication failed
    if "access_token" not in token:

        return {
            "status": "Authentication Failed",
            "azure_response": token
        }

    access_token = token["access_token"]
    refresh_token = token.get("refresh_token")

    mail_result = send_mail()

    return {
        "status": "Authentication Successful",
        "mail_result": mail_result
    }


def send_mail():

    global access_token

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "message": {
            "subject": "Microsoft Graph API Test",
            "body": {
                "contentType": "Text",
                "content": "Hello! This is a test email sent using Microsoft Graph API from Render."
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "recipient@example.com"
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

    print("\n========== SEND MAIL ==========\n")
    print("Status Code:", response.status_code)
    print("Response:", response.text)

    if response.status_code == 202:

        return "Mail Sent Successfully"

    return {
        "status_code": response.status_code,
        "response": response.text
    }


if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
