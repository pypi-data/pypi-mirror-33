# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import os
import unittest

###############################################################################
from mikrocad.fd3 import FD3Reader
from some_math.fit_plane import fitPlane

###############################################################################
class FD3Test(unittest.TestCase):
    def test_00_FD3Reader(self):
        testdir = os.path.abspath(os.path.dirname(__file__))
        basedir = os.path.abspath(os.path.join(testdir, '..'))
        datadir = os.path.join(basedir, 'data')

        filename = 'mounting_plate.fd3'
        fullfile = os.path.join(datadir, filename)
        
        FD3Test.fd3 = FD3Reader(fullfile)

        Nx = FD3Test.fd3.Nx
        self.assertEqual(Nx, 1624)
        
        Ny = FD3Test.fd3.Ny
        self.assertEqual(Ny, 1236)
        
        i_nan = FD3Test.fd3.i_nan
        self.assertEqual(i_nan, -10010)

        dx = FD3Test.fd3.dx
        self.assertAlmostEqual(dx, 0.00305, places=5)

        dy = FD3Test.fd3.dy
        self.assertAlmostEqual(dy, 0.00305, places=5)
        
        dz = FD3Test.fd3.dz
        self.assertAlmostEqual(dz, 1E-4, places=4)

    def test_01_plane(self):
        x = FD3Test.fd3.x
        y = FD3Test.fd3.y

        n = np.array([-0.0108, 0.7620, 0.6475])

        X, Y = np.meshgrid(x, y, indexing='ij')
        Z = FD3Test.fd3.Z

        ij = np.where(np.isfinite(Z))

        dataPoints = np.vstack((X[ij], Y[ij], Z[ij])).T
        n_hat, a_hat = fitPlane(dataPoints)
        
        self.assertAlmostEqual(a_hat, 1.063, places=3)

        check = np.allclose(n_hat, n, atol=0.0001)
        self.assertTrue(check)
        
    def test_02_survey_plot(self):
        FD3Test.fd3.get_survey_plot()
