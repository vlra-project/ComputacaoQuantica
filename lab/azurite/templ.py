#import requests

#url = "https://cloud.tenable.com/scans"

#headers = {
#      "accept": "application/jason",
#      "content-type": "application/json",
#      "X-ApiKeys": accessKey=af833672f4b0a05e9186f7117190312c810814637ad2edea6aaf3cf010992495"
#}

#response = requests.get(url, headers=headers)

#print(response.text)

#temp_list = tio.policies.templates()
#print temp_list

#ACCESS_KEY = '62d53691e867ce414af878198c00769e804b8915841fee1171edc95145ba7ee2'
#SECRET_KEY = '257b13f8ff931af64f5cfc2f34662665c014ba44ac5ceefb9817dd34284d0b05'


import requests

headers = {
    'X-ApiKeys': 'accessKey=62d53691e867ce414af878198c00769e804b8915841fee1171edc95145ba7ee2; secretKey=257b13f8ff931af64f5cfc2f34662665c014ba44ac5ceefb9817dd34284d0b05',
    'Content-Type': 'application/json'
}

response = requests.get('https://cloud.tenable.com/editor/scans', headers=headers)

if response.status_code == 200:
    templates = response.json()['templates']
    for template in templates:
        print(f"Nome: {template['name']}, UUID: {template['uuid']}")
else:
    print("Erro ao obter templates:", response.status_code, response.text)


