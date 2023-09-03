import pymongo
import json


conn_str = "YOUR_CONNECTION_STRING"
myclient = pymongo.MongoClient(conn_str)
mydb = myclient["YOUR_DB_NAME"]
mycol = mydb["YOUR_COLLECTION_NAME"]

a_list = list(mycol.find())

res_list = []

for i in a_list:
    del i["_id"]
    res_list.append(i)
    
print(res_list)

with open('data.json', 'w') as f:
    json.dump(res_list, f)