enipedia-search
===============

## What?
This is the web page code that is used for http://enipedia.tudelft.nl/Elasticsearch.html.  The main motivation is that data for global power plants is not published using a standardized format.  Data that is relevant for a single plant may be distributed across multiple databases which do not (re)use standard identifiers.  The interface below has been created to help deal with this situation by allowing one to easily search across multiple databases that may contain relevant data.  

<a href="http://enipedia.tudelft.nl/Elasticsearch.html"><img src=EnipediaSearch.png></a>

This isn't just for the humans, and you can send API requests as well to http://enipedia.tudelft.nl/search.  
Behind the scenes, [Elasticsearch](https://www.elastic.co) is used, and you can use their [documentation](https://www.elastic.co/guide/index.html) to help create your own queries.

There are a few interesting types of queries for which examples are included further below in the documentation:
* **Common Terms Query** - This reduces the importance of commonly occurring terms in suggesting matches.  This is also useful when searching across data in different languages, as it will automatically reduce the importance of terms like "power plant" and "kraftwerk" which may frequently appear in the data.
* **Fuzzy Like This** - This is useful if you're searching for the name of a power plant that may have different spellings due to translation or the conversion of [diacritical characters to ascii characters](https://docs.oracle.com/cd/E29584_01/webhelp/mdex_basicDev/src/rbdv_chars_mapping.html)
* **Geographic** - You can search for anything within a geographic bounding box or a distance from a point

## Available Databases
* `carmav2` - Version 2 of the dataset collected by http://carma.org
* `carmav3` - Version 3 of the dataset collected by http://carma.org
* `eprtr` - [European Pollutant Release and Transfer Register](http://prtr.ec.europa.eu/#/home)
* `euets` - European Union Emissions Trading System
* `osm` - OpenStreetMap - everything tagged as "[power=generator](http://wiki.openstreetmap.org/wiki/Tag:power%3Dgenerator)", updated daily
* `wikipedia` - Wikipedia articles about power plants, updated daily via https://github.com/cbdavis/wikipedia-power-plants
* `geo` - [Global Energy Observatory](globalenergyobservatory.org) via scraper at https://morph.io/coroa/global_energy_observatory_power_plants
* `lcpd` - [Large Combustion Plant Directive](https://en.wikipedia.org/wiki/Large_Combustion_Plant_Directive) - data is old but contains information on heat input, energy per fuel type, etc.

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

### Search for anything within 10 km of a specific geographic point
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
        "geo_distance": {
          "distance": "10km", 
          "location": { 
            "lat":  52,
            "lon": 4
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

### Search over both country and name
Search for the Fierza plant within Albania.  Use boost to make sure we prioritize matching Albania.  Numerous results will be returned for Albania and it's important to look at the score as it should highlight the one correct match above the others.
```
curl -XPOST 'http://enipedia.tudelft.nl/search/geo/_search?pretty=true' -d '
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "Name": "Fierza"
          }
        }, 
        {
          "match": {
            "Country": {
              "query": "Albania",
              "boost": 2
            }
          }
        }
      ]
    }
  }
}'
```
