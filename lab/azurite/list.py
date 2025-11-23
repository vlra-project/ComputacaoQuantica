import requests

url = "https://cloud.tenable.com/scans"

headers = {
      "accept": "application/jason",
      "content-type": "application/json",
      "X-ApiKeys": accessKey=a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9; secretKey=c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213"
}

response = requests.get(url, headers=headers)

print(response.text)
