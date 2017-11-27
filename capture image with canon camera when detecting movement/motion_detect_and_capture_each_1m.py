from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess
import io
from io import StringIO
import subprocess
import os
import time
from datetime import datetime
#from PIL import Image
#kill the gphoto process
def killgphoto2():
    p = subprocess.Popen(['ps','-A'],stdout=subprocess.PIPE)
    out, err = p.communicate()

    #search fro the line we want to kill
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            #kill the process
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)

shot_date = datetime.now().strftime("%Y-%m-%d")
shot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
picID = "PiShots"

clearCommand = ["--folder","/store_00020001/DCIM/100EOS1D","-R","--delete-all-files"]
triggerCommand = ["--trigger-capture"]
downloadCommand = ["--get-all-files"]

folder_name = shot_date + picID
save_location = "/home/pi/metabolon/test/images" + folder_name

def createSaveFolder():
    try:
        os.makedirs(save_location)
    except:
        print("Failed to create the new directory.")
    os.chdir(save_location)

def captureImages():
    gp(triggerCommand)
    sleep(1)
    gp(downloadCommand)
    gp(clearCommand)

def renameFiles(ID):
    for filename in os.listdir("."):
        if len(filename) < 13:
            if filename.endswith(".JPG"):
                os.rename(filename, (shot_time + ID + ".JPG"))
                print ("Renamed the JPG")
            elif filename.endswith(".CR2"):
                os.rename(filename, (shot_time + ID + ".JPG"))
                print("Renamed the CR2")

killgphoto2()
gp(clearCommand)
###############################################
##############################################
import io
import picamera
from PIL import Image
scan = True
images = []


color_offset = 25 # Adjusts for slight varitaions in color

while(scan):
	stream = io.BytesIO()
	with picamera.PiCamera() as camera:
		camera.resolution = (64,36) #Low Res For Faster Comparisons
		camera.start_preview()
		camera.capture(stream, format='jpeg')
	stream.seek(0)	

	if(len(images)!=2):
		images.append(Image.open(stream))
	else:
		images[0] = Image.open(stream)
	
	x = 0
	y = 0
	diff = 0

	if len(images) != 1:
		#Start On X and Move Down Y 
		while(x < images[0].size[0]):
			while(y < images[0].size[1]):

				#Add Up All RGB Values For Current Pixel
				img1 = images[1].getpixel((x,y))
				val = img1[0] + img1[1] + img1[2]
				img2 = images[0].getpixel((x,y))
				val2 = img2[0] + img2[1] + img2[2]
				
				pd = abs(val2-val)
				
				if(pd > color_offset):
					diff += 1
				y += 1
				
			#Move Right 1 & Reset Y For Next Loop
			x+=1
			y=0
		
		changed  = (diff * 100) / (images[0].size[0] * images[0].size[1])
		if changed > 20:
                    createSaveFolder() 
                    captureImages()
                    renameFiles(picID)
                    sleep(15)
		print( str(changed) + "% changed.")
		images[1] = images[0]


