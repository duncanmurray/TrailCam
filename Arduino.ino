// 
// Simple example showing how to wake up the Arduino from a falling
// edge on a GPIO pin and then power up the Raspberry Pi
//
// NOTE: This library uses the "pinchangeint" library, which can be downloaded from
// https://code.google.com/p/arduino-pinchangeint/

// **** INCLUDES *****
#include "SleepyPi2.h"
#include <TimeLib.h>
#include <LowPower.h>
#include <PCF8523.h>
#include <Wire.h>
#include <PinChangeInt.h>

// Optimisation defines
#define NO_PORTC_PINCHANGES
#define DISABLE_PCINT_MULTI_SERVICE
#define NO_PIN_STATE
#define NO_PIN_NUMBER

// Define power off MS
#define kBUTTON_POWEROFF_TIME_MS   2000
#define kBUTTON_FORCEOFF_TIME_MS   8000

const int LED_PIN = 13;
const int WAKEUP_PIN = 8;  // Pin B0 - Arduino 8

// States
typedef enum {
  eWAIT = 0,
  eBUTTON_PRESSED,
  eBUTTON_HELD,
  eBUTTON_RELEASED
}eBUTTONSTATE;

typedef enum {
   ePI_OFF = 0,
   ePI_BOOTING,
   ePI_ON,
   ePI_SHUTTING_DOWN
}ePISTATE;

volatile bool  buttonPressed = false;
volatile bool  pirTriggered = false;

eBUTTONSTATE   buttonState = eBUTTON_RELEASED;
ePISTATE       pi_state = ePI_OFF;
bool state = LOW;
unsigned long  time, timePress;

void wakeup_isr()
{
    // Just a handler for the wakeup interrupt.
    pirTriggered = true;
}

void button_isr()
{
    // A handler for the Button interrupt.
    buttonPressed = true;
}

void setup()
{

  // Configure "Standard" LED pin
  pinMode(LED_PIN, OUTPUT);   
  digitalWrite(LED_PIN,LOW);    // Switch off LED
  
  // Configure "Wakeup" pin 
  pinMode(WAKEUP_PIN, INPUT);   // Set as input 

  // Allow wake up triggered by button press
  attachInterrupt(1, button_isr, LOW);    // button pin 

  // Attach WAKEUP_PIN to wakeup pi
  PCintPort::attachInterrupt(WAKEUP_PIN, wakeup_isr, RISING);

  // Set the initial Power to be off
  SleepyPi.enableExtPower(true);
  SleepyPi.enablePiPower(false);  
  
  
  // initialize serial communication: In Arduino IDE use "Serial Monitor"
  Serial.begin(9600);

  SleepyPi.rtcInit(true);

}

void loop()
{

    bool pi_running;

    // Attach WAKEUP_PIN to wakeup pi
    PCintPort::attachInterrupt(WAKEUP_PIN, wakeup_isr, RISING);
    
    // Enter power down state with ADC and BOD module disabled.
    pi_running = SleepyPi.checkPiStatus(true);  // Cut Power if we detect Pi not running
    if(pi_running == false){
      SleepyPi.enableExtPower(true); // Make sure that the external power is on
      SleepyPi.powerDown(SLEEP_FOREVER, ADC_OFF, BOD_OFF);
    }

    // Wake up when wake up pin is low.
    // Wake up when wake button is pressed
    // Once button is pressed stay awake.

    //PIR Triggered
    if(pirTriggered == true){
      // Remove interupt
      PCintPort::detachInterrupt(WAKEUP_PIN);
      
      // Print to serial
      Serial.println("Motion Detected");
      digitalWrite(LED_PIN,HIGH);   // Switch on LED
      delay(100);
      digitalWrite(LED_PIN,LOW);    // Switch off LED
      delay(100);
      digitalWrite(LED_PIN,HIGH);   // Switch on LED
      delay(100);
      digitalWrite(LED_PIN,LOW);    // Switch off LED
      delay(100);
      digitalWrite(LED_PIN,HIGH);   // Switch on LED
      delay(100);
      digitalWrite(LED_PIN,LOW);    // Switch off LED
      delay(100);
      
      // Reset variable
      pirTriggered = false;
      pi_running = SleepyPi.checkPiStatus(true);
      if(pi_running == false){
        // Switch on the Pi
        SleepyPi.enablePiPower(true);
        SleepyPi.enableExtPower(true);

        // Print to serial
        Serial.println("Motion Detected");
        digitalWrite(LED_PIN,HIGH);   // Switch on LED
        delay(250);
        digitalWrite(LED_PIN,LOW);    // Switch off LED
        delay(250);
        digitalWrite(LED_PIN,HIGH);   // Switch on LED
        delay(250);
        digitalWrite(LED_PIN,LOW);    // Switch off LED
        delay(250);
        digitalWrite(LED_PIN,HIGH);   // Switch on LED
        delay(250);
        digitalWrite(LED_PIN,LOW);    // Switch off LED
      }
    }

    // Button State changed
    if(buttonPressed == true){
        detachInterrupt(1);      
        buttonPressed = false;  
        switch(buttonState) { 
          case eBUTTON_RELEASED:
              // Button pressed           
              timePress = millis();             
              pi_running = SleepyPi.checkPiStatus(false);
              if(pi_running == false){  
                  // Switch on the Pi
                  SleepyPi.enablePiPower(true);
                  SleepyPi.enableExtPower(true);   
              }          
              buttonState = eBUTTON_PRESSED;
              digitalWrite(LED_PIN,HIGH);           
              attachInterrupt(1, button_isr, HIGH);                    
              break;
          case eBUTTON_PRESSED:
              // Button Released
              unsigned long buttonTime;
              time = millis();
              buttonState = eBUTTON_RELEASED;
              pi_running = SleepyPi.checkPiStatus(false);
              if(pi_running == true){
                  // Check how long we have held button for
                  buttonTime = time - timePress;
                  if(buttonTime > kBUTTON_FORCEOFF_TIME_MS){
                     // Force Pi Off               
                     SleepyPi.enablePiPower(false);
                     SleepyPi.enableExtPower(true);         
                  } else if (buttonTime > kBUTTON_POWEROFF_TIME_MS){
                      // Start a shutdown
                      SleepyPi.piShutdown();
                      SleepyPi.enableExtPower(true);            
                  } else { 
                     // Button not held off long - Do nothing
                  } 
              } else {
                  // Pi not running  
              }
              digitalWrite(LED_PIN,LOW);            
              attachInterrupt(1, button_isr, LOW);    // button pin       
              break;
           default:
              break;
        }                
    } 
}
