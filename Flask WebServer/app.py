from flask import Flask, render_template
import serial
from threading import Thread
import time
from mailService import sendEmail

PORT = "COM1"
BAUD_RATE = 9600


objectDic = {}

objectDic[14] = {"sensor" : "potenciometar", "value": 0, "lastUpdate": "00:00:00"}
objectDic[2] = {"sensor" : "taster", "value": 0, "lastUpdate": "00:00:00"}


running = True
serialConnection = serial.Serial(PORT, BAUD_RATE)

def receive(serialConnection):
    global running
    
    while running:
        
        if serialConnection.in_waiting > 0:
            receivedMessage = serialConnection.read_until(b';').decode('ascii')
            processMessage(receivedMessage)
        time.sleep(0.1)

def processMessage(message):
    # FIXME format poruke je kakav?? 
    l = message[:-1].split(":")
    arudinoId = int(l[0])
    pin = int(l[1].split("|")[0])
    val = int(l[1].split("|")[1])

    objectDic[pin]['value'] = val;
    objectDic[pin]['lastUpdate'] = time.strftime();

threadReceiver = Thread(target=receive, args=(serialConnection,))
threadReceiver.start()

threadEmail = Thread(target=sendEmail)
threadEmail.start()

app = Flask(__name__)

@app.route('/')
def dashboard():
    global objectDic
    return render_template("dashboard.html", data=objectDic)
    # return jsonify(isError=False, message="Success", statusCode=200, data=pin_id)

@app.route('/light', methods=['GET'])
def light():
    #serialConnection.write("LED;".encode('ascii'))
    return "Proslo"
    # return render_template("dashboard.html")

@app.route('/door/<status>', methods=["GET"])
def door(status):
    print(status)
    # serialConnection.write("11:"+status.upper()+";".encode("ascii"))
    return render_template("dashboard.html")

@app.route('/ventilation/<value>', methods=['GET'])
def venetilation(value):
    print(value)
    # serialConnection.write("5:"+value+";".encode('ascii'))
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(port=5000, debug=True)