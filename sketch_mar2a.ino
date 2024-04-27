#include <Servo.h>

Servo myservo;  
int ledPin = 13; 

int pos = 0;    
unsigned long previousMillis = 0; 
const long interval = 3000; 

void setup() {
  myservo.attach(9); 
  pinMode(ledPin, OUTPUT); 
  
  Serial.begin(9600); 
  
  
  while (!Serial) {
    ;
  }
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read(); 
    
    if (command == 'H') { 
      for (pos = 90; pos <= 240; pos += 1) { 
        myservo.write(pos);             
        delay(15);                      
      }
      delay(2500);  
      
      for (pos = 240; pos >= 90; pos -= 1) { 
        myservo.write(pos);              
        delay(15);                       
      }
      delay(2500);  
    } else if (command == 'D') { 
      digitalWrite(ledPin, HIGH); 
      previousMillis = millis(); 
      
      while (millis() - previousMillis < interval) { 
       
      }
      
      digitalWrite(ledPin, LOW); 
    }
  }
}
