import pymongo
import json
import ipfsApi
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests


load_dotenv()

# General configs
MONGO_DB_CLIENT = "docker_mongodb_1:27017"#os.environ.get("MONGO_DB_CLIENT", "docker_mongodb_1:27017")
IPFS_CLIENT = "ipfs"#os.environ.get("IPFS_CLIENT", "ditto-ipfs")
IPFS_CLIENT_PORT = 5002#os.environ.get("IPFS_CLIENT_PORT", 5001)

# IPFS configssd
try:
    ipfs = ipfsApi.Client(IPFS_CLIENT, IPFS_CLIENT_PORT)
    print("Connection to IPFS client was established successfully!")
    # You can now use the 'ipfs' object to interact with IPFS, e.g., ipfs.cat(), ipfs.add(), etc.
except Exception as e:
    print("Connection to IPFS client failed. Error:", str(e))


# Eclipse Ditto MongoDB configs
mongoClient = pymongo.MongoClient(f"mongodb://{MONGO_DB_CLIENT}")
database = mongoClient["things"]
collection = database["things_journal"]

def save_ditto_things_ipfs():
    last_hour_things = ditto_data_to_file()
    ipfs_responses = things_data_to_ipfs()
    print(f"{ datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {len(last_hour_things)} entries -> {ipfs_responses}")
    first_hash = ipfs_responses[0]['Hash']
    save_ipfs_hash_on_fabric(first_hash)


def save_ipfs_hash_on_fabric(ipfs_hash):
    url = "http://fabric-gateway:3025/regdataset"
    payload = {"string": ipfs_hash}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Hash sent successfully to Fabric!")
    else:
        print("Failed to send string to the server.")


def get_last_hour_things():
    last_hour = datetime.utcnow() - timedelta(hours=1)
    query = { "events": { "$elemMatch": { "p._timestamp": { "$gte": last_hour.strftime("%Y-%m-%d %H:%M:%S") } } } }
    pipeline = [
        { '$match': query },
        { '$group': { '_id': '$pid', 'docs': { '$push': '$$ROOT' } } },
        { '$project': { '_id': '$_id', 'documents': '$docs' } }
    ]
    return collection.aggregate(pipeline=pipeline)

def ditto_data_to_file():
    last_hour_things = list(map(map_mongo_thing, get_last_hour_things()))

    for thing in last_hour_things:
        print(thing["thingId"])
        with open(f"{thing['thingId']}.json", "w") as f:
            json.dump(thing, f)

    print('Mongo Data to file done')
    return last_hour_things

def things_data_to_ipfs():
    print(ipfs.id)
    ipfs_responses = []
    directory = '.'
    for filename in os.listdir('.'):
        if os.path.isfile(os.path.join(directory, filename)):
            if filename.endswith('.json'):
                ipfs_response = ipfs.add(filename)
                print(f"{filename} ---> {ipfs_response}")
                ipfs_responses.append(ipfs_response)
                ipfs.pin_rm
    return ipfs_responses

def map_mongo_thing(mongo_thing):
    return {
        "thingId": mongo_thing["_id"],
        "definition": map_mongo_definition(mongo_thing["documents"]),
        "results": map_mongo_attributes(mongo_thing["documents"])
    }

def map_mongo_attributes(documents):
    results = []
    for entry in documents:
        for event in entry["events"]:
            thing = event["p"]["thing"]
            results.append({
                "timestamp": event["p"]["_timestamp"],
                "attributes": thing["attributes"]
            })
    return results

def map_mongo_definition(documents):
    return documents[0]["events"][0]["p"]["thing"]["definition"]
