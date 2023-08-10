""" Programm for capturing images on demand using the OAK-1 MAX by Luxonis.
"""

__author__ = "Sven Nivera"
__contact__ = "sven.nivera@balticmaterials.de"
__date__ = "2023/08/10"
__deprecated__ = False
__license__ = "CC0 1.0 Universal"
__maintainer__ = "Sven Nivera"
__status__ = "DEVELOPMENT"
__version__ = "0.1.0"

import cv2
import depthai as dai
import numpy as np

pipeline = dai.Pipeline()

cam = pipeline.create(dai.node.ColorCamera) # add cam
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_5312X6000) # 32MP
cam.setNumFramesPool(2,2,1,1,1) # usefull for minimizing RAM usage

stillEncoder = pipeline.create(dai.node.VideoEncoder)
stillMjpegOut = pipeline.create(dai.node.XLinkOut)
stillMjpegOut.setStreamName('still')
stillEncoder.setDefaultProfilePreset(1, dai.VideoEncoderProperties.Profile.MJPEG)
cam.still.link(stillEncoder.input)
stillEncoder.bitstream.link(stillMjpegOut.input)

with dai.Device(pipeline) as device: # initialize device via USB3
    device.setLogLevel(dai.LogLevel.INFO)
    device.setLogOutputLevel(dai.LogLevel.INFO)
    stillQueue = device.getOutputQueue('still')    
    i = 0

    while True:
        stillFrames = stillQueue.tryGetAll()
        for stillFrame in stillFrames:
            # Decode JPEG
            frame = cv2.imdecode(stillFrame.getData(), cv2.IMREAD_UNCHANGED)
            # Display
            cv2.imshow('still', frame)            
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            elif key == ord('n'):
                cv2.imwrite("Frame " + str(i).jpeg, frame)
                i += 1
            