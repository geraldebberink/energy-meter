#include <Servo.h>

//Number of pulses, used to measure energy.
unsigned long nPulses = 0;  
int led = 13;


//Used to measure power.
unsigned long currentTime,previousTime = 0;
unsigned long oldPulses = 0;

//power and energy
double power;


String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
boolean firstRead = true;

void setup()
{
Serial.begin(9600);
inputString.reserve(100);
pinMode(led, OUTPUT);
// Make pin 3 an input with it's pull-up resistor activated.
pinMode(3, INPUT);
digitalWrite(3, HIGH);

// Wh interrupt attached to IRQ 1 = pin3
attachInterrupt(1, onPulse, FALLING);
}


void loop()
{
if (stringComplete) {
  //used to measure time between measurements
  //Serial.println(inputString);
  if (inputString.startsWith("set"))
  {
    nPulses = inputString.substring(4).toInt();
  } 
  else 
  {
    Serial.print(firstRead,DEC);
    Serial.print(" ");
    Serial.print(power,DEC);
    Serial.print(" ");
    Serial.println(nPulses,DEC);
  }
  firstRead = false;
  stringComplete = false;
  inputString="";
  Serial.flush();
  }

}

// The interrupt
void onPulse()
{
//pulseCounter
nPulses++;
previousTime = currentTime;
currentTime = micros();
  
  
  
//Calculate power (W)
power = ( ( 3600000000.0 * ( nPulses - oldPulses ) ) / ( currentTime - previousTime ) );
  
oldPulses = nPulses;

digitalWrite(led, !digitalRead(led));
    
}
/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

