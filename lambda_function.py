import os
import requests

def lambda_handler(event, context):
  #main call in order formatted for ans
  media = call_anilist_api()
  check_upcoming_episodes(media)
  
  
def call_anilist_api():
  userId = os.environ.get("USER_ID")
  #environment variable for changing which userId is pulled
  
  has_next_line = True
  page = 0
  #variable for potential loops
  
  media = []
  #output of the function
  
  while has_next_line:
    page+=1
    query = '''
    query Query($userId: Int, $status: MediaListStatus, $type: MediaType, $sort: [MediaListSort], $perPage: Int, $page: Int) {
      Page(perPage: $perPage, page: $page) {
        pageInfo {
          hasNextPage
        }
        mediaList(userId: $userId, status: $status, type: $type, sort: $sort) {
          media {
          coverImage {
            extraLarge
          }
            title {
              romaji
            }
            nextAiringEpisode {
              timeUntilAiring
            }
          }
        }
      }
    }
    ''' 
    #Graphql schema call for anilist api
    
    variables = {
      "userId": userId,
      "page": page,
      "perPage": 50,
      "status": "CURRENT",
      "sort": "MEDIA_TITLE_ROMAJI",
      "type": "ANIME"
    }
    #Varibles inputed into the request page and userId being variables
    
    url = 'https://graphql.anilist.co'

    try:
      response = requests.post(url, json={'query': query, 'variables': variables})
      response.raise_for_status()
      data = response.json()
      #api call
    except requests.RequestException as e:
      print(f"Request failed: {e}")
      return []
    #error handling
    media.extend(data["data"]["Page"]["mediaList"])
    #saving series output
    
    has_next_line = data["data"]["Page"]["pageInfo"]["hasNextPage"] 
    #check if more data to check on more pages
  return media

def check_upcoming_episodes(media):
  for series in media:
    if series["media"]["nextAiringEpisode"] != None and series["media"]["nextAiringEpisode"]["timeUntilAiring"] < 300:
      send_webhook(series["media"])
      #check all curently watching series to check if it is ongoing and if it is going to release within 5 minutes, then calls for a webhook 
    
def send_webhook(series):
  discord_webhook = os.environ.get("WEBHOOK")
  #enviromental variable for changing the webhook used
  
  time_until_airing = series["nextAiringEpisode"]["timeUntilAiring"]
  #varible used next line to shorten, pull the next episode coming out and check when it is excepted to release
  
  body = series["title"]["romaji"] + " will be releasing in " + str(int(time_until_airing/60)) + " mintues and " + str(time_until_airing%60) + " seconds approximately." 
  requests.post(discord_webhook, json={"content": body})
  requests.post(discord_webhook, json={"content": series["coverImage"]["extraLarge"]})
  #call to webhook to send out series going to release soon