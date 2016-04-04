enipedia-search
===============

## What?
This is the web page code that is used for http://enipedia.tudelft.nl/Elasticsearch.html.  The main motivation is that data for global power plants is not published using a standardized format.  Data that is relevant for a single plant may be distributed across multiple databases which do not (re)use standard identifiers.  The interface below has been created to help deal with this situation by allowing one to easily search across multiple databases that may contain relevant data.  

<a href="http://enipedia.tudelft.nl/Elasticsearch.html"><img src=EnipediaSearch.png></a>

This isn't just for the humans, and you can send API requests as well to http://enipedia.tudelft.nl/search.  
Behind the scenes, [Elasticsearch](https://www.elastic.co) is used, and you can use their [documentation](https://www.elastic.co/guide/index.html) to help create your own queries.

## Available Databases
* `carmav2` - Version 2 of the dataset collected by http://carma.org
* `carmav3` - Version 3 of the dataset collected by http://carma.org
* `eprtr` - [European Pollutant Release and Transfer Register](http://prtr.ec.europa.eu/#/home)
* `euets` - European Union Emissions Trading System
* `osm` - OpenStreetMap - everything tagged as "[power=generator](http://wiki.openstreetmap.org/wiki/Tag:power%3Dgenerator)", updated daily
* `wikipedia` - Wikipedia articles about power plants, updated daily via https://github.com/cbdavis/wikipedia-power-plants
* `geo` - [Global Energy Observatory](globalenergyobservatory.org) via scraper at https://morph.io/coroa/global_energy_observatory_power_plants
* `lcpd` - [Large Combustion Plant Directive](https://en.wikipedia.org/wiki/Large_Combustion_Plant_Directive)

In the examples below, you'll see URLs such as `http://enipedia.tudelft.nl/search/geo,osm,wikipedia/_search`, which indicate that the `geo`, `osm`, and `wikipedia` databases are to be searched.  You can add or remove these to search over as few or as many databases as you want.

## Examples

### Search for "Maasvlakte" using Common Terms Query
```
curl -H "Content-Type: application/json" -X POST -d '{
  "from": 0,
  "size": "10",
  "query": {
    "common": {
      "_all": {
        "query": "Maasvlakte",
        "cutoff_frequency": 0.001
      }
    }
  }
}' http://enipedia.tudelft.nl/search/geo,osm,wikipedia/_search
```

### Search for "Maasvlakte" using Fuzzy Like This query
```
curl -H "Content-Type: application/json" -X POST -d '{
  "from": 0,
  "size": "10",
  "query": {
    "fuzzy_like_this": {
      "like_text": "Maasvlakte"
    }
  }
}' http://enipedia.tudelft.nl/search/geo,osm,wikipedia/_search
```

### Search for anything within a geographic bounding box

```
curl -H "Content-Type: application/json" -X POST -d '{
  "from": 0,
  "size": "10",
  "query": {
    "filtered": {
      "query": {
        "match_all": {
          
        }
      }
    }
  },
  "filter": {
    "geo_bounding_box": {
      "location": {
        "top_left": "51.9746049736781,3.9879854492187405",
        "bottom_right": "51.932286908856256,4.1253145507812405"
      }
    }
  }
}' http://enipedia.tudelft.nl/search/geo,osm,wikipedia/_search
```


### Search for "Maasvlakte" within a geographic bounding box

```
curl -H "Content-Type: application/json" -X POST -d '{
  "from": 0,
  "size": "10",
  "query": {
    "common": {
      "_all": {
        "query": "Maasvlakte",
        "cutoff_frequency": 0.001
      }
    }
  },
  "filter": {
    "geo_bounding_box": {
      "location": {
        "top_left": "51.9746049736781,3.9879854492187405",
        "bottom_right": "51.932286908856256,4.1253145507812405"
      }
    }
  }
}' http://enipedia.tudelft.nl/search/geo,osm,wikipedia/_search
```



