import os
import base64
import datetime
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
#app = Flask(__name__)

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
SHORTCODE = os.getenv("SHORTCODE")
PASSKEY = os.getenv("PASSKEY")
CALLBACK_URL = os.getenv("CALLBACK_URL")

OAUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
STK_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

def generate_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")
def get_access_token():
    auth = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}
    res = requests.get(OAUTH_URL, headers=headers)
    return res.json()["access_token"]

def generate_password(timestamp):
    return base64.b64encode(f"{SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()

def normalize_phone(phone):
    if phone.startswith("07"):
        return "254" + phone[1:]
    return phone

@app.route("/pay", methods=["GET"])
def pay():
    phone = normalize_phone("254708374149")  # SANDBOX TEST NUMBER
    amount = 1

    timestamp = generate_timestamp()
    password = generate_password(timestamp)
    token = get_access_token()

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "Test",
        "TransactionDesc": "Test Payment"
    }

    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(STK_URL, json=payload, headers=headers)
    return jsonify(res.json())
if __name__ == "__main__":
    app.run(port=5000, debug=True)
     