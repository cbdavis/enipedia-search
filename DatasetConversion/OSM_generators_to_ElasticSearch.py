#!/usr/bin/python

import urllib
import urllib2
from zipfile import ZipFile
from StringIO import StringIO
import json
import os
from collections import defaultdict

# Take care of silly unicode issues.  Why is ASCII the default?
import sys
reload(sys)  # need to reload
sys.setdefaultencoding('UTF8')

from lxml import etree
import sys

myfile="ElasticSearchBulkImport.json"
## if file exists, delete it ##
if os.path.isfile(myfile):
        os.remove(myfile)

# download latest file from Enipedia
url = urllib2.urlopen("http://enipedia.tudelft.nl/OpenStreetMap/PlanetPowerGenerators.zip")
#url = urllib2.urlopen("http://enipedia.tudelft.nl/OpenStreetMap/GermanyPowerGenerators.zip")
zipfile = ZipFile(StringIO(url.read()))

#context = etree.iterparse(zipfile.open("PlanetPowerGenerators.osm"), events=('end',), tag=('node', 'way', 'relation'))
context = etree.iterparse(zipfile.open("GermanyPowerGenerators.osm"), events=('end',), tag=('node', 'way', 'relation'))
# testing
#context = etree.iterparse("/home/cdavis/ElasticSearch/PlanetPowerGenerators.osm", events=('end',), tag='node')


# make two passes over the file - the first needs to figure out the coordinates for the ways and relations
nodeLat = {}
nodeLon = {}

# find the connections between the objects
# this is needed in order by find the centroids of the objects
wayNodeLookup = defaultdict()
relationNodeLookup = defaultdict()
relationWayLookup = defaultdict()

for action, elem in context:
        type = elem.tag

        if type in ('node'):
		objectID = elem.xpath("./@id")[0]
		lat = elem.xpath("./@lat")[0]
		lon = elem.xpath("./@lon")[0]

		nodeLat[objectID] = lat
		nodeLon[objectID] = lon

        elif type in ('way'):
		objectID = elem.xpath("./@id")[0]
		nodes = elem.xpath("./nd/@ref")

		for node in nodes:
			wayNodeLookup.setdefault(objectID, []).append(node)

        elif type in ('relation'):
		objectID = elem.xpath("./@id")[0]
		nodes = elem.xpath("./member[@type='node']/@ref")
		ways = elem.xpath("./member[@type='way']/@ref")

		for node in nodes:
			relationNodeLookup.setdefault(objectID, []).append(node)

		for way in ways:
			relationWayLookup.setdefault(objectID, []).append(way)

        elem.clear()

        while elem.getprevious() is not None:
                del elem.getparent()[0]

#print "nodeLat : %d" % len (nodeLat)
#print "nodeLon : %d" % len (nodeLon)
#print "wayNodeLookup : %d" % len (wayNodeLookup)
#print "relationNodeLookup : %d" % len (relationNodeLookup)
#print "relationWayLookup : %d" % len (relationWayLookup)

wayLat = {}
wayLon = {}
relationLat = {}
relationLon = {}

# get the centroid for the ways
for way in wayNodeLookup:
	nodeCount = len(wayNodeLookup[way])
	latSum = 0.0
	lonSum = 0.0
	for node in wayNodeLookup[way]:
		if node in nodeLat: # make sure that we have the coordinates
			latSum = latSum + float(nodeLat[node])
			lonSum = lonSum + float(nodeLon[node])

	latCentroid = latSum/nodeCount
	lonCentroid = lonSum/nodeCount
	wayLat[way] = latCentroid
	wayLon[way] = lonCentroid

# get the centroid for the relations
# create a unique list of relations - these could have either nodes or ways or a combination of both
relations = set(relationWayLookup.keys())
relations.update(set(relationNodeLookup.keys()))

