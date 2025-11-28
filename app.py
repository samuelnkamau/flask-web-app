import sqlite3
import datetime
from flask import Flask, request, jsonify
import requests
import json

import os
import csv
from datetime import datetime

app = Flask(__name__)
#define path for the file
CSV_FILE="TokenRecord.csv"


# Function to write data to CSV
def write_to_csv(data, filename=CSV_FILE):
    # Check if file exists to decide whether to write header
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        # Write header only if file is new
        if not file_exists:
            writer.writeheader()

        # Write the row
        writer.writerow(data)


#header=["Timestamp","Meter ID","Phone","Amount"]


#Data to append
#timestamp = datetime.datetime.now().isoformat()

#file_empty=not os.path.exists(file_name) or os.path.getsize(file_name) == 0

#Append to csv file
# with open(file_name, 'a+', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     if file_empty:
#         writer.writerow(header)
#         writer.writerow([timestamp])
# print("Row appended to Token Record.csv")



@app.route('/confirmation', methods=['POST'])
def confirmation():
    # Get JSON payload from Daraja
    data1 = request.get_json()
    received_at = datetime.now().isoformat()

    # Log or process the incoming data
    print("Received confirmation:", data1)

    # Example: Extract key fields (customize based on Daraja payload)
    trans_type = data1.get('TransactionType')
    trans_id = data1.get('TransID')
    #trans_time = data1.get('TransTime')

    trans_amount = data1.get('TransAmount')
    business_short_code = data1.get('BusinessShortCode')
    bill_ref_number = data1.get('BillRefNumber')
    #invoice_number = data1.get('InvoiceNumber')
    #org_account_balance = data1.get('OrgAccountBalance')
    #third_party_trans_id = data1.get('ThirdPartyTransID')

    phone = data1.get('MSISDN')
    first_name = data1.get('FirstName')
    middle_name = data1.get('MiddleName')
    last_name = data1.get('LastName')
    # Convert metadata list to dictionary
    # meta_dict = {item['Name']: item.get('Value') for item in metadata}





    # API endpoint for vending tokens
    #url = "http://www.server-newa.stronpower.com/api/VendingMeterDirectly"
    url="http://www.server-newa.stronpower.com/api/VendingMeter"

    # Replace with your actual credentials and meter details
    payload = {
        "CompanyName": "Samuel",
        "UserName": "Samuel",
        "PassWord": "Samuel123",
        "MeterID":bill_ref_number,
        "is_vend_by_unit": "true ",
        "Amount":trans_amount
    }

    #}
    # payload = {
    #     "CompanyName": "Samuel",
    #     "UserName": "Samuel",
    #     "PassWord": "Samuel123",
    #     "MeterId": invoice_number,
    #     "Amount": trans_amount  # Amount to vend
    # }

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
        print("Customer_name:", token_info['Customer_name'])
        print("Customer_Phone", token_info['Customer_phone'])
        print("Meter ID:", token_info['Meter_id'])
        print("Meter Type:", token_info['Meter_type'])
        print("Token:", token_info['Token'])
        print("Generated Time:", token_info['Gen_time'])
    else:
        print("❌ Failed to vend token. Status Code:", response.status_code)
        print("Response:", response.text)

    token_string = "Meter ID: " + token_info['Meter_id'] + "\n" + "Token: " + token_info['Token'] + "\n" + "Date: " + \
                   token_info['Gen_time']+"\n"+token_info['Customer_id']

    # Share the Token as an SMS
    # Replace with your actual credentials
    api_key = '84ecb8bdba9bfbe45d505256dd493884'
    partner_id = '14970'
    shortcode = 'TextSMS'  # e.g., your company name or shortcode
    recipient = token_info['Customer_phone'] #phone Kenyan mobile number
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
    data2 = response.json()
    description = data2['responses'][0]['response-description']
    mobile = data2['responses'][0]['mobile']
    messageid = data2['responses'][0]['messageid']
    print("Description:", description)
    print("Mobile:", mobile)
    print("Message ID", messageid)
    try:
        write_to_csv(data1)
        return jsonify({"message": "Data written to CSV successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        #
        # # Respond with a success message
        # return (jsonify({
        #     "ResultCode": 0,
        #     "ResultDesc": "Confirmation received successfully",
        #     "TransactionID": trans_id,
        #     "Amount": trans_amount,
        #     "Phone": phone
        #     }), 200
    return "Confirmation successful", 200  # Explicit HTTP 200 OK


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

#
#
#
# def validation():
#     try:
#         # Get the incoming JSON payload
#         data = request.get_json(force=True)
#         print("Validation request received:", data)
#
#         # Respond with acceptance (ResultCode 0 means success)
#         # return jsonify({
#         #     "ResultCode": 0,
#         #     "ResultDesc": "Accepted"
#         # }), 200
#     except Exception as e:
#         print("Error in validation:", e)
#         return jsonify({
#             "ResultCode": 1,
#             "ResultDesc": "Failed"
#         }), 500
    

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
