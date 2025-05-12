import requests

def lambda_handler():
  media = call_anilist_api()
  check_upcoming_episodes(media)
  
  
def call_anilist_api():
  has_next_line = True
  page = 0
  media = []
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
    variables = {
      "userId": 7322485,
      "page": page,
      "perPage": 50,
      "status": "CURRENT",
      "sort": "MEDIA_TITLE_ROMAJI",
      "type": "ANIME"
    }
    url = 'https://graphql.anilist.co'

    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()
    media.extend(data["data"]["Page"]["mediaList"])
    
    has_next_line = data["data"]["Page"]["pageInfo"]["hasNextPage"]
  return media    

def check_upcoming_episodes(media):
  for series in media:
    if series["media"]["nextAiringEpisode"] != None and series["media"]["nextAiringEpisode"]["timeUntilAiring"] < 300:
      send_webhook(series[media])
    
def send_webhook(series):
  discord_webhook = "https://discord.com/api/webhooks/1371573170825593037/ZQXyMtptqMCmNzjwev4_uZ40nolBE8-6sRTiNAZ1-NBVOB5OTc2W4c9-SRcNpmBYsEnQ"
  time_until_airing = series["nextAiringEposide"]["timeUntilAiring"]
  body = series["title"]["romaji"] + " will be releasing in " + str(time_until_airing/60) + " mintues and " + str(time_until_airing%60) + " seconds approximately." 
  requests.post(discord_webhook, json={"content": body})
  requests.post(discord_webhook, json={"content": series["coverImage"]["large"]})
  
  

lambda_handler()
requests.post("https://discord.com/api/webhooks/1371573170825593037/ZQXyMtptqMCmNzjwev4_uZ40nolBE8-6sRTiNAZ1-NBVOB5OTc2W4c9-SRcNpmBYsEnQ", json={"content": "text"})