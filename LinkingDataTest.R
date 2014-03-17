#never ever convert strings to factors
options(stringsAsFactors = FALSE)

# TODO 
# Also do blocking per country, etc.
# Should investigate work at https://github.com/YannBrrd/elasticsearch-entity-resolution

library(rjson)
library(RCurl)
library(httr)
library(sqldf)
library(plyr) # rbind.fill

convertResultsToDataFrame <- function(results){
  df = data.frame()
  
  if (!is.null(results$hits$hits)){
    for (element in results$hits$hits){
      df = rbind.fill(df, as.data.frame(element))
    }    
  } else { # probably a single result
    df = as.data.frame(t(unlist(results["_source"])))
    colnames(df) = gsub("^_source\\.", "", colnames(df))
  }
  colnames(df) = gsub("^a\\.", "", colnames(df))
  colnames(df) = gsub("^X_", "", colnames(df))
  return(df)  
}

commonTermsQuery <- function(queryString, indexName){
  query = paste('{"query":{"common": {"_all": {"query":"', queryString, '" ,"cutoff_frequency":0.001}}}}', sep="")
  results = runQuery(query, indexName)
  return(results)
}

fuzzyLikeThisQuery <- function(queryString, indexName){
  query = paste('{query : {fuzzy_like_this: {like_text: "', queryString, '"}}}', sep="")
  results = runQuery(query, indexName)
  return(results)
}

# process the json query request
runQuery <- function(queryRequest, indexName){
  url= paste('http://enipedia.tudelft.nl/search/',indexName,'/_search?pretty=true', sep="")
  results = POST(url = url, 
                 config = c(add_headers(Connection = "keep-alive", Expect=''), 
                            accept_json()), 
                 body = queryRequest)
  results = rawToChar(results$content)
  #print(results)
  results = fromJSON(results)
  results = convertResultsToDataFrame(results)
}

totalNumberOfHits <- function(indexName){
  url= paste('http://enipedia.tudelft.nl/search/",indexName,"/_search?pretty=true', sep="")
  queryRequest = '{"from":10000, "size":1, "query": {"filtered" : {"query" : {"match_all" : {}}}}}}'
  results = POST(url = url, 
                 config = c(add_headers(Connection = "keep-alive", Expect=''), 
                            accept_json()), 
                 body = queryRequest)
  
  results = rawToChar(results$content)
  #print(results)
  results = fromJSON(results)
  return(results$hits$total)  
}

getSearchStringForEntryNumber <- function(entryNum, indexName, type){
  url = paste("http://enipedia.tudelft.nl/search/",indexName,"/",type,"/", entryNum, sep="")
  results = GET(url, 
                config = c(add_headers(Connection = "keep-alive", Expect=''), 
                           accept_json()))
  
  results = rawToChar(results$content)
  #print(results)
  results = fromJSON(results)
  results = convertResultsToDataFrame(results) 
  results = paste(results, collapse = " ")
  queryString = gsub(" +", " ", results)
  queryString = gsub('"', '', queryString)
  return(queryString)
}

# This gets all the indices (i.e. data sets)
getAllIndices <- function(){
  results = GET("http://enipedia.tudelft.nl/search/_aliases?pretty=1  ")
  return(names(fromJSON(rawToChar(results$content))))
}

getAllIndicesAndTypes <- function(){
  # There's also info in here about all the different fields and the data types specifed for them
  # This can be useful for figuring which things are geographic coordinates, etc.
  
  url = "http://enipedia.tudelft.nl/search/_mapping"
  results = GET(url = url, 
                 config = c(add_headers(Connection = "keep-alive", Expect=''), 
                            accept_json()))
  data = fromJSON(rawToChar(results$content))
  
  indicesAndTypes = data.frame()
  
  indices = names(data)
  for (index in indices){
    types = names(data[[index]])
    indicesAndTypes = rbind(indicesAndTypes, cbind(index, types))
  }
  return(indicesAndTypes)
}

getAllEntriesInIndex <- function(indexName){
  resultSize = 100
  
  queryRequest = '{"query" : {"match_all" : {}}}'
  url = paste("http://enipedia.tudelft.nl/search/", 
              indexName, 
              "/_search?search_type=scan&scroll=10m&size=", 
              resultSize, 
              "&pretty=true", # make it pretty even though no one's looking
              sep="")
  results = POST(url = url, 
                 config = c(add_headers(Connection = "keep-alive", Expect=''), 
                            accept_json()))
  results = rawToChar(results$content)
  data = fromJSON(results)
  
  totalHits = data$hits$total
  
  scrollID = as.character(data["_scroll_id"]) # basically unlist this, just make it a character

  allData = data.frame()
  count = 0
  keepScanning = TRUE
  while(keepScanning){
    print(count)
    scrollID = as.character(data["_scroll_id"])
    
    url = paste("http://enipedia.tudelft.nl/search", 
                "/_search/scroll?scroll=10m",
                "&scroll_id=", scrollID, 
                sep="")
    results = POST(url = url, 
                   config = c(add_headers(Connection = "keep-alive", Expect=''), 
                              accept_json()))
    
    results = rawToChar(results$content)
    data = fromJSON(results)
    
    if (length(data$hits$hits) > 0){
      
      df = convertResultsToDataFrame(data)
      allData = rbind.fill(allData, df)
      
      count = count + resultSize
    } else {
      keepScanning = FALSE
    }
  }
  return(allData)
}

# try to get all the data
eprtrData = getAllEntriesInIndex("eprtr")
euetsData = getAllEntriesInIndex("euets")
carmav3Data = getAllEntriesInIndex("carmav3")

## TODO possible to run multiple queries at once?
# try to match the euets to the eprtr
#matchingResults = data.frame()
for (i in c(1:nrow(euetsData))){
  print(i)
  queryString = paste(euetsData[i,which(!is.na(euetsData[i,]))], collapse=" ")
  queryString = gsub('"', '', queryString)
  fuzzy_df = fuzzyLikeThisQuery(queryString, "eprtr")
  common_terms_df = commonTermsQuery(queryString, "eprtr")
  df = rbind.fill(fuzzy_df, common_terms_df)
  df = sqldf("select * from df order by score DESC")
  # get rid of duplicated entries
  df = df[!duplicated(df$id),]
  df$euetsID = euetsData$id[i]
  matchingResults = rbind.fill(matchingResults, df)
}

topResults = sqldf("select euetsID, max(score) as maxScore from matchingResults group by euetsID")

# this is pretty good - most max scores are above one, almost half are above two
plot(sort(topResults$maxScore))

# now need some interactive tool that allows us to verify the best links - prioritize highest links

# geonames to deal with location info?