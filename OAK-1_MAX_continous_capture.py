""" Programm for capturing images on demand using the OAK-1 MAX by Luxonis.
"""

__author__ = "Sven Nivera"
__contact__ = "sven.nivera@balticmaterials.de"
__date__ = "2023/12/04"
__deprecated__ = False
__license__ = "CC0 1.0 Universal"
__maintainer__ = "Sven Nivera"
__status__ = "DEVELOPMENT"
__version__ = "0.1.1"
__annotations__ = "Measuring performances"

import depthai as dai
import cv2
import time
from pathlib import Path

format = ".tiff"

pipeline = dai.Pipeline()

camRgb = pipeline.create(dai.node.ColorCamera)

# Possible Resolutions:
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_5312X6000)
# camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4000X3000)
# camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)

# camRgb.setFps(10)
camRgb.setNumFramesPool(2,2,2,1,1)

xoutRgb = pipeline.create(dai.node.XLinkOut)
xoutRgb.setStreamName("rgb")
camRgb.video.link(xoutRgb.input)

xin = pipeline.create(dai.node.XLinkIn)
xin.setStreamName("control")
xin.out.link(camRgb.inputControl)

# Linking
xoutStill = pipeline.create(dai.node.XLinkOut)
xoutStill.setStreamName("still")
camRgb.still.link(xoutStill.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    # Output queue will be used to get the rgb frames from the output defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=1, blocking=False)
    qStill = device.getOutputQueue(name="still", maxSize=1, blocking=True)
    qControl = device.getInputQueue(name="control")

    # Make sure the destination path is present before starting to store the examples
    dirName = "images"
    Path(dirName).mkdir(parents=True, exist_ok=True)
    first = True
    a = time.time()
    b = time.time()
    counter = 1
    times = 0
    cap = 0
    while True:
        inRgb = qRgb.tryGet()  # Non-blocking call, will return a new data that has arrived or None otherwise
        if inRgb is not None and first:
            ctrl = dai.CameraControl()
            ctrl.setCaptureStill(True)
            qControl.send(ctrl)
            first = False            
        
        if qStill.has():
            print("------------------------------------------")
            print("Image in Queue...")
            print("Capturing needed: ", time.time() - a, "s")
            cap += time.time() - a
            fName = f"{dirName}/{int(time.time() * 1000)}" + format
            print("Retrieving image...")
            a = time.time()
            img = qStill.get().getCvFrame()
            print("Time needed: ", time.time() - a, "s")
            print("Saving image...")
            a = time.time()                        
            cv2.imwrite(fName, img)
            print('Image saved to', fName) 
            print("Time needed: ", time.time() - a, "s")           
            ctrl = dai.CameraControl()
            ctrl.setCaptureStill(True)
            qControl.send(ctrl)
            print("Sent 'still' event to the camera...")
            a = time.time()
            print("Capture, retrieval and processing needed: ", time.time() - b,  "s")
            times += time.time() - b
            b = time.time()

            if counter == 100: break
            counter += 1

    times = times / counter
    cap = cap / counter
    f = open("benchmark.txt", "a")
    f.write("Resolution: " + str(camRgb.getResolution()) + "\n")
    f.write("Format: " + format + "\n")
    f.write("For 100 images...")
    f.write("Time overall: " + str(times) + "s\n")
    f.write("Time for capture: " + str(cap) + "s")
    f.write("--------------------------------")
    f.close()