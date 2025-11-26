import sqlite3
import datetime
from flask import Flask, request, jsonify
import requests
import json


app = Flask(__name__)
DB_NAME = 'daraja.db'

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daraja_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT,
            trans_id TEXT,
            trans_time TEXT,
            trans_amount REAL,
            business_short_code TEXT,
            bill_ref_number TEXT,
            invoice_number TEXT,
            org_account_balance TEXT,
            third_party_trans_id TEXT,
            msisdn TEXT,
            first_name TEXT,
            middle_name TEXT,
            last_name TEXT,
            received_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/confirmation', methods=['POST'])
def confirmation():
    # Get JSON payload from Daraja
    data = request.get_json()
    received_at = datetime.datetime.now().isoformat()

    # Log or process the incoming data
    print("Received confirmation:", data)

    # Example: Extract key fields (customize based on Daraja payload)
    trans_type = data.get('TransactionType')
    trans_id = data.get('TransID')
    trans_time = data.get('TransTime')

    trans_amount = data.get('TransAmount')
    business_short_code = data.get('BusinessShortCode')
    bill_ref_number = data.get('BillRefNumber')
    invoice_number = data.get('InvoiceNumber')
    org_account_balance = data.get('OrgAccountBalance')
    third_party_trans_id = data.get('ThirdPartyTransID')

    phone = data.get('MSISDN')
    first_name = data.get('FirstName')
    middle_name = data.get('MiddleName')
    last_name = data.get('LastName')
    # Convert metadata list to dictionary
    # meta_dict = {item['Name']: item.get('Value') for item in metadata}

    # Save to SQLite

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO daraja_transactions (
            transaction_type, trans_id, trans_time, trans_amount,
            business_short_code, bill_ref_number, invoice_number,
            org_account_balance, third_party_trans_id, msisdn,
            first_name, middle_name, last_name, received_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trans_type, trans_id, trans_time, trans_amount,
        business_short_code, bill_ref_number, invoice_number,
        org_account_balance, third_party_trans_id, phone,
        first_name, middle_name, last_name, received_at

    ))
    conn.commit()
    conn.close()

    # API endpoint for vending tokens
    url = "http://www.server-newa.stronpower.com/api/VendingMeterDirectly"

    # Replace with your actual credentials and meter details
    payload = {
        "CompanyName": "Samuel",
        "UserName": "Samuel",
        "PassWord": "Samuel123",
        "MeterId": invoice_number,
        "Amount": trans_amount  # Amount to vend
    }

    # Send the POST request
    response = requests.post(url, json=payload)

    # Print the response
    print("Status Code:", response.status_code)
    # print("Response:", response.json())
    # data = response.json()
    # Access the first item and Print specific fields
    if response.status_code == 200:
        print("✅ Token Vended Successfully!")
        token_info = response.json()[0]
        print("Meter ID:", token_info['Meter_id'])
        print("Meter Type:", token_info['Meter_type'])
        print("Token:", token_info['Token'])
        print("Generated Time:", token_info['Gen_time'])
    else:
        print("❌ Failed to vend token. Status Code:", response.status_code)
        print("Response:", response.text)

    token_string = "Meter ID: " + token_info['Meter_id'] + "\n" + "Token: " + token_info['Token'] + "\n" + "Date: " + \
                   token_info['Gen_time']

    # Share the Token as an SMS
    # Replace with your actual credentials
    api_key = '84ecb8bdba9bfbe45d505256dd493884'
    partner_id = '14970'
    shortcode = 'TextSMS'  # e.g., your company name or shortcode
    recipient = phone  # Kenyan mobile number
    message = token_string

    # Prepare the payload
    payload = {
        "apikey": api_key,
        "partnerID": partner_id,
        "message": message,
        "shortcode": shortcode,
        "mobile": recipient
    }

    # Send the request
    url = 'https://sms.textsms.co.ke/api/services/sendsms/'
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Print the response
    print("Status Code:", response.status_code)
    print("Response:", response.json())
    data = response.json()
    description = data['responses'][0]['response-description']
    mobile = data['responses'][0]['mobile']
    messageid = data['responses'][0]['messageid']
    print("Description:", description)
    print("Mobile:", mobile)
    print("Message ID", messageid)






    # Respond with a success message
    return jsonify({
        "ResultCode": 0,
        "ResultDesc": "Confirmation received successfully",
        "TransactionID": trans_id,
        "Amount": trans_amount,
        "Phone": phone
    }), 200

@app.route('/validation', methods=['POST'])
def validation():
    try:
        # Get the incoming JSON payload
        data = request.get_json(force=True)
        print("Validation request received:", data)

        # Respond with acceptance (ResultCode 0 means success)
        return jsonify({
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }), 200
    except Exception as e:
        print("Error in validation:", e)
        return jsonify({
            "ResultCode": 1,
            "ResultDesc": "Failed"
        }), 500
    

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
