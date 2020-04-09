import requests

url = "https://coolguruji-youtube-to-mp3-download-v1.p.rapidapi.com/"

querystring = {"id":"IDj_SBw3C_E"}

headers = {
    'x-rapidapi-host': "coolguruji-youtube-to-mp3-download-v1.p.rapidapi.com",
    'x-rapidapi-key': "SIGN-UP-FOR-KEY"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)