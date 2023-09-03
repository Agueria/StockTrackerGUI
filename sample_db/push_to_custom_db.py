import pymongo
import json


conn_str = "YOUR_CONNECTION_STRING"
myclient = pymongo.MongoClient(conn_str)
mydb = myclient["YOUR_DB_NAME"]
mycol = mydb["YOUR_COLLECTION_NAME"]

with open('data.json') as file:
    file_data = json.load(file)
    for i in file_data:
        mycol.insert_one(i)
        print(i)
print("done")
