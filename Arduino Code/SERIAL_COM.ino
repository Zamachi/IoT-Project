#define LED_RED  8
#define LED_BLUE 9
#define BTN      2
#define POT      A0

#define ARDUINO_ID 0

void btnISR() {
  sendData(BTN, 1);
}

void setup() {
  
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  
  pinMode(BTN, INPUT);

  attachInterrupt(digitalPinToInterrupt(BTN), btnISR, FALLING);
  
  Serial.begin(9600);

}

void loop() {
  
  
  while(Serial.available() > 0) {

      // PORUKA : "ARDUINO_ID:W/R[:PIN:VREDNOST];"
      String inMessage = Serial.readStringUntil(';');
      int i = inMessage.indexOf(':');
      
      
      if(i > 0) {
        String arduinoId = inMessage.substring(0, i);
        int id = arduinoId.toInt();
        
        char w_r = inMessage.charAt(i+1);
        
        if(w_r == 'W') {
          // WRITE REQUEST
          
          int s = i + 3;
          i = inMessage.indexOf(':', s);
          String pin = inMessage.substring(s, i);
          String vrednost = inMessage.substring(i+1);
          int p = pin.toInt();
          int v = vrednost.toInt();
          
          if(id != ARDUINO_ID) {
            // posalji dalje
          } else {
            if(p == 8)
              digitalWrite(p, v);
            else if(p == 9)
              analogWrite(p, v);
          }

            
        } else {

          int analogIn = analogRead(POT);
          // ODGOVOR : "ARDUINO_ID:PIN|VREDNOST;"
          sendData(POT, analogIn);

          
          
        }
    } 
  }
}

void sendData(int pin, int value) {
  String s = String(ARDUINO_ID) + ":" + String(pin) + "|" + String(value) + ";";
  Serial.print(s);
}
