# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 13:04:52 2015

@author: twagner
"""

### imports ###################################################################
import logging
import numpy as np
import os

from .fd3 import FD3Reader

###############################################################################
logging.getLogger('mikrocad').addHandler(logging.NullHandler())

### LMI MikroCAD premium mock up ##############################################
class MikroCAD_Mock:
    def __init__(self, parameterDict):
        self.logger = logging.getLogger('mikrocad')

        Nx = 1624
        Ny = 1236
        Nxy = Nx * Ny

        self.dummyImage = np.random.randint(0, 255, Nxy, dtype='uint8')

        self.paraDict = {
            'camera brightness': 7,
            'projector': 1,
            'dynamic mode': 2,
            'x-size': Nx,
            'y-size': Ny,
            'invalidValue': -10010,
            'max projection area x-size': 1.608,
            'max projection area y-size': 1.787,
            'shutterCam': 0,
            'shutterTimeBaseCam': 0,
            'x-scale': 0.00305,
            'x-scale_ref': 0.00305,
            'y-scale': 0.00305,
            'y-scale_ref': 0.00305,
            'z-scale': 0.0001,
        }

        self.ptrScan = np.zeros(Nxy, dtype='int16')

        self.paraName = {
            11: 'brightnessCam',
            12: 'dynamicMode',
            16: 'projector',
            21: '',
            22: '',
            111: '',
            112: '',
            113: '',
            114: '',
            115: '',
            201: '',
            202: '',
        }
    
    def _GFM_DeinitializeMeasurementModule(self):
        # void method to deinitialise the measurement module
        pass
        
    def _GFM_GetCameraImage(self, value):
        return self.dummyImage
       
    def _GFM_GetInvalidProfileValue(self):
        return self.paraDict['invalidValue']
        
    def _GFM_GetMeasParameterFloat(self, parameterID, value):
        return 0
        
    def _GFM_GetMeasParameterInt(self, parameterID, value):
        return 0

    def _GFM_GetMeasParameterLimitsInt(self, parameterID,
                                       lowerLimit, upperLimit):
        return 0
        
    def _GFM_GetMeasProgCatalogName(self, index):
        return 0

    def _GFM_GetMeasProgItemName(self, i, j):
        return 0
            
    def _GFM_GetMeasProgItems(self, index):
        return 0

    def _GFM_GetNumMeasProgCatalogs(self):
        return 0
       
    def _GFM_GetNumberMeasProgItems(self, index):
        return 0

    def _GFM_HaltContinueLiveImage(self, liveOn):
        return 0
        
    def _GFM_InitializeMeasurementModule(self):
        return 0

    def _GFM_LoadDataFile(self, a, b, c, d, e, f):
        return True

    def _GFM_MeasParameterAvailable(self, parameter_id, available):
        isAvailable = True if parameter_id in self.paraName.keys() else False
        available.contents.value = isAvailable
        
        return 0
        
    def _GFM_Measurement(self, value):
        # Set raw datapoints
        # from myfilereader import kantenprofil
        filepath = "data"
        filename = "mounting_plate.fd3"
        fullfile = os.path.join(filepath, filename)
        fd3 = FD3Reader(fullfile)
        self.ptrScan = fd3.Image

        self.paraDict['xScale'] = fd3.dx
        self.paraDict['yScale'] = fd3.dy
        self.paraDict['zScale'] = fd3.dz
        
        return 0

    def _GFM_ProjectPattern(self, patternID):
        return 0
        
    def _GFM_ProjectImage(self, image):
        return 0

    def _GFM_PtrToCameraData(self):
        return 0
    
    def _GFM_PtrToProfileData(self):
        return self.ptrScan
        
    def _GFM_PtrToValidData(self):
        return 0

    def _GFM_SaveCameraData(self, filename, fileFormat):
        return 0
        
    def _GFM_SaveProfileData(self, filename, fileFormat, colorMode):
        return 0

    def _GFM_SetLanguage(self, language):
        return 0
        
    def _GFM_SetMeasParameterInt(self, parameterID, value):
        parameterName = self.paraName[parameterID]

        self.logger.debug(
            "Setting %s with id %i to %i",
            parameterName, parameterID, value
        )

        self.paraDict[parameterName] = value

        return 0

    def _GFM_SetProgramPath(self, path):
        return 0
        
    def _GFM_StartLiveImage(self, handle, i1, i2, b):
        return 0

    def  _GFM_WriteLogFile(self, value):
        return 0
