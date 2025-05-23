# Anilist API

### GraphQL API
Anilist uses the graphQL structure for its api. This structure was fair easy to using lead to only a little bit of time spent on determining the structure of the request push to them. The only issues being the separation of pagination into put into a separate type encompassing any other type that could have been a list. 

The query was for a page for the medialist from a specified user with their UserID. This UserID was found quickly by sending a seperate query to Anilist for the UserID using the Username as a filter. The medialist would be filtered by currently consumed media and if that media was an anime. The query would request a cover image url, title, and the time of the next airing episode.

The only remaining part of the request was to check if their were more pages in medialist and if so, to query the that page, repeating until complete.

### Logic
The logic to check episode coming out soon was simple, check all the media for if they have an upcoming episode and if so check if they are coming out in the next five minutes or not. If the media met the requirements a webhook would be sent out.

### Webhook
In order for a discord webhook to be sent out a url would have to be create. By looking into the  setting of a discord channel and going into Integration > Webhooks, one can quickly be create and url be generated. With this webhook, requests are send out to this webhook with the series image, title, and time until upcoming episode we be sent in a json.

### Lambda Function
To setup this script to run on a regular interval, a lambda function was set up.  The lambda function required a few edits to the script, the script was encapsulated into a function call, lambda_handler with the parameter of event and context, and the main.py was renamed into lambda_function.py. The environment variable were place into the lambda, defining variable that are specific to the people running it, the webhook and the userID. Lambda does not include the request library, which is used for the api and webhook so that package was sent using github actions discussed later, other method will be just later as well. All that remain was to set up the script to run at a regular interval automatically, which required a event bridge used a cron rule that defined when to run.

### Github Actions
This last portion was not a requirement in order to run this script, but allow the syncing of GitHub repository updates to the lambda. OIDC was used here to link the repository and the GitHub together specifically.
After that the requirement.txt is pulled to grab the only requirement, requests, and it and the lambda_function.py is zipped and sent to the lambda defined in the OIDC
### Lambda Role Assignment
In order to link the GitHub and Lambda directly, a Identity provider and an audience of AWS is set setup to. Then a role is create for GitHub to access as a web Identity. The trust policy is then edited to connect the repository with AWS with the repository as the sub and AWS as the aud.
