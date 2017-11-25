import argparse
import threading
import RPi.GPIO as GPIO, time
from datetime import datetime

GPIO.setmode(GPIO.BCM)

from pythonosc import osc_message_builder
from pythonosc import udp_client

globalVideoPath = "/home/pi/media"
events = 0
lock = threading.Lock()

needToPrint = 0
count = 0
PIN_INPUT = 2
GPIO.setup(PIN_INPUT, GPIO.IN)

lastState = GPIO.LOW
trueState = GPIO.LOW
lastStateChangeTime = 0
cleared = 0

dialHasFinishedRotatingAfterMs = 100
debounceDelay = 10

targetProject = ""

def millis():
	return datetime.now().microsecond

def event_lock_holder(lock,delay):
    print('Starting')
    print('events is: {0}'.format(events))
    print('delay is: {0}'.format(delay))    
    
    global events
    th_id = 0
    lock.acquire()
    try:
        print("Increase")
        events += 1
        th_id = events
    finally:
        lock.release()
        
    time.sleep(delay)
        
    if events == th_id :
        print("/play "+globalVideoPath+"/LOOP-B-made.mp4")
        client.send_message("/play", globalVideoPath+"/LOOP-B-made.mp4" )
    else:
        print('terminated {0}'.format(th_id))
    return

def videoPaths(x):
    return {
       0: [globalVideoPath+"/00.mp4", 60 ],
       1: [globalVideoPath+"/01.mp4", 20 ],
       2: [globalVideoPath+"/02.mp4", 60 ],
       3: [globalVideoPath+"/03.mp4", 20 ],
       4: [globalVideoPath+"/04.mp4", 60 ],
       5: [globalVideoPath+"/05.mp4", 20 ],
       6: [globalVideoPath+"/06.mp4", 60 ],
       7: [globalVideoPath+"/07.mp4", 20 ],
       8: [globalVideoPath+"/08.mp4", 60 ],
       9: [globalVideoPath+"/09.mp4", 20 ],
       10: [globalVideoPath+"/10.mp4", 60 ],
       11: [globalVideoPath+"/11.mp4", 20 ]
    }.get(x, [globalVideoPath+"/00.mp4", 10 ])    # 9 is default if x not found

print('Zanuso - GRILLO HACKING')
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1",
    help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=9000,
    help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

# Main loop to print a message every time a pin is touched.
print('Press Ctrl-C to quit.')

while True:

    reading = GPIO.input(PIN_INPUT)

    if ((millis() - lastStateChangeTime) > dialHasFinishedRotatingAfterMs):
        # the dial isn't being dialed, or has just finished being dialed.
        if (needToPrint):
            # if it's only just finished being dialed, we need to send the number down the serial
            # line and reset the count. We mod the count by 10 because '0' will send 10 pulses.
            
            targetProject += str(count%10)
            #Serial.print(count % 10, DEC);
            path = ""
            if( len(targetProject) == 2):
                Serial.print(targetProject)
                if( targetProject == "00" ):
                    path = videoPaths(0)
                if( targetProject == "01" ):
                    path = videoPaths(1)    
                targetProject = ""
            print( "/play " + path[0] )
            client.send_message("/play", path[0] )
            threading.Thread(target=event_lock_holder, args=(lock,path[1]), name='eventLockHolder').start()

            needToPrint = 0
            count = 0
            cleared = 0

    if (reading != lastState):
        lastStateChangeTime = millis()

    if ((millis() - lastStateChangeTime) > debounceDelay):
        #debounce - this happens once it's stablized
        if (reading != trueState):
            # this means that the switch has either just gone from closed->open or vice versa.
            trueState = reading
            if (trueState == GPIO.HIGH):
                # increment the count of pulses if it's gone high.
                count = count + 1; 
                needToPrint = 1; # we'll need to print this number (once the dial has finished rotating)
    lastState = reading
