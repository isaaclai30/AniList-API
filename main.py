import requests

def lambda_handler():
  #main call in order formatted for ans
  media = call_anilist_api()
  check_upcoming_episodes(media)
  
  
def call_anilist_api():
  userId = 7322485
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
          currentPage
          hasNextPage
          perPage
        }
        mediaList(userId: $userId, status: $status, type: $type, sort: $sort) {
          media {
          coverImage {
            large
          }
            title {
              romaji
            }
            status
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

    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()
    media.extend(data["data"]["Page"]["mediaList"])
    #api call and saving series output
    
    has_next_line = data["data"]["Page"]["pageInfo"]["hasNextPage"] 
    #check if more data to check on more pages
  return media

def check_upcoming_episodes(media):
  for series in media:
    if series["media"]["nextAiringEpisode"] != None and series["media"]["nextAiringEpisode"]["timeUntilAiring"] < 3000000:
      send_webhook(series["media"])
      #check all curently watching series to check if it is ongoing and if it is going to release within 5 minutes, then calls for a webhook 
    
def send_webhook(series):
  discord_webhook = "https://discord.com/api/webhooks/1371573170825593037/ZQXyMtptqMCmNzjwev4_uZ40nolBE8-6sRTiNAZ1-NBVOB5OTc2W4c9-SRcNpmBYsEnQ"
  #enviromental variable for changing the webhook used
  
  time_until_airing = series["nextAiringEpisode"]["timeUntilAiring"]
  #varible used next line to shorten, pull the next episode coming out and check when it is excepted to release
  
  body = series["title"]["romaji"] + " will be releasing in " + str(time_until_airing/60) + " mintues and " + str(time_until_airing%60) + " seconds approximately." 
  requests.post(discord_webhook, json={"content": body, "image": series["coverImage"]["large"]})
  #call to webhook to send out series going to release soon
  
  

lambda_handler()