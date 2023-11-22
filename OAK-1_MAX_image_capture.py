""" Programm for capturing images on demand using the OAK-1 MAX by Luxonis.
"""

__author__ = "Sven Nivera"
__contact__ = "sven.nivera@balticmaterials.de"
__date__ = "2023/11/22"
__deprecated__ = False
__license__ = "CC0 1.0 Universal"
__maintainer__ = "Sven Nivera"
__status__ = "DEVELOPMENT"
__version__ = "0.1.4"
__annotations__ = "https://docs.luxonis.com/projects/api/en/latest/samples/ColorCamera/rgb_camera_control/#rgb-camera-control", 
"https://docs.luxonis.com/projects/api/en/latest/samples/VideoEncoder/rgb_full_resolution_saver/"

import time
from pathlib import Path
import cv2
import depthai as dai
import numpy as np

pipeline = dai.Pipeline()

camRgb = pipeline.create(dai.node.ColorCamera)
camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_5312X6000)
camRgb.setFps(10)
camRgb.setNumFramesPool(2,2,2,1,1)

xoutRgb = pipeline.create(dai.node.XLinkOut)
xoutRgb.setStreamName("rgb")
camRgb.video.link(xoutRgb.input)

xin = pipeline.create(dai.node.XLinkIn)
xin.setStreamName("control")
xin.out.link(camRgb.inputControl)

# Encoder not needed: https://discuss.luxonis.com/d/967-oak-d-poe-pro-making-camera-send-image-only-when-i-need/5

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

    while True:
        inRgb = qRgb.tryGet()  # Non-blocking call, will return a new data that has arrived or None otherwise
        if inRgb is not None:
            frame = inRgb.getCvFrame()
            # 4k / 4
            frame = cv2.pyrDown(frame)
            frame = cv2.pyrDown(frame)
            cv2.imshow("Real-Time Preview", frame)

        if qStill.has():
            fName = f"{dirName}/{int(time.time() * 1000)}.jpeg"
            img = qStill.get().getCvFrame()            
            cv2.imwrite(fName, img)            
            print('Image saved to', fName)            

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('c'):
            ctrl = dai.CameraControl()
            ctrl.setCaptureStill(True)
            qControl.send(ctrl)
            print("Sent 'still' event to the camera!")