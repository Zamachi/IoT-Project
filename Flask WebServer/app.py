from flask import Flask, render_template, jsonify
import serial
from threading import Thread
import time
from mailService import sendEmail
from thnigspeak import sendData
from random import randint
from datetime import datetime

PORT = "COM4"
BAUD_RATE = 9600

IS_LED_ON = False
IS_DOOR_OPEN = False
PWM_STATE = 0


objectDic = {
    "LIGHT":{
        "lastUpdate": "00:00:00",
        "value":0,
        "unit":"Lux"
    },
    "TEMP":{
        "lastUpdate": "00:00:00",
        "value":0,
        "unit": "°C"
    },
    "RELAY":{
        "lastUpdate": "00:00:00",
        "value":0,
        "unit": ""
    },
    "DOOR":{
        "lastUpdate": "00:00:00",
        "value":0,
        "unit": ""
    }
}

running = True
serialConnection = serial.Serial(PORT, BAUD_RATE)

def receive(serialConnection):
    global running
    
    while running:
        
        if serialConnection.in_waiting > 0:
            receivedMessage = serialConnection.read_until(b';').decode('ascii')
            processMessage(receivedMessage)
            serialConnection.reset_input_buffer()
        time.sleep(0.1)

def processMessage(message):
    # NOTE format poruke: "$TEMP:value$LIGHT:value$RELAY:value$DOOR:value;"
    # print(message)
    # print(message[0])
    if(message[0] == "$"):
        # print("Poruka je pristigla "+ str(datetime.now()) +message[1:])
        ocitavanja = message[1:].split("$")
        for senzor in ocitavanja:
            key_value = senzor.split(":")
            objectDic[key_value[0]]['value'] = key_value[1]
            objectDic[key_value[0]]['lastUpdate'] = str(datetime.now())

        sendData(
            temp=objectDic["TEMP"]["value"], 
            osvetljenje=objectDic["LIGHT"]["value"], 
            relej=objectDic["RELAY"]["value"], 
            vrata=objectDic["DOOR"]['value']
        )

threadReceiver = Thread(target=receive, args=(serialConnection,))
threadReceiver.start()

threadEmail = Thread(target=sendEmail)
threadEmail.start()

# NOTE ovde simuliramo slanje na ThingSpeak(bez potrebe za Arduino serijskom com...)
# threadSend = Thread(target=sendData, args=(randint(-55, 151), randint(0, 10000), randint(1,10), randint(1,10)))
# threadSend.start()

app = Flask(__name__)

@app.route('/')
def dashboard():
    global objectDic
    return render_template("dashboard.html", data=objectDic)

@app.route('/light', methods=['GET'])
def light():
    global IS_LED_ON
    # print(IS_LED_ON)
    IS_LED_ON = not IS_LED_ON
    serialConnection.write("4:;".encode('ascii'))
    return jsonify(isError=False, message="Success", statusCode=200, data=IS_LED_ON)

@app.route('/door/<status>', methods=["GET"])
def door(status):
    global IS_DOOR_OPEN
    #print(status[0])
    IS_DOOR_OPEN = not IS_DOOR_OPEN
    serialConnection.write(("11:"+status.upper()[0]+";").encode("ascii"))
    return jsonify(isError=False, message="Success", statusCode=200, data=IS_DOOR_OPEN)

#NOTE ova funkcija treba samo da vrati jsonify, ne treba nam randomizacija podataka
@app.route('/updateVals', methods=['GET'])
def updateVals():
    global objectDic

    # objectDic["TEMP"]["value"] = randint(-55, 150)
    # objectDic["TEMP"]["lastUpdate"] = str(datetime.now())

    # objectDic["LIGHT"]["value"] = randint(0, 10000)
    # objectDic["LIGHT"]["lastUpdate"] = str(datetime.now())
    return jsonify(isError=False, message="Success", statusCode=200, data=objectDic)

@app.route('/ventilation/<value>', methods=['GET'])
def ventilation(value):
    global PWM_STATE
    PWM_STATE = int( (int(value) / 100) * 255)
    # print(PWM_STATE)
    if(PWM_STATE > 255):
        PWM_STATE = 255
    elif(PWM_STATE < 0 ):
        PWM_STATE = 0
    serialConnection.write(("5:"+str(PWM_STATE)+";").encode('ascii'))
    return jsonify(isError=False, message="Success", statusCode=200, data=PWM_STATE)

if __name__ == "__main__":
    app.run(port=5000, debug=True)