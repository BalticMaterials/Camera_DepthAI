""" Translation of the same named Notebook code.
Neccessary for accessing the logging capabilities of the OAK-1 MAX.
"""

__author__ = "Sven Nivera"
__contact__ = "sven.nivera@balticmaterials.de"
__date__ = "2023/08/10"
__deprecated__ = False
__license__ = "CC0 1.0 Universal"
__maintainer__ = "Sven Nivera"
__status__ = "Production"
__version__ = "1.0.0"

import cv2
import depthai as dai
import numpy as np

pipeline = dai.Pipeline()

cam = pipeline.create(dai.node.ColorCamera) # add cam
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_5312X6000) # 32MP
# cam.setNumFramesPool(2,2,1,1,1) usefull for minimizing RAM usage

xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam.preview.link(xout_rgb.input)

def frameNorm(frame, bbox):
    normVals = np.full(len(bbox), frame.shape[0])
    normVals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

with dai.Device(pipeline) as device: # initialize device via USB3
    device.setLogLevel(dai.LogLevel.INFO)
    device.setLogOutputLevel(dai.LogLevel.INFO)
    q_rgb = device.getOutputQueue("rgb") # frame queue for host side filling up with frames from the cam
    frame = None
    while True:
        in_rgb = q_rgb.tryGet() # Consuming latest (or None) frame from queue
        if in_rgb is not None:
            frame = in_rgb.getCvFrame() # Receive frame 
            if frame is not None:
                cv2.imshow("preview", frame)
                if cv2.waitKey(1) == ord('q'):
                    break