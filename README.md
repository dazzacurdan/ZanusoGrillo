# ZanusoGrillo

#Add to /etc/rc.local
python3 /home/pi/ZanusoGrillo/ZanusoGrillo.py &
/home/pi/HPlayer/bin-raspbian-armv6/HPlayer --start 1 --ahdmi 1 --gl 1 --loop 1 --media /home/pi/media/LOOP-B-made.mp4 &
