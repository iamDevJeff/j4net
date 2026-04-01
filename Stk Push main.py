import os, base64, datetime, requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# 1. SETUP & CONFIGURATION
load_dotenv()
app = Flask(__name__)

# Helper to look up .env keys
def get_env(key, default=None):
    return os.getenv(key) or default

CONF = {
    "KEY": get_env("CONSUMER_KEY"),
    "SECRET": get_env("CONSUMER_SECRET"),
    "SHORTCODE": get_env("SHORTCODE"), 
    "PASSKEY": get_env("PASSKEY"),
    "CALLBACK": get_env("CALLBACK_URL")
}

class DarajaBridge:
    _token, _expiry = None, datetime.datetime.min
    @classmethod
    def get_token(cls):
        if datetime.datetime.now() < cls._expiry:
            return cls._token
        
        auth = base64.b64encode(f"{CONF['KEY']}:{CONF['SECRET']}".encode()).decode()
        url = ""
        
        try:
            # Note: verify=True is better, but verify=False is okay for local sandbox testing
            res = requests.get(url, headers={"Authorization": f"Basic {auth}"}, timeout=10).json()
            cls._token = res['']
            expires_in = int(res.get('expires_in', 3599))
            cls._expiry = datetime.datetime.now() + datetime.timedelta(seconds=expires_in - 60)
            return cls._token
        except Exception as e:
            raise RuntimeError(f"OAuth Failure: {str(e)}")

def normalize_phone(p):
    p = str(p).strip().replace("+", "")
    if p.startswith("0"): p = "254" + p[1:]
    if p.startswith("7") or p.startswith("1"): p = "254" + p
    return p

# 2. ROUTES

@app.route("/")
def index():
    """Serves your UI file."""
    return render_template("UI.html")

@app.route("/pay", methods=["POST"])
def initiate_stk():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400

    phone = normalize_phone(data.get("phone", ""))
    amount = int(data.get("amount", 1))

    # Password Generation
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = f"{CONF['SHORTCODE']}{CONF['PASSKEY']}{ts}"
    password = base64.b64encode(data_to_encode.encode()).decode()
    
    payload = {
        "BusinessShortCode": CONF['174379'], 
        "Password": "",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": 254745373340,
        "PartyB": CONF['174379'],
        "PhoneNumber": 254745373340,
        "CallBackURL": " ",
        "AccountReference": "NetPay_Sub",
        "TransactionDesc": "Subscription Payment"
    }
    
    try:
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {DarajaBridge.get_token()}"}
        res = requests.post(url, json=payload, headers=headers, timeout=10000)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": "STK Push Failed", "details": str(e)}), 500

@app.route("/callback", methods=["POST"])
def mpesa_callback():
    data = request.get_json()
    # Safely get result info
    stk_result = data.get('Body', {}).get('stkCallback', {})
    result_code = stk_result.get('ResultCode')
    result_desc = stk_result.get('ResultDesc')
    
    if result_code == 0:
        print(f"SUCCESS: {result_desc}")
    else:
        print(f"FAILED: {result_desc}")
        
    return jsonify({"ResultCode": 0, "ResultDesc": "Success"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
