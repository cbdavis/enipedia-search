enipedia-search
===============
This is the web page code that is used for http://enipedia.tudelft.nl/Elasticsearch.html

This isn't just for the humans, and you can send API requests as well to http://enipedia.tudelft.nl/search.  

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



