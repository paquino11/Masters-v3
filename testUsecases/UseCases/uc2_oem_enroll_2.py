import requests
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
sys.path.append('/home/pedro/Desktop/Masters-v3/testUsecases/')  # Add the path to the directory containing test.py
import test_framework_v2 as tfv2
import datetime
import time


CRED_FORMAT_INDY = "indy"
CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/2.0/credential-preview"

def generate_credential_offer(self, aip, cred_type, cred_def_id, exchange_tracing):
    age = 24
    d = datetime.date.today()
    birth_date = datetime.date(d.year - age, d.month, d.day)
    birth_date_format = "%Y%m%d"
    if aip == 10:
        # define attributes to send for credential
        self.cred_attrs[cred_def_id] = {
            "name": "Alice Smith",
            "date": "2018-05-28",
            "degree": "Maths",
            "birthdate_dateint": birth_date.strftime(birth_date_format),
            "timestamp": str(int(time.time())),
        }

        cred_preview = {
            "@type": CRED_PREVIEW_TYPE,
            "attributes": [
                {"name": n, "value": v}
                for (n, v) in self.cred_attrs[cred_def_id].items()
            ],
        }
        offer_request = {
            "connection_id": self.connection_id,
            "cred_def_id": cred_def_id,
            "comment": f"Offer on cred def id {cred_def_id}",
            "auto_remove": False,
            "credential_preview": cred_preview,
            "trace": exchange_tracing,
        }
        return offer_request

    elif aip == 20:
        if cred_type == CRED_FORMAT_INDY:
            self.cred_attrs[cred_def_id] = {
                "name": "Alice Smith",
                "date": "2018-05-28",
                "degree": "Maths",
                "birthdate_dateint": birth_date.strftime(birth_date_format),
                "timestamp": str(int(time.time())),
            }

            cred_preview = {
                "@type": CRED_PREVIEW_TYPE,
                "attributes": [
                    {"name": n, "value": v}
                    for (n, v) in self.cred_attrs[cred_def_id].items()
                ],
            }
            offer_request = {
                "connection_id": self.connection_id,
                "comment": f"Offer on cred def id {cred_def_id}",
                "auto_remove": False,
                "credential_preview": cred_preview,
                "filter": {"indy": {"cred_def_id": cred_def_id}},
                "trace": exchange_tracing,
            }
            return offer_request


        else:
            raise Exception(f"Error invalid credential type: {self.cred_type}")

    else:
        raise Exception(f"Error invalid AIP level: {self.aip}")


def step1(dave_inv):
    print("\nStep 1- D:1 makes an introduction using Aries RFC0028 to O:1 passing the OOB along with goal code. ")
    #get consortium pub did
    url = 'http://0.0.0.0:8181/wallet/did/public'
    headers = { 'accept': 'application/json' }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        #print(response_data)
        pub_did = response_data["result"]["did"]
    else:
        return response.status_code
    
    #send consortium pub did from dave to oem egw
    url = f'http://0.0.0.0:8201/connections/{dave_inv}/send-message'
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    data = {"content": pub_did}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        #print("Message sent successfully")
        return pub_did
    else:
        #print("Failed to send message")
        print("Response:", response.text)

def step2(cons_pub_did):
    print("\nStep 2- O:1 uses the OOB to connect to C:1. ")
    #Implicit invitation from oem egw to consortium
    url = 'http://0.0.0.0:8061/didexchange/create-request'
    params = { 'their_public_did': cons_pub_did }
    headers = { 'accept': 'application/json' }

    response = requests.post(url, params=params, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        #print("Request failed with status code:", response.status_code)
        #print("Response content:", response.text)
        return response.status_code

def step3():
    print("\nStep 3- C:1 recognizes the goal code UUID and recognizes it refers to the ongoing OEM enrollment and updates the previously entered Agent Table with the OEM’s public DID. ")
    #get oem pub did
    url = 'http://0.0.0.0:8061/wallet/did/public'
    headers = { 'accept': 'application/json' }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        #print(response_data)
        oem_pub_did = response_data["result"]["did"]
    else:
        return response.status_code
    
    dbname = "postgres"
    user = "postgres"
    password = "mysecretpassword"
    host = "localhost"
    port = "5432"

    try:
        connection = psycopg2.connect( dbname=dbname,user=user,password=password,host=host,port=port)
        #print("Connection established successfully!")

        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS agent_table (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent TEXT
            )
        """)
        cursor.execute(create_table_query)
        insert_query = sql.SQL("""
            INSERT INTO agent_table (agent)
            VALUES (%s)
        """)
        connection_value = oem_pub_did
        cursor.execute(insert_query, (connection_value,))
        connection.commit()

        cursor.close()

    except psycopg2.Error as e:
        print("Error:", e)

    finally:
        if connection:
            connection.close()
            #print("Connection closed.")

def step4():
    print("\nStep 4- C:1 proposes O:1 the Enrollment VC which defines the proofs (e.g., documents) O:1 must submit so C:1 can assess the OEM trustworthiness. ")
    offer_request = generate_credential_offer(
                                20,
                                CRED_FORMAT_INDY,
                                "",
                                False,
                            )
    
def step5():
    print("\nStep 5- O:1 provides the proofs to C:1. ")

def step6():
    print("\nStep 6- Upon validating the submitted proofs, C:1 sends a message to O:1 to generate its ecosystem ledger credentials. ")


def step7():
    print("\nStep 7- O:1 requests the consortium a X.509 certificate. ")

def step8():
    print("\nStep 8- O:1 makes an enrollment request. ")

def step9():
    print("\nStep 9- O:1 sends an acknowledgment to C:1 to indicate ledger successful enrollment. ")

def step10():
    print("\nStep 10- C:1 sends the “Enrollment VC” to O:1 and expires the OOB. ")


def main(dave_inv):
    cons_pub_did = tfv2.time_execution(step1, dave_inv)
    tfv2.time_execution(step2, cons_pub_did)
    tfv2.time_execution(step3)
    tfv2.time_execution(step4)
    tfv2.time_execution(step5)
    tfv2.time_execution(step6)
    tfv2.time_execution(step7)
    tfv2.time_execution(step8)
    tfv2.time_execution(step9)
    tfv2.time_execution(step10)


if __name__ == "__main__":
    main()