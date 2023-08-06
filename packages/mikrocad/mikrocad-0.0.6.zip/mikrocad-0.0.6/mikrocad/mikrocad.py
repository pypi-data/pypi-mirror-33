# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 13:04:52 2015

@author: twagner
"""

### imports ###################################################################
import logging
import numpy as np
import os
import sys
import yaml

if os.name != "posix":
    import win32com.client

### imports from ##############################################################
from ctypes import CDLL
from ctypes import c_char_p, c_bool
from ctypes import c_byte, c_double, c_int, c_int16, c_short, c_uint8, c_long
from ctypes import byref, pointer, POINTER

### relative imports from #####################################################
from .mikrocad_mock import MikroCAD_Mock
from .parameter import Parameter

###############################################################################
logging.getLogger('mikrocad').addHandler(logging.NullHandler())

###############################################################################
# LMI MikroCAD premium
###############################################################################
class MikroCAD(object):
    '''
    This class binds its methods to the GFM API in Measurement.dll
    '''
    
    def __init__(self, filename):
        self.logger = logging.getLogger('mikrocad')
        self.logger.info("Starting LMI MikroCAD premium")

        self._brightnessCam = 0
        self._invalidValue = -10010
        self._language = 0
        self._programPath = ''
        self.temp_path = ''

        self.hardwareParameter = {}
        
        with open(filename) as f:    
            self.hardwareParameter = yaml.load(f)        

        # print(self.hardwareParameter)
        
        self.hardwareFound = False
        self.LMI_DLL = None

        for key, value in self.hardwareParameter.items():
            if key == 'language':
                self._language = value
            elif key == 'program_path':
                self._programPath = value
            elif key == 'temp_path':
                self.temp_path = value

        #%% properties
        self._brightnessProjector = 1
        self._dynamicMode = 0
        self._projectionPattern = 0
        self._shutterCam = 0
        self._shutterTimeBaseCam = 100

        self.hardwareFound = self.searchHardware()
            
        if self.hardwareFound:
            self.loadDLL()
            self.liveImage = True
        else:
            self.switchToEmulator()
            self.liveImage = False
        
        self.logFile = os.path.join(self._programPath, 'gfm.log')
        self.writeLogFile()

        self.language = self._language
        self.programPath = self._programPath

        self.paraDict = {}

        for key, values in self.hardwareParameter['parameters'].items():
            id = values['id']
            cType = values['type']
            
            limits = values['limits'] if 'limits' in values.keys() else False
            
            parameter = Parameter(id, key, cType, limits)
            self.paraDict[key] = parameter

    ### properties
    @property
    def brightnessCam(self):
        self._brightnessCam = self.getParameter('camera brightness')
        return self._brightnessCam

    @brightnessCam.setter
    def brightnessCam(self, value):
        self.setParameter('camera brightness', value)

    #%%        
    @property
    def brightnessProjector(self):
        self._brightnessProjector = self.getParameter('projector')
        return self._brightnessProjector

    @brightnessProjector.setter
    def brightnessProjector(self, value):
        self.setParameter('projector', value)

    #%%
    @property
    def dynamicMode(self):
        self._dynamicMode = self.getParameter('dynamic mode')
        return self._dynamicMode

    @dynamicMode.setter
    def dynamicMode(self, value):
        self.setParameter('dynamic mode', value)

    #%%
    @property
    def invalidValue(self):
        # integer value which corresponds to NaN            
        self._invalidValue = self.LMI_DLL._GFM_GetInvalidProfileValue()
        return self._invalidValue


    #%%
    @property
    def language(self):
        return self._language
        
    @language.setter
    def language(self, value):
        self._language = value
        if value == 0:
            self.logger.info("Language: %s", 'german')
        else:
            self.logger.info("Language: %s", 'german')

        self.LMI_DLL._GFM_SetLanguage(value)

    #%%
    @property
    def max_projection_area_x_size(self):
        self._max_projection_area_x_size = self.getParameter(
                'max projection area x-size')
        
        return self._max_projection_area_x_size

    #%%
    @property
    def max_projection_area_y_size(self):
        self._max_projection_area_y_size = self.getParameter(
                'max projection area y-size')
        return self._max_projection_area_y_size

    #%%
    @property
    def programPath(self):
        return self._programPath
        
    @programPath.setter
    def programPath(self, filepath):
        self.logger.info("path: %s", filepath)
        c_progPath = c_char_p(filepath.encode('utf-8'))

        self.LMI_DLL._GFM_SetProgramPath(c_progPath)

        self._programPath = filepath

    #%%
    @property
    def projectionPattern(self):
        return self._projectionPattern
        
    @projectionPattern.setter
    def projectionPattern(self, value):
        self._projectionPattern = value
        self.LMI_DLL._GFM_ProjectPattern(value)


    #%%        
    @property
    def shutterCam(self):
        self._shutterCam = self.getParameter('shutterCam')
        return self._shutterCam

    @shutterCam.setter
    def shutterCam(self, value):
        self.setParameter('shutterCam', value)

    #%%        
    @property
    def shutterTimeBaseCam(self):
        self._shutterTimeBaseCam = self.getParameter('shutterTimeBaseCam')
        return self._shutterTimeBaseCam

    @shutterTimeBaseCam.setter
    def shutterTimeBaseCam(self, value):
        self.setParameter('shutterTimeBaseCam', value)

    @property
    def x_scale(self):
        self._x_scale = self.getParameter('x-scale')
        return self._x_scale

    @property
    def x_scale_ref(self):
        self._x_scale_ref = self.getParameter('x-scale_ref')
        return self._x_scale_ref

    @property
    def x_size(self):
        self.Nx = self.getParameter('x-size')
        return self.Nx

    @property
    def y_scale(self):
        self._y_scale = self.getParameter('y-scale')
        return self._y_scale

    @property
    def y_scale_ref(self):
        self._y_scale_ref = self.getParameter('y-scale_ref')
        return self._y_scale_ref

    @property
    def y_size(self):
        self.Ny = self.getParameter('y-size')
        return self.Ny

    @property
    def z_scale(self):
        self._z_scale = self.getParameter('z-scale')
        return self._z_scale

    ### methods
    def deinitMeasurement(self):
        self.logger.info("Deinitialising Measurement module")
        self.LMI_DLL._GFM_DeinitializeMeasurementModule()

    def doMeasure(self):
        self.logger.info("measuring ...")
        error = self.LMI_DLL._GFM_Measurement(True)
        
        if error:
            self.logger.error("Error: %s", error)
            return error
        
        dx = self.getParameter('x-scale')
        dy = self.getParameter('y-scale')
        dz = self.getParameter('z-scale')
        self.scale = (dx, dy, dz)

        # scan data
        self.ptrScan = self.LMI_DLL._GFM_PtrToProfileData()

        # camera data
        self.ptrCam = self.LMI_DLL._GFM_PtrToCameraData()

        # valid data
        self.ptrValid = self.LMI_DLL._GFM_PtrToValidData()

        return error

    def initMeasurement(self):
        self.logger.debug("Initialising measurement module")

        # changing to program directory omits Error -2001:
        # Error initialising measurement module
        currentDir = os.getcwd()
        os.chdir(self.programPath)
        error = self.LMI_DLL._GFM_InitializeMeasurementModule()
        os.chdir(currentDir)

        self.initialised = error

        if error != 0:
            self.logger.warning(
                "Could not initialise measurement module: %i", error
            )
            
            self.switchToEmulator()
        
        return error

    '''
    def initParameters(self):
            self.brightnessCam = self.hardwareParameter['brightnessCam']
            self.dynamicMode = self.hardwareParameter['dynamicMode']
            self.shutterCam = self.hardwareParameter['shutterCam']
            
            self.shutterTimeBaseCam = (
                self.hardwareParameter['shutterTimeBaseCam'])
                
            self.brightnessProjector = (
                self.hardwareParameter['brightnessProjector'])
                
            self.projectionPattern = (
                self.hardwareParameter['projectionPattern'])
    '''
    
    def loadDLL(self):
        dllFile = os.path.join(self._programPath, "Measurement.dll")

        ### look for the DLL file
        if os.path.isfile(dllFile):
            self.dllFound = True

            self.logger.debug("Loading %s", dllFile)
            
            currentDir = os.getcwd()
            os.chdir(self._programPath)

            self.LMI_DLL = CDLL('Measurement')

            self.LMI_DLL._GFM_GetInvalidProfileValue.restype = c_int16

            self.LMI_DLL._GFM_GetMeasProgCatalogName.restype = c_char_p
            self.LMI_DLL._GFM_GetMeasProgItemName.restype = c_char_p

            self.LMI_DLL._GFM_LoadDataFile.restype = c_bool

            self.LMI_DLL._GFM_PtrToCameraData.restype = POINTER(c_short)
            self.LMI_DLL._GFM_PtrToProfileData.restype = POINTER(c_short)
            self.LMI_DLL._GFM_PtrToValidData.restype = POINTER(c_byte)

            os.chdir(currentDir)
        else:
            self.dllFound = False
            
            self.logger.error("Could not find file %s", dllFile)

        return self.dllFound


    def loadFile(self, filename):
        if os.name == "posix":
            return -1

        # self.LMI_DLL._GFM_LoadDataFile.restype = c_bool

        Nxy = 1624 * 1236

        dataPointer = pointer(c_short())
        validPointer = pointer(c_byte())

        cShort_Data_Array = (c_short * Nxy)()
        cByte_Valid_Array = (c_byte * Nxy)()
        
        cDouble_Scale_Array = (c_double * 3)()

        cNx = c_short()
        cNy = c_short()

        # using arrays
        success = self.LMI_DLL._GFM_LoadDataFile(
            filename,
            byref(cShort_Data_Array),
            byref(cByte_Valid_Array),
            byref(cNx), byref(cNy),
            byref(cDouble_Scale_Array)
        )

        # using pointers
        success = self.LMI_DLL._GFM_LoadDataFile(
            filename,
            dataPointer,
            validPointer,
            byref(cNx), byref(cNy),
            byref(cDouble_Scale_Array)
        )

        Nx = cNx.value
        Ny = cNy.value

        self.logger.debug("loadFile: %s", success)
        self.logger.debug("DEBUG Nx: %s", Nx)
        self.logger.debug("DEBUG Ny: %s", Ny)
        self.logger.debug("DEBUG scale: %s", cDouble_Scale_Array[:])

        self.logger.debug("DEBUG valid: %s", cByte_Valid_Array[0:100])
        self.logger.debug("DEBUG data: %s", cShort_Data_Array[0:100])

        self.logger.debug("DEBUG valid: %s", validPointer[0:100])
        self.logger.debug("DEBUG data: %s", dataPointer[0:100])

        return success

    def measParameterAvailable(self, parameter_id):
        available = c_bool()
        
        '''
        error = self.LMI_DLL._GFM_MeasParameterAvailable(
                parameter_id, byref(available))
        '''

        error = self.LMI_DLL._GFM_MeasParameterAvailable(
                parameter_id, pointer(available))
        
        if error:
            self.logger.error(
                "Error reading parameter %s: %s", parameter_id, error)
        
        
        return available.value
        
    '''
    def loadParameters(self):
        
        filepath = os.path.dirname(os.path.abspath(__file__))
        fullfile = os.path.join(filepath, 'mikrocad.json')
        
        with open(fullfile) as data_file:    
            data = json.load(data_file)

        print(data)

        hardwareData = data['Hardware']

        self.setParameter('brightnessCam', hardwareData['BrightnessCam'])
   ''' 
        
    def searchHardware(self):
        hardwareFound = False

        if os.name != "posix":
            wmi = win32com.client.GetObject("winmgmts:")
    
            for usb in wmi.InstancesOf("Win32_USBHub"):
                if 'USB\VID_2032&PID_0101' in usb.DeviceID:
                    self.logger.info("found GFM Alligator")
                    hardwareFound = True
                    break
    
            if not hardwareFound:
                self.logger.error("Could not find GFM Alligator!")
            
        return hardwareFound

    def switchToEmulator(self):
        self.mockUp = True
        self.logger.warning("Switching to MikroCAD mock up")
        self.LMI_DLL = MikroCAD_Mock(self.hardwareParameter)

    def writeLogFile(self, override = True):
        self.logger.info("Logging to: %s", self.logFile)
        
        if override and os.path.exists(self.logFile):
            os.remove(self.logFile)
        
        self.LMI_DLL._GFM_WriteLogFile(True)

    def setParameter(self, name, value):
        parameter = self.paraDict[name]
        id = parameter.id
        cType = parameter.cType

        self.logger.info("Setting parameter %s to %s", parameter.name, value)
        
        if cType == 'int':
            error = self.LMI_DLL._GFM_SetMeasParameterInt(id, value)
        elif cType == 'long':
            error = self.LMI_DLL._GFM_SetMeasParameterInt(id, value)

        if error != 0:
            self.logger.error(
                "Error setting parameter %s to value %s: %i",
                parameter.name, str(value), error
            )
        else:
            self.getParameter(name)

    def setProjectionPattern(self, pattern):
        self.LMI_DLL._GFM_ProjectPattern(pattern)

    def getParameter(self, name):
        parameter = self.paraDict[name]
        id = parameter.id
        cType = parameter.cType
        cInt1 = c_int()
        error = -1

        if self.hardwareFound:
            if cType == 'int':
                error = self.LMI_DLL._GFM_GetMeasParameterInt(id, byref(cInt))
                parameter.value = cInt.value
            elif cType == 'long':
                error = self.LMI_DLL._GFM_GetMeasParameterInt(id, byref(cLong))
                parameter.value = cLong.value
            elif cType == 'double':
                error = self.LMI_DLL._GFM_GetMeasParameterFloat(
                    id, byref(cDouble)
                )
               
                parameter.value = cDouble.value
        else:
            parameter.value = self.LMI_DLL.paraDict[name]
            error = 0
            
        if error != 0:
            self.logger.error(
                "Error reading parameter %s: %s", parameter.name, error)
        else:
            if type(parameter.value) == np.float64:
                self.logger.debug(
                        "%s: %10.6G", parameter.name, parameter.value)
            else:
                self.logger.debug("%s: %s", parameter.name, parameter.value)

        errorLimits = -1
        
        if parameter.hasLimits:
            if self.hardwareFound:
                errorLimits = self.LMI_DLL._GFM_GetMeasParameterLimitsInt(
                    id,
                    byref(cInt),
                    byref(cInt1)
                )
                
                parameter.lowerLimit = cInt.value
                parameter.upperLimit = cInt1.value
            else:
                parameter.lowerLimit = 0
                parameter.upperLimit = 10
                errorLimits = 0

            if errorLimits != 0:
                self.logger.error(
                    "Error reading parameter %s limits: %s", parameter.name,
                    errorLimits
                )
            else:
                self.logger.debug(
                    '%s lower limit: %s', parameter.name, parameter.lowerLimit
                )

                self.logger.debug(
                    '%s upper limit: %s', parameter.name , parameter.upperLimit
                )

        return parameter.value
        
    def getParameters(self):
        self.getParameter('brightnessCam')
        self.getParameter('dynamicMode')
        self.getParameter('shutterCam')
        self.getParameter('shutterTimeBaseCam')
        self.getParameter('brightnessProjector')
        self.getParameter('imageSizeX')
        self.getParameter('imageSizeY')

        self.getParameter('xScale')
        self.getParameter('yScale')
        self.getParameter('zScale')
        self.getParameter('xScaleRef')
        self.getParameter('yScaleRef')
        self.getParameter('maxProjectionAreaSizeX')
        self.getParameter('maxProjectionAreaSizeY')

        self.pScanner = {'name': 'Scanner parameters', 'type': 'group'}

        value = self.paraDict['brightnessCam'].value

        pCamSensitivity = {
            'name': 'camera sensitivity', 'type': 'int',
            'value': value, 'limits': (1, 20)
        }
        
        pCamDynamicMode = {
            'name': 'dynamic mode', 'type': 'int',
            'value': 0, 'limits': (0, 2)
        }
        
        pProjectorBrightness = {
            'name': 'projector brightness', 'type': 'bool',
            'value': True
        }
        
        pProjectorPattern = {
            'name': 'projection pattern', 'type': 'int',
            'value': 0, 'limits': (-1, 13)
        }

        self.pScanner['children'] = [
            pCamSensitivity,
            pCamDynamicMode,
            pProjectorBrightness,
            pProjectorPattern]


    def getMeasurements(self):
            
        Nc = self.LMI_DLL._GFM_GetNumMeasProgCatalogs()
        self.logger.info("Number of measurement program catalogs: Nc = %i", Nc)
           
        catalogName = self.LMI_DLL._GFM_GetMeasProgCatalogName(0)
        self.logger.info("Catalog name: %s", catalogName)

        Ni = self.LMI_DLL._GFM_GetNumberMeasProgItems(0)
        self.logger.info("Number of measurement programs: %i", Ni)

        itemName = self.LMI_DLL._GFM_GetMeasProgItemName(0, 0)
        self.logger.info("measurement program name: %s", itemName)

    def save(self, fullfile=None):

        if fullfile is None:
            brightnessCamera = self.getParameter('brightnessCam')
            dynamicMode = self.getParameter('dynamicMode')

            filename = ("test_C" + str(brightnessCamera) +
                "_D" + str(dynamicMode))

            fullfile = os.path.join(self.temp_path, filename)

        error = self.saveCam(fullfile, 2)
        error += self.saveScan(fullfile, 1)
        
        return error

    def saveScan(self, fullfile, fileFormat=0):
        colorMode = 0

        self.logger.info("Saving %s", fullfile)
        
        c_fullfile = c_char_p(fullfile.encode('utf-8'))
        
        error = self.LMI_DLL._GFM_SaveProfileData(c_fullfile, fileFormat,
                                                  colorMode)

        if error != 0:
            self.logger.error("Error: %i", error)

        return error
        

    def saveCam(self, fullfile, fileFormat = 2):
        '''
            fileFormat: {
                0: ".kam",
                1: ".bmp",
                2: ".jpg"
            }
        '''
        self.logger.info("Saving %s", fullfile)

        c_fullfile = c_char_p(fullfile.encode('utf-8'))
        
        error = self.LMI_DLL._GFM_SaveCameraData(c_fullfile, fileFormat)

        if error != 0:
            self.logger.error("Error: %i", error)
            
        return error
            

    def projectImage(self):
        Nx = 1624
        Ny = 1236
        Nxy = Nx * Ny
        img = (c_bool * Nxy)()
        self.logger.debug(type(img))
        sys.stdout.flush()

        for ij in range(Nxy):
            img[ij] = False
        
        for ix in range(Nx):
            for jy in range(Ny):
                ij = jy * Nx + ix
                
                if ix < 256 and jy < 256:
                    img[ij] = True
            
        
        # cast(img, POINTER(c_bool))        
        # timestamp(type(img))
        
        # mc.LMI_DLL._GFM_ProjectImage.argtypes = [c_bool]
        self.LMI_DLL._GFM_ProjectImage(byref(img))        

    
    def getCam(self):
        if hasattr(self.LMI_DLL._GFM_GetCameraImage, 'restype'):
            self.LMI_DLL._GFM_GetCameraImage.restype = POINTER(c_uint8)
            
        # LP_c_ubyte
        self.ptrCam = self.LMI_DLL._GFM_GetCameraImage(0)
            

    def startLiveImage(self, handle):
        self.LMI_DLL._GFM_StartLiveImage(handle, 0, 0, True)

    def continueLiveImage(self):
        liveOn = c_bool()
        self.LMI_DLL._GFM_HaltContinueLiveImage(byref(liveOn))

        self.liveOn = liveOn.value

###############################################################################
cShort = c_short()
cInt = c_int()
cLong = c_long()
cDouble = c_double()

###############################################################################
if __name__ == "__main__":

    # %% setup logger
    logging.basicConfig(
        format = '%(asctime)s %(levelname)s: %(message)s',
        level = logging.DEBUG,
        datefmt = '%Y-%m-%d %I:%M:%S'
    )
    
    fileHandler = logging.FileHandler('..\\output\\mikrocad.log', 'w')    
    
    logger = logging.getLogger("mikrocad")
    logger.addHandler(fileHandler)
    
    mc = MikroCAD('..\\config\\company_mikrocad.cfg')

    mc.loadFile("C:\\LMI\\Test\\test_C1_D0.omc")

    if mc.initMeasurement() == 0:
        mc.setParameter('brightnessCam', 10)
        
        mc.getParameters()
        mc.getMeasurements()
        mc.doMeasure()
    
        imageSizeX = mc.paraDict['imageSizeX'].value
        imageSizeY = mc.paraDict['imageSizeY'].value
        Nxy = imageSizeX * imageSizeY
        bmpPath = '..\\output'
    
        mc.LMI_DLL._GFM_ProjectPattern(0)

        mc.projectImage()

        mc.getCam()
    
        for i in range(1):
            bmpFile = 'hello_' + str(i) + '.bmp'
            input('Press key when ready to save next bitmap: ' + bmpFile)
            fullfile = os.path.join(bmpPath, bmpFile)
            mc.getCam()
            mc.saveCam(fullfile)
    
            shape = (imageSizeY, imageSizeX)
            cam = np.array(mc.ptrCam[0:Nxy], dtype = 'uint8').reshape(shape)
    
        mc.deinitMeasurement()
        print('Done.')
