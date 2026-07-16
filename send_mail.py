from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import requests
import webbrowser
import threading
import uvicorn

app = FastAPI()

# ==========================
# Azure App Registration
# ==========================

CLIENT_ID = "255aa5ef-a176-4c97-ab87-3161190fc46c"

CLIENT_SECRET = "YNN8Q~BilYhDkR19_8FexXlx5cemr.X.dOwl8aIy"

TENANT_ID = "1c057d6e-b484-4389-9806-e7ee92872103"

REDIRECT_URI = "http://localhost:8000/auth/callback"

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
    return {"status": "Server Running"}


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

    token = response.json()

    print("\n========== TOKEN RESPONSE ==========\n")
    print(token)

    access_token = token["access_token"]
    refresh_token = token["refresh_token"]

    send_mail()

    return {
        "message": "Authentication Successful. Mail Sent.",
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def send_mail():

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "message": {
            "subject": "Microsoft Graph API Test",
            "body": {
                "contentType": "Text",
                "content": "Hello! This is a test email sent using Microsoft Graph API."
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "sanket.gardi@cotmac.io"
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
    print(response.status_code)

    if response.text:
        print(response.text)
    else:
        print("Mail Sent Successfully")


def open_browser():
    webbrowser.open("http://localhost:8000/login")


if __name__ == "__main__":

    threading.Timer(1, open_browser).start()

    uvicorn.run(
        app,
        host="localhost",
        port=8000
    )
