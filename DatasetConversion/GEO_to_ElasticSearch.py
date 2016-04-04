# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 10:36:05 2016

@author: cbdavis
"""

import sqlite3
import urllib
import json

# get (hopefully) the latest sqlite database
dbURL = "https://morph.io/coroa/global_energy_observatory_power_plants/data.sqlite?key=RopNCJ6LtIx9%2Bdp1r%2BQV"
urllib.urlretrieve (dbURL, "data.db")

# check the name here
conn = sqlite3.connect("data.db")
conn.text_factory = str
c = conn.cursor()

c.execute("SELECT * FROM powerplants")
colnames = list(map(lambda x: x[0], c.description))
rows = c.fetchall()                
count = 0
for row in rows:
    count += 1
    print count
    # ignore 'None'
    data = {}
    for i in range(len(row)):
        if row[i] != None:
            data[colnames[i]] = row[i]
    
    if data.has_key("Saved_Latitude_Start") and data.has_key("Saved_Longitude_Start"):
        data["location"] = str(data["Saved_Latitude_Start"]) + ", " + str(data["Saved_Longitude_Start"])
    
    jsonarray = json.dumps(data)

    # check if valid page
    if data.has_key("Description_ID"):
        with open("GeoElasticSearchBulkImport.json", "a") as f_ElasticSearchBulkImport:
            f_ElasticSearchBulkImport.write('{ "create" : { "_index" : "geo", "_type" : "powerplant", "_id" : ' + data["Description_ID"] + ' } }\n')
            f_ElasticSearchBulkImport.write(jsonarray + "\n")



c.execute("SELECT * FROM ppl_units")
colnames = list(map(lambda x: x[0], c.description))
rows = c.fetchall()                
count = 0
for row in rows:
    count += 1
    print count
    # ignore 'None'
    data = {}
    for i in range(len(row)):
        if row[i] != None:
            data[colnames[i]] = row[i]
    
    jsonarray = json.dumps(data)

    # check if valid page
    if data.has_key("GEO_Assigned_Identification_Number") and data.has_key("Unit_Nbr"):
        with open("GeoElasticSearchBulkImport.json", "a") as f_ElasticSearchBulkImport:
            f_ElasticSearchBulkImport.write('{ "create" : { "_index" : "geo", "_type" : "ppl_unit", "_id" : ' + data["GEO_Assigned_Identification_Number"] + '_' + data["Unit_Nbr"] + ' } }\n')
            f_ElasticSearchBulkImport.write(jsonarray + "\n")

