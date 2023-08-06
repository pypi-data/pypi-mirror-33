# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import os
import struct

### imports from ##############################################################
from PIL import Image

###############################################################################
class KamReader:
    def __init__(self, filename):
        self.kamFullfile = filename
        self.kamFile = open(filename, 'rb')
        self.data = self.kamFile.read()
        self.kamFile.close()

        Ncol = 1624
        Nrow = 1236
    
        self.Image = np.zeros((Ncol, Nrow), dtype = 'uint8')
        
        offset = len(self.data) - Ncol * Nrow * 2
        
        for iRow in range(Nrow):    
    
            pos = offset + 2 * iRow * Ncol
       
            row = self.readShort(pos, Ncol)
    
            # self.Image[:, Nrow - iRow - 1] = row
            self.Image[:, iRow] = row

    def readShort(self, i1, N):
        i2 = i1 + 2 * N
            
        # unpack big-endinan unsigned short
        formatString = '<' + str(N) + 'H'
        value = struct.unpack(formatString, self.data[i1:i2])
        return value

    def kam2png(self, filename = None):

        if filename is None:
            filename = self.kamFullfile
            pngFile = filename.split('.', 1)[0] + '.png'
            pngFullfile = os.path.join(filename, pngFile)
        else:
            pngFullfile = filename
        
        img = Image.fromarray(self.Image)
        img.save(pngFullfile)
