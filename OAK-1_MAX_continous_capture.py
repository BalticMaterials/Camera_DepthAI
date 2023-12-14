""" Programm for capturing images on demand using the OAK-1 MAX by Luxonis.
"""

__author__ = "Sven Nivera"
__contact__ = "sven.nivera@balticmaterials.de"
__date__ = "2023/12/14"
__deprecated__ = False
__license__ = "CC0 1.0 Universal"
__maintainer__ = "Sven Nivera"
__status__ = "DEVELOPMENT"
__version__ = "0.2.0"
__annotations__ = "Capturing and saving locally."

import depthai as dai
import cv2
import time
from pathlib import Path

format = ".bmp"
resolution = dai.ColorCameraProperties.SensorResolution.THE_5312X6000
dirName = "continous_session" + str(time.time())
Path(dirName).mkdir(parents=True, exist_ok=True)


pipeline = dai.Pipeline()
camRgb = pipeline.create(dai.node.ColorCamera)

camRgb.setResolution(resolution)
camRgb.setFps(10)
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

with dai.Device(pipeline) as device:
    qRgb = device.getOutputQueue(name="rgb", maxSize=1, blocking=False)
    qStill = device.getOutputQueue(name="still", maxSize=1, blocking=True)
    qControl = device.getInputQueue(name="control")
    
    first = True
    while True:
        inRgb = qRgb.tryGet()  # Non-blocking call, will return a new data that has arrived or None otherwise
        if inRgb is not None and first:
            ctrl = dai.CameraControl()
            ctrl.setCaptureStill(True)
            qControl.send(ctrl)
            first = False            
        
        if qStill.has():            
            fName = f"{dirName}/{int(time.time() * 1000)}" + format            
            img = qStill.get().getCvFrame()                      
            cv2.imwrite(fName, img)         
            ctrl = dai.CameraControl()
            ctrl.setCaptureStill(True)
            qControl.send(ctrl)