#include <Arduino.h>
#include <Servo.h>
#include <TimerOne.h>

#define RELAY_CONTROL 4
#define MOTOR_CONTROL 5
#define WIPER_READOUT A5
#define ULTRASONIC_TRIG 13
#define ULTRASONIC_ECHO 12
#define SERVO_CONTROL 11
#define TEMPERATURE A4
#define VOLTAGE_SPLIT A3

int RELAY_STATE;
int vrednost_potenciometra = 0;
int stara_vrednost_potenciometra = 0;
int otpornost_otpornika = 1000; // otpornost otpornika(razdelnik napona) u omima

unsigned long TIMER_DURATION = 2000; // nakon koliko vremena se okida vrem. prekid(us)
unsigned long counter = 0;           // counter za tajmer
typedef enum
{
  Transmission,
  Receive,
  Action,
  Wait
} SerialState;          // Stanje naseg serijsokg I/O
unsigned long duration; // vreme trajanja povratka
float distance;         // udaljenost objekta i senzora
int ukupan_broj_promena_stanja_releja = 0;
int ukupan_broj_otvaranja_vrata = 0;
bool is_door_open = false;

Servo servoControl; // potreban nam je Servo objekat iz biblioteke za rad

void Timer1Interrupt()
{
  counter++;

  // NOTE Uzima se najveca moguca udaljenost koju senzor moze da izmeri
  // NOTE zatim se na osnovu toga izracuna vreme potrebno da signal udari u objekat
  // NOTE Ako je max. udaljenost 3m(kao kod naseg uredjaja), a brzina zvuka u vazduhu 343 m/s
  // NOTE Onda je t= S/V = 3/343 ~ 0.008746 s = 8746 us...
  // NOTE Znaci treba 8746 mikrosekundi da drzimo signal na HIGH, a nakon toga da ga ugasimo
  // NOTE i da na prijemnoj strani izvrsimo citanje HIGH signala, tj. koliko on traje
  // NOTE Buduci da smo stavili da se tajmer okida na 2000 mikrosekundi, da bismo dosli do
  // NOTE priblizne vrednosti od 8000 mikrosekundi vremenski prekid treba da se okine 4 puta
  // NOTE jer 4*2000=8000 mikrosekundi, nakon toga treba da setujemo signal na LOW.

  switch (SerialState)
  {
  case Transmission:
    digitalWrite(ULTRASONIC_TRIG, HIGH);
    if (counter % 4 == 0)
      SerialState = Receive;
    break;
  case Receive:
    digitalWrite(ULTRASONIC_TRIG, LOW);
    duration = pulseIn(ULTRASONIC_ECHO, HIGH); // citamo vreme koje je bilo potrebno signalu da se vrati u prijemnik(milisekundama)
    distance = duration * 0.0343 * 0.5;
    SerialState = Wait;
    break;
  case Action: // WARNING ovo potencijalno treba premestiti u loop!
    if (distance < 5 && !is_door_open)
    {
      servoControl.write(90);
      is_door_open = !is_door_open;
      ukupan_broj_otvaranja_vrata++;
    }
    else if (is_door_open)
    {
      is_door_open = !is_door_open;
      servoControl.write(0);
    }
    break;
  case Wait:
    if (counter % 500 == 0)
      SerialState = Transmission;
    break;
  }

  // Arduino treba svakog minuta da salje izvestaj Web serveru(Flask)
  // NOTE 60 s / 0.002 = 30000 otkucaja
  if (counter % 30000 == 0)
  {
    // FIXME ovde vrsimo slanje serijsko slanje...
    Serial.println(
        "TEMP:" + String(getTemperatureFromSensor()) +
        ";LIGHT:" + String(getLightInLux()) +
        ";RELAY:" + String(ukupan_broj_promena_stanja_releja) +
        ";DOOR:" + String(ukupan_broj_otvaranja_vrata) + ";");

    ukupan_broj_promena_stanja_releja = 0;
    ukupan_broj_otvaranja_vrata = 0;
    counter = 0;
  }
}

