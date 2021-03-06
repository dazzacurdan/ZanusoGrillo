#include <Keyboard.h>

int needToPrint = 0;
int count;
int in = 2;
int lastState = LOW;
int trueState = LOW;
long lastStateChangeTime = 0;
int cleared = 0;

// constants

int dialHasFinishedRotatingAfterMs = 100;
int debounceDelay = 10;

String targetProject;

void setup()
{
    Serial.begin(9600);
    //Keyboard.begin();
    pinMode(in, INPUT);
    targetProject = "";
}

void loop()
{
    int reading = digitalRead(in);

    if ((millis() - lastStateChangeTime) > dialHasFinishedRotatingAfterMs) {
        // the dial isn't being dialed, or has just finished being dialed.
        if (needToPrint) {
            // if it's only just finished being dialed, we need to send the number down the serial
            // line and reset the count. We mod the count by 10 because '0' will send 10 pulses.
            targetProject += String(count % 10);
            //Serial.print(count % 10, DEC);

            if(targetProject.length() == 2)
            {
                Serial.print("Project is: ");
                Serial.println(targetProject);
                if( targetProject == "00" )
                {
                    //Keyboard.press('q');
                }
                if( targetProject == "01" )
                {
                    //Keyboard.press('w');
                }
                if( targetProject == "02" )
                {
                    //Keyboard.press('e');
                }
                if( targetProject == "03" )
                {
                    //Keyboard.press('r');
                }
                if( targetProject == "04" )
                {
                    //Keyboard.press('t');
                }
                if( targetProject == "05" )
                {
                    //Keyboard.press('a');
                }
                if( targetProject == "06" )
                {
                    //Keyboard.press('s');
                }
                if( targetProject == "07" )
                {
                    //Keyboard.press('d');
                }
                if( targetProject == "08" )
                {
                    //Keyboard.press('f');
                }
                if( targetProject == "09" )
                {
                    //Keyboard.press('g');
                }
                //delay(10);
                //Keyboard.releaseAll();
                targetProject = "";
            } 
            
            needToPrint = 0;
            count = 0;
            cleared = 0;
        }
    } 

    if (reading != lastState) {
        lastStateChangeTime = millis();
        Serial.print("lastStateChangeTime:");
        Serial.println(lastStateChangeTime);
    }

    if ((millis() - lastStateChangeTime) > debounceDelay) {
        // debounce - this happens once it's stablized
        if (reading != trueState) {
            // this means that the switch has either just gone from closed->open or vice versa.
            trueState = reading;
            if (trueState == HIGH) {
                // increment the count of pulses if it's gone high.
                count++; 
                needToPrint = 1; // we'll need to print this number (once the dial has finished rotating)
            } 
        }
    }
    lastState = reading;
} 