for relation in relations:
	latSum = 0.0
	lonSum = 0.0
	nodeCount = 0
	# get all the ways associated with this relation
	if relation in relationWayLookup:
		ways = relationWayLookup[relation]
		for way in ways:
			if way in wayNodeLookup:
				nodeCount += len(wayNodeLookup[way])
				# get all the nodes associated with this way
				for node in wayNodeLookup[way]:
					if node in nodeLat: # make sure that we have the coordinates
						latSum = latSum + float(nodeLat[node])
						lonSum = lonSum + float(nodeLon[node])
	
	# get all the nodes associated with this relation
	if relation in relationNodeLookup:
		nodes = relationNodeLookup[relation]
		nodeCount += len(nodes)
		for node in wayNodeLookup[way]:
			if node in nodeLat: # make sure that we have the coordinates
				latSum = latSum + float(nodeLat[node])
				lonSum = lonSum + float(nodeLon[node])


	latCentroid = latSum/nodeCount
	lonCentroid = lonSum/nodeCount

	relationLat[relation] = latCentroid
	relationLon[relation] = lonCentroid

# re-open the file
context = etree.iterparse(zipfile.open("GermanyPowerGenerators.osm"), events=('end',), tag=('node', 'way', 'relation'))

for action, elem in context:
        type = elem.tag

	if elem.tag == "node":
	        #if type in ('node'):
		objectID = elem.xpath("./@id")[0]
		data = {}
		# just grab all of the attributes
		if elem.attrib:
			for attrName, attrValue in elem.attrib.items():
				data[attrName] = attrValue

		tags = elem.xpath("./tag")

		for tag in tags:
			if tag.attrib:
				key = tag.xpath("./@k")[0]
				value = tag.xpath("./@v")[0]
				data[key] = value

		jsonarray = json.dumps(data)

		with open("ElasticSearchBulkImport.json", "a") as f_ElasticSearchBulkImport:
			f_ElasticSearchBulkImport.write('{ "create" : { "_index" : "osm", "_type" : "node", "_id" : ' + objectID + ' } }\n')
			f_ElasticSearchBulkImport.write(jsonarray + "\n")

        #elif type in ('way'):
	elif elem.tag == "way":
		objectID = elem.xpath("./@id")[0]
		nodes = elem.xpath("./nd/@ref")

		data = {}
		# just grab all of the attributes
		if elem.attrib:
			for attrName, attrValue in elem.attrib.items():
				data[attrName] = attrValue

		tags = elem.xpath("./tag")

		for tag in tags:
			if tag.attrib:
				key = tag.xpath("./@k")[0]
				value = tag.xpath("./@v")[0]
				data[key] = value

		# add in lat/lon based on centroid calculations above
		if objectID in wayLat:
			data["lat"] = wayLat[objectID]
			data["lon"] = wayLon[objectID]

		jsonarray = json.dumps(data)

		with open("ElasticSearchBulkImport.json", "a") as f_ElasticSearchBulkImport:
			f_ElasticSearchBulkImport.write('{ "create" : { "_index" : "osm", "_type" : "way", "_id" : ' + objectID + ' } }\n')
			f_ElasticSearchBulkImport.write(jsonarray + "\n")


	#elif type in ('relation'):
	elif elem.tag == "relation":
		objectID = elem.xpath("./@id")[0]
		nodes = elem.xpath("./member[@type='node']/@ref")
		ways = elem.xpath("./member[@type='way']/@ref")

		data = {}
		# just grab all of the attributes
		if elem.attrib:
			for attrName, attrValue in elem.attrib.items():
				data[attrName] = attrValue

		tags = elem.xpath("./tag")

		for tag in tags:
			if tag.attrib:
				key = tag.xpath("./@k")[0]
				value = tag.xpath("./@v")[0]
				data[key] = value

		# add in lat/lon based on centroid calculations above
		if objectID in relationLat:
			data["lat"] = relationLat[objectID]
			data["lon"] = relationLon[objectID]

		jsonarray = json.dumps(data)

		with open("ElasticSearchBulkImport.json", "a") as f_ElasticSearchBulkImport:
			f_ElasticSearchBulkImport.write('{ "create" : { "_index" : "osm", "_type" : "relation", "_id" : ' + objectID + ' } }\n')
			f_ElasticSearchBulkImport.write(jsonarray + "\n")

        elem.clear()

        while elem.getprevious() is not None:
                del elem.getparent()[0]

