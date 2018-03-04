import argparse
import threading
import RPi.GPIO as GPIO, time
from datetime import datetime
from pygame import mixer

GPIO.setmode(GPIO.BCM)

from pythonosc import osc_message_builder
from pythonosc import udp_client

globalVideoPath = "/home/pi/media"
lock = threading.Lock()

needToPrint = 0
count = 0
PIN_INPUT = 2
BUTTON_PIN = 3
TEL_NUM_LENGTH = 8
GPIO.setup(PIN_INPUT, GPIO.IN)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

lastState = GPIO.LOW
trueState = GPIO.LOW
lastStateChangeTime = 0
cleared = 0

dialHasFinishedRotatingAfterMs = 100000 #100 in millisecond 
debounceDelay = 10000 # 10 in millisecond

targetProject = ""

def millis():
	return datetime.now().microsecond

def event_lock_holder(lock,delay):
    print('Lock.Starting')
    print('events is: {0}'.format(events))
    print('delay is: {0}'.format(delay))    
    
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
        print("/play "+globalVideoPath+"/Loop.mp4")
        client.send_message("/play", globalVideoPath+"/LOOP-B-Zanuso.mp4" )
    else:
        print('terminated {0}'.format(th_id))
    return

def videoPaths(x):
    return {
       0: [globalVideoPath+"/01-ZANUSO.mp4", 59 ],
       1: [globalVideoPath+"/02-ZANUSO.mp4", 53 ],
       2: [globalVideoPath+"/03-ZANUSO.mp4", 60 ],
       3: [globalVideoPath+"/04-ZANUSO.mp4", 67 ],
       4: [globalVideoPath+"/05-ZANUSO.mp4", 67 ],
       5: [globalVideoPath+"/06-ZANUSO.mp4", 80 ],
       6: [globalVideoPath+"/07-ZANUSO.mp4", 87 ],
       7: [globalVideoPath+"/08-ZANUSO.mp4", 59 ],
       8: [globalVideoPath+"/09-ZANUSO.mp4", 86 ],
       9: [globalVideoPath+"/10-ZANUSO.mp4", 52 ],
    }.get(x, [globalVideoPath+"/00.mp4", 10 ])    # 9 is default if x not found

print('Zanuso - GRILLO HACKING')
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="192.168.1.3",
    help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=9000,
    help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

parser_pc = argparse.ArgumentParser()
parser_pc.add_argument("--ip", default="192.168.1.79",
    help="The ip of the OSC server")
parser_pc.add_argument("--port", type=int, default=15000,
    help="The port the OSC server is listening on")
args_pc = parser_pc.parse_args()

client_pc = udp_client.SimpleUDPClient(args_pc.ip, args_pc.port)

global events
events = 0

mixer.init()
mixer.music.load("lineaCaduta.mp3")

# Main loop to print a message every time a pin is touched.
print('Press Ctrl-C to quit.')

while True:
    if GPIO.input(BUTTON_PIN) == False:
        print("reset number %s" % (targetProject))
        targetProject=""
        time.sleep(0.2)

    reading = GPIO.input(PIN_INPUT)

    if ((millis() - lastStateChangeTime) > dialHasFinishedRotatingAfterMs):
        # the dial isn't being dialed, or has just finished being dialed.
        if (needToPrint):
            # if it's only just finished being dialed, we need to send the number down the serial
            # line and reset the count. We mod the count by 10 because '0' will send 10 pulses.
            
            number = (count%10)-1
            if(number < 0):
                number = 9
            targetProject += str(number)
            print("Count is %d ,Target project is %s" % (count, targetProject))
            path = ""
            sendMessage = False
            number = 0
            if( len(targetProject) == TEL_NUM_LENGTH):
                print(targetProject)
                if( targetProject.find("11") > 5):
                    path = videoPaths(0)
                    sendMessage = True
                    number = 81#Q
                if( targetProject.find("54") > 5):
                    path = videoPaths(1)
                    sendMessage = True
                    number = 87#W
                if( targetProject.find("65") > 5):
                    path = videoPaths(2)
                    sendMessage = True
                    number = 69#E
                if( targetProject.find("76") > 5):
                    path = videoPaths(3)
                    sendMessage = True
                    number = 82#R
                if( targetProject.find("12") > 5):
                    path = videoPaths(4)
                    sendMessage = True
                    number = 84#T
                if( targetProject.find("53") > 5):
                    path = videoPaths(5)
                    sendMessage = True
                    number = 89#Y
                if( targetProject.find("25") > 5):
                    path = videoPaths(6)
                    sendMessage = True
                    number = 85#U    
                if( targetProject.find("21") > 5):
                    path = videoPaths(7)
                    sendMessage = True
                    number = 73#I
                if( targetProject.find("15") > 5):
                    path = videoPaths(8)
                    sendMessage = True
                    number = 65#A
                if( targetProject.find("34") > 5):
                    path = videoPaths(9)
                    sendMessage = True
                    number = 83#S

                print("TargetProject reset %s" % (targetProject))  
                targetProject = ""

                if sendMessage:
                    print( "/play " + path[0] )
                    client.send_message("/play", path[0] )
                    client_pc.send_message("/play", number)
                    threading.Thread(target=event_lock_holder, args=(lock,path[1]), name='eventLockHolder').start()
                else:
                     mixer.music.play()

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
