# -*- coding: utf-8 -*-

### imports ###################################################################
import time
import unittest

### imports from ##############################################################
from mikrocad.mikrocad import MikroCAD

class MikroCAD_Test(unittest.TestCase):
    Nx = 1624
    Ny = 1236
    
    max_projection_area_x_size = 1.608
    max_projection_area_y_size = 1.787
    
    x_scale = 0.00305
    y_scale = 0.00305
    z_scale = 1E-4
    
    @classmethod
    def setUpClass(cls):
        cls.mc = MikroCAD('config\\company_mikrocad.cfg')
        
    def test_00_init(self):
        self.assertEqual(self.mc.initMeasurement(), 0)

    def test_01_available_parameters(self):
        parameter_id_dict = {
                11: True,
                12: True,
                13: False,
                14: False,
                15: False,
                16: True,
                21: True,
                22: True,
                111: True,
                112: True,
                113: True,
                114: True,
                115: True,
                201: True,
                202: True,
        }
        
        for parameter_id, value in parameter_id_dict.items():
            available = self.mc.measParameterAvailable(parameter_id)
            
            self.assertEqual(available, value)

    def test_02_camera(self):
        self.mc.brightnessCam = 7
        self.assertEqual(self.mc.brightnessCam, 7)
        
    def test_03_projector(self):
        self.mc.brightnessProjector = 0
        self.assertEqual(self.mc.brightnessProjector, 0)
        
        self.mc.brightnessProjector = 1
        self.assertEqual(self.mc.brightnessProjector, 1)

    def test_04_dynamic_mode(self):
        self.mc.dynamicMode = 2
        self.assertEqual(self.mc.dynamicMode, 2)
        
    def test_05_image_size(self):
        self.assertEqual(self.mc.x_size, self.Nx)
        self.assertEqual(self.mc.y_size, self.Ny)

    def test_06_scale(self):
        self.assertAlmostEqual(self.mc.x_scale, self.x_scale, places=5)
        self.assertAlmostEqual(self.mc.y_scale, self.y_scale, places=5)
        self.assertAlmostEqual(self.mc.z_scale, self.z_scale, places=5)

        self.assertAlmostEqual(self.mc.x_scale_ref, self.x_scale, places=5)
        self.assertAlmostEqual(self.mc.y_scale_ref, self.y_scale, places=5)

    def test_07_projection(self):
        self.assertAlmostEqual(
                self.mc.max_projection_area_x_size,
                self.max_projection_area_x_size, places=3)
        
        self.assertAlmostEqual(
                self.mc.max_projection_area_y_size,
                self.max_projection_area_y_size, places=3)

        for pattern in range(13):
            self.mc.projectionPattern = pattern
            time.sleep(0.5)
            self.assertEqual(self.mc.projectionPattern, pattern)

        self.mc.projectionPattern = 0
        
    def test_08_measure(self):
        self.assertEqual(self.mc.doMeasure(), 0)

    def test_09_camera(self):
        self.mc.getCam()
    
    def tearDownClass(self):
        self.mc.deinitMeasurement()

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
