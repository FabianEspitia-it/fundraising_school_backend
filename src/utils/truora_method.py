import requests
import os

def send_outbound_message(phone_number, country_code):
    URL = f"{os.getenv('TRUORA_END_POINT')}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Truora-API-Key": os.getenv("TRUORA_API_KEY")}
    data = {
        "phone_number": phone_number,
        "country_code": f'+{country_code}',
        "outbound_id": os.getenv("OUTBOUND_ID"),
        "flow_id": os.getenv("FLOW_ID"),
        "user_authorized": "true"
    }
    response = requests.post(URL, headers=headers, data=data)
    if response.status_code == 200:
        return {"status": "success", "details": response.json()}
    else:
        return {"status": "error", "details": response.text}

