from tempfile import tempdir
import urllib.request

READ_KEY = ""
WRITE_KEY = "5MAB2VHW58FD71WV"


def sendData():
    temp = 25
    osvetljenje = 10
    vrata = 2
    relej = 0

    urllib.request.urlopen('https://api.thingspeak.com/update?api_key={}&field1={}&field2={}&field3={}&field4={}'.format(WRITE_KEY, temp, osvetljenje, vrata, relej))
    print("Poslato na thing speak")

sendData()
# import requests
# CHANNEL_ID = 0
# READ_KEY = ""

# res = requests.get("https://api.thingspeak.com/channels/{}/feeds.json?api_key={}".format(CHANNEL_ID, READ_KEY))

# res = requests.get(" https://api.thingspeak.com/channels/{}/fields/{}.json?api_key={}".format(CHANNEL_ID, 2,READ_KEY))

# data = res.json()



# print(data['feeds'])
