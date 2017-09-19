"use strict";

var googleTrends = require('path_to_google_trends_api');
var util = require('util')
var result = [];

//google-trends api returns nested dictionaries with number as a key until you hit the level with actual data.
//this function finds only the data part and return, for ease of transformation into data format that chart.js uses.
function recursive_key_search(obj)
{
  var key = "";
  for (key in obj)
  {
    if(!isNaN(Number(key)))
    {
      return obj;
    }
    break;
  }
  return recursive_key_search(obj[key]);
};

//returns a string that resembles "DATAsplitHereForListDATA".
//splitHereForList is added for server application to use as token when spliting the string.
function related_queries(search_word, start_date, end_date, country)
{
  start_date = new Date(start_date);
  end_date = new Date(end_date);
  googleTrends.relatedQueries({keyword: search_word, startTime: start_date,
                                endTime: end_date, geo: country}, function(err, results){
                                  if(err) console.log("error!", err);
                                  else {
                                    //find data part of the response.
                                    var queries = recursive_key_search(JSON.parse(results));
                                    //output
                                    console.log(JSON.stringify(queries[0]["rankedKeyword"]));
                                    //token for server application to use when spliting.
                                    console.log("splitHereForList");
                                    //output
                                    console.log(JSON.stringify(queries[1]["rankedKeyword"]));
                                  }
                                })
}

related_queries(process.argv[2], process.argv[3], process.argv[4], 'KR');
