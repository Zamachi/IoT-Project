import urllib.request
import requests

READ_KEY = "IDK2WDSQQWZ07AG0"
WRITE_KEY = "5MAB2VHW58FD71WV"
CHANNEL_ID = 1727211

def sendData(temp, osvetljenje, vrata, relej):
    urllib.request.urlopen('https://api.thingspeak.com/update?api_key={}&field1={}&field2={}&field3={}&field4={}'.format(WRITE_KEY, temp, osvetljenje, vrata, relej))
    print("Poslato na thing speak")

def receiveData():
    res = requests.get("https://api.thingspeak.com/channels/{}/feeds.json?api_key={}".format(CHANNEL_ID, READ_KEY))
    # res = requests.get(" https://api.thingspeak.com/channels/{}/fields/{}.json?api_key={}".format(CHANNEL_ID, 2,READ_KEY))
    data = res.json()
    print(data['feeds'])
