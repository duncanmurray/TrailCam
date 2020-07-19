from picamera import PiCamera
from time import sleep
import os
import subprocess
from subprocess import call
import time
import board
#import adafruit_dht
from datetime import datetime
import picamera
import serial
import smbus2
import bme280

ser = serial.Serial(
    #port='/dev/ttyAMA0',
    port='/dev/ttyS0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)


save_directory = "/home/pi/Projects/TrailCam/captures/"
if not os.path.exists(save_directory):
        os.makedirs(save_directory)

def next_path(path_pattern):
    """
    Finds the next free path in an sequentially named list of files

    e.g. path_pattern = 'file-%s.txt':

    file-1.txt
    file-2.txt
    file-3.txt

    Runs in log(n) time where n is the number of existing files in sequence
    """
    i = 1

    # First do an exponential search
    while os.path.exists(path_pattern % i):
        i = i * 2

    # Result lies somewhere in the interval (i/2..i]
    # We call this interval (a..b] and narrow it down until a + 1 = b
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2 # interval midpoint
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

    return path_pattern % b


#Create a function for taking videos and converting them to MP4
def capture_video(file_h264, file_mp4, vid_length):
    camera.rotation = 180
    camera.resolution = (1640, 1232)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text_size = 25
    camera.annotate_text = "Date: {}   Temp: {}C   Humidity: {}% ".format(current_time, temperature, humidity)
    # Record a 15 seconds video.
    print("Info: Capturing {} second video as {}".format(vid_length, file_h264))
    camera.start_recording(file_h264)
    while (datetime.now() - now).seconds < vid_length:
    #sleep(vid_length)
        camera.annotate_text = "Date: {}   Temp: {}C   Humidity: {}% ".format(current_time, temperature, humidity)
        camera.wait_recording(0.2)
    camera.stop_recording()
    #Convert the h264 format to the mp4 format.
    print("Info: Converting video to MP4 as {}".format(file_mp4))
    command = "MP4Box -add " + file_h264 + " " + file_mp4
    call([command], shell=True)

#Create a function for taking pictures
def capture_photo(file_jpg):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    camera.resolution = (2592, 1944)
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text_size = 25
    camera.annotate_text = "Date: {}   Temp: {}C   Humidity: {}% ".format(current_time, temperature, humidity)
    camera.rotation = 180
    print("Info: Capturing still image as {}".format(file_jpg))
    camera.capture(file_jpg)

#BME280 Temerature Sensor
port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

# the sample method will take a single reading and return a
# compensated_reading object
bme280data = bme280.sample(bus, address, calibration_params)

# the compensated_reading class has the following attributes
#print(bme280data.id)
#print(bme280data.timestamp)
#print(bme280data.temperature)
#print(bme280data.pressure)
#print(bme280data.humidity)

# there is a handy string representation too
#print(bme280data)

temperature = round(bme280data.temperature,1)
humidity = round(bme280data.humidity,1)


# For some reason this can't go in a function
#def get_temperature():
# Initial the dht device, with data pin connected to:
#dhtDevice = adafruit_dht.DHT11(board.D17)
#Start the counter at 0
#attempts = 0
#Change how many attempts to try to read the sensor
#while attempts < 2:
#    print("Info: Attempt {} to read DHT sensor".format(attempts))
#    try:
#        # Print the values to the serial port
#        temperature_c = dhtDevice.temperature
#        temperature_f = temperature_c * (9 / 5) + 32
#        humidity = dhtDevice.humidity
#        break
#    except RuntimeError as error:
#        #Increment the counter
#        attempts += 1
#        # Errors happen fairly often, DHT's are hard to read, just keep going
#        print("Error: Unable to retreive data from DHT sensor")
#        print("Error: {}".format(error.args[0]))
#        
#    time.sleep(2.0)
#    if attempts == 2:
#        temperature_c = 0
#        temperature_f = 0
#        humidity = 0



camera = PiCamera()

#Take picture n times
photo_num = 3
for i in range(photo_num):
    print("Info: Attemptng to capture {} still images".format(photo_num))
    image_filename = next_path(save_directory + 'IMAGE%s.jpg')
    capture_photo(image_filename)

#Ideally find a way to not have to specify file extention
video_filename = next_path(save_directory + 'VIDEO%s.h264')
#Take Video.  Doing it this way just adds .mp4 to the video name
capture_video(video_filename, video_filename + ".mp4", 10)

timeout_seconds = 60*2
timeout_time = time.time() + timeout_seconds   # N minutes from now
print("Info: Waiting up to {} seconds for further motion".format(timeout_seconds))

while True:
    read_ser=ser.readline()
    read_ser_ascii = read_ser.decode('ASCII')
    if(read_ser_ascii.strip()=="Motion Detected"):
        print("Info: PIR sensor detected further motion")
        #Ideally find a way to not have to specify file extention
        video_filename = next_path(save_directory + 'VIDEO%s.h264')
        #Take Video.  Doing it this way just adds .mp4 to the video name
        capture_video(video_filename, video_filename + ".mp4", 10)
        
        timeout_time = time.time() + timeout_seconds   # N minutes from now
        print("Info: Waiting up to {} seconds for further motion".format(timeout_seconds))


    test = 0
    if test == 5 or time.time() > timeout_time:
        print("Warning: Exiting because no motion was detected in {} seconds".format(timeout_seconds))
        break
    test = test - 1

# Shutdown now that we're finished
print("Warning: Shutting down Raspberry Pi")
#call("sudo shutdown -h now", shell=True)

