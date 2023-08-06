# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 09:47:02 2015

@author: twagner
"""

### imports ###################################################################
import matplotlib.pyplot as plt
import numpy as np
import struct

###############################################################################
class FD3Reader:
    def __init__(self, filename):
        self.kamFullfile = filename
        self.kamFile = open(filename, 'rb')
        self.data = self.kamFile.read()
        self.kamFile.close()

        self.readHeader()
        
        Ncol = self.Nx
        Nrow = self.Ny
    
        self.Image = np.zeros((Ncol, Nrow), dtype = 'int16')
        
        offset = len(self.data) - Ncol * Nrow * 2
        
        for iRow in range(Nrow):    
    
            pos = offset + 2 * iRow * Ncol
       
            row = self.readShort(pos, Ncol)
    
            self.Image[:, iRow] = row

        self.i_nan = np.min(self.Image)

        self.Z = self.dz * self.Image
        self.Z[self.Image == self.i_nan] = np.NaN


    def readShort(self, i1, N):
        i2 = i1 + 2 * N
            
        # unpack big-endinan unsigned short
        littleEndian = '<'
        short = 'h'
        formatString = littleEndian + str(N) + short
        value = struct.unpack(formatString, self.data[i1:i2])
        return value

    '''
    def readUnsignedShort(self, i1, N):
        i2 = i1 + 2 * N
            
        # unpack big-endinan unsigned short
        littleEndian = '<'
        ushort = 'H'
        formatString = littleEndian + str(N) + ushort
        value = struct.unpack(formatString, self.data[i1:i2])
        return value


    def readInteger(self, i1, N):
        i2 = i1 + 4 * N
            
        # unpack big-endinan unsigned short
        littleEndian = '<'
        integer = 'i'
        formatString = littleEndian + str(N) + integer
        value = struct.unpack(formatString, self.data[i1:i2])
        return value
    '''
    

    def readDouble(self, i1, N):
        i2 = i1 + 8 * N
            
        # unpack big-endinan unsigned short
        littleEndian = '<'
        double = 'd'
        formatString = littleEndian + str(N) + double
        value = struct.unpack(formatString, self.data[i1:i2])
        return value


    def readHeader(self):
        iStart = 0
        headerDouble = np.array(self.readDouble(iStart, 28))
        headerShort = np.array(self.readShort(iStart, 112))

        self.dx = headerDouble[17]
        self.dy = headerDouble[21]
        self.dz = headerDouble[25]
        self.scale = (self.dx, self.dy, self.dz)
    
        self.Nx = headerShort[56]
        self.Ny = headerShort[58]
        self.shape = (self.Nx, self.Ny)

        self.x = self.dx * np.arange(self.Nx)
        self.y = self.dy * np.arange(self.Ny)
        
        self.x_max = self.x[-1]
        self.y_max = self.y[-1]
        self.extent = [0, self.x_max, 0, self.y_max]


    def get_survey_plot(self):
        Nx2 = self.Nx // 2
        z = self.Z[Nx2, :]
        
        fig, ax = plt.subplots(figsize=(5, 3))

        plt.subplot(1,2,1)

        plt.imshow(
            self.Image.T,
            cmap='gray', extent=self.extent, origin='lower')

        plt.xlabel('$x$ [mm]')
        plt.ylabel('$y$ [mm]')
    
        ax = plt.subplot(1,2,2)
        plt.plot(self.y, z, '.')
        plt.xlim(0, 4)
        plt.ylim(-1, 1)
        ax.set_aspect('equal')
        plt.xlabel('$y$ [mm]')
        plt.ylabel('$z$ [mm]')
        plt.tight_layout()
        
        return fig