void setup()
{
  pinMode(RELAY_CONTROL, OUTPUT);   // kontrolise kotvu na releju
  pinMode(ULTRASONIC_TRIG, OUTPUT); // koristimo da posaljemo signal na predajniku ultrason.senz.
  pinMode(MOTOR_CONTROL, OUTPUT);   // Kontrolise DC elektromotor(PWM)
  pinMode(ULTRASONIC_ECHO, INPUT);  // vrsimo ocitavanja sa prijemnika na ultrason.senz.
  pinMode(TEMPERATURE, INPUT);      // ocitavanja sa analognog ulaza(napon) za temperatuu
  pinMode(VOLTAGE_SPLIT, INPUT);    // razdelnik napona(analogni senzor)

  RELAY_STATE = LOW; // relej inicijalno LOW

  servoControl.attach(SERVO_CONTROL); // Na digitalnom portu 11 se vrsi kontrola servo motora

  SerialState = Transmission; // inicijalizujemo stanje

  Timer1.initialize(TIMER_DURATION);       // inicijalizujemo tajmer sa odedjenim trajanjem
  Timer1.attachInterrupt(Timer1Interrupt); // koja funkcija se izvrsi kada dodje do vrem. prek.

  Serial.begin(9600);
}

int getTemperatureFromSensor()
{
  // NOTE ovo je formula za TMP36!
  return (5 * analogRead(TEMPERATURE) / 1023.0f) * 100 - 50;

  // NOTE Formula za LM35:
  //       T = 500 * D/1023 (○C),  gde je D - ocitavanje sa analognog ulaza ( ?)
}

int getLightInLux()
{ // NOTE: proveriti formulu!
  float vrednost_napona = analogRead(VOLTAGE_SPLIT) * 5 * 9.7751710e-4;
  float otpornost_fotootpornika = otpornost_otpornika * (5 - vrednost_napona) / vrednost_napona;

  return (int)(12518931 * pow(otpornost_fotootpornika, -1.405));
}

void loop()
{
  //NOTE Format poruke koji prihvatamo PIN[:VREDNOST];
  if (Serial.available() > 0)
  {
    String poruka = Serial.readStringUntil(';');
    int index = poruka.indexOf(':');

    if (index == -1) //NOTE RELEJ MENJAMO TAKO STO SA FRONTA POSALJEMO ZAHTEV FORMATA "PIN;"(bez vrednosti)
    {
      RELAY_STATE = !RELAY_STATE;
      digitalWrite(RELAY_CONTROL, RELAY_STATE);
      ukupan_broj_promena_stanja_releja++;
      Serial.println(RELAY_STATE);//FIXME ovo treba da vrati stanje releja da se prikaze na frontu
    }
    else
    {
      int pin = poruka.substring(0, index).toInt();

      switch (pin)
      {
      case 5:
      {
        // NOTE ovde vrsimo kontrolu motora(poruka stize sa Fronta)
        analogWrite(MOTOR_CONTROL, poruka.substring(index + 1, poruka.indexOf(':', index + 1)).toInt());
        break;
      }
      case 11:
        // NOTE Poruka tipa 11:O ili C;
        char open_close = poruka[2];
        if (open_close == 'O' && !is_door_open)
        {
          servoControl.write(90);
          ukupan_broj_otvaranja_vrata++;
          is_door_open = !is_door_open;
        }
        else if (is_door_open)
        {
          servoControl.write(0);
          is_door_open = !is_door_open;
        }
        Serial.println(is_door_open);//FIXME povratna informacija

        break;
      default:
        Serial.println("Dati uredjaj nije pronadjen");
        break;
      }
    }
  }
  else
  {
    // NOTE Ukoliko nema poruke, onda se samo ocitava vrednost sa potenciometra da bi se promenio PWM DC motora
    vrednost_potenciometra = analogRead(WIPER_READOUT);
    if (vrednost_potenciometra != stara_vrednost_potenciometra)
    {
      stara_vrednost_potenciometra = vrednost_potenciometra;
      analogWrite(MOTOR_CONTROL, map(vrednost_potenciometra, 0, 1023, 0, 255));
    }
  }
}