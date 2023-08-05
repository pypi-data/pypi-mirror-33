"""
oRGB
====

Color conversion between RGB, sRGB and oRGB and also RGB and oRGB random generation.

Converting colors
-----------------
sRGB_to_RGB(sR,sG,sB)
RGB_to_sRGB(R,G,B)
RGB_to_oRGB(R,G,B)
oRGB_to_RGB(oR,oG,oB)
sRGB_to_oRGB(sR,sG,sB)
oRGB_to_sRGB(oR,oG,oB)

Random color generation
-----------------------
randcolor_RGB()
randcolor_oRGB()
"""

import math
import numpy
import random

class _Converter:
    """Convert colors from RGB/sRGB to oRGB and vice versa""" 
    _matrix_to_LCC = 0.0
    _matrix_to_sRGB = 0.0
    def __init__(self):
        self._matrix_to_LCC = numpy.matrix([[0.2990, 0.5870, 0.1140],[0.5, 0.5, -1.0],[0.866, -0.866, 0]])
        self._matrix_to_sRGB = numpy.matrix([[1.0, 0.1140, 0.7436],[1.0, 0.1140, -0.4111],[1.0, -0.886, 0.1663]])

    def sRGB_to_RGB(self,sR,sG,sB):
        sR = abs(sR)
        sG = abs(sG)
        sB = abs(sB)
        return [math.pow(sR,2.2),math.pow(sG,2.2),math.pow(sB,2.2)]

    def RGB_to_sRGB(self,R,G,B):
        return [math.pow(R,1.0/2.2),math.pow(G,1.0/2.2),math.pow(B,1.0/2.2)]

    def RGB_to_oRGB(self,R,G,B):
        sR,sG,sB = self.RGB_to_sRGB(R,G,B)
        return self.sRGB_to_oRGB(sR,sG,sB)

    def oRGB_to_RGB(self,L,CYB,CRG):
        sR,sG,sB = self.oRGB_to_sRGB(L,CYB,CRG)
        return self.sRGB_to_RGB(sR,sG,sB)

    def sRGB_to_oRGB(self,sR,sG,sB):
        L,C1,C2 = self._sRGB_to_LCC(sR,sG,sB)
        return self._LCC_to_LCYBCRG(L,C1,C2)

    def oRGB_to_sRGB(self,L,CYB,CRG):
        L,C1,C2 = self._LCYBCRG_to_LCC(L,CYB, CRG)
        return self._LCC_to_sRGB(L,C1,C2)

    def _sRGB_to_LCC(self,R,G,B):
        RGB = numpy.matrix([[R],[G],[B]])
        LCC = self._matrix_to_LCC * RGB;
        LCC = numpy.array(LCC.reshape(3,))[0]
        return [LCC[0], LCC[1], LCC[2]]

    def _LCC_to_sRGB(self,L,C1,C2):
        LCC = numpy.matrix([[L],[C1],[C2]])
        sRGB = self._matrix_to_sRGB * LCC;
        sRGB = numpy.array(sRGB.reshape(3,))[0]
        return [sRGB[0], sRGB[1], sRGB[2]]

    def _LCC_to_LCYBCRG(self,L,C1,C2):
        a = self._getAngleLCYBCRG(C1, C2);
        R = self._rotationMatrix(a)
        CC = R * numpy.matrix([[C1],[C2]])
        CC = numpy.array(CC.reshape(2,))[0]
        return [L, CC[0], CC[1]]

    def _LCYBCRG_to_LCC(self,L,CYB,CRG):
        a = self._getAngleLCC(CYB,CRG)
        R = self._rotationMatrix(a)
        CC = R * numpy.matrix([[CYB],[CRG]])
        CC = numpy.array(CC.reshape(2,))[0]
        return [L, CC[0], CC[1]]

    def _getAngleLCYBCRG(self,C1,C2):
        t = math.fabs(math.atan2(C2,C1))
        ot = self._ot(t)
        a = ot - t
        if C2 < 0:
            a = - a
        return a

    def _getAngleLCC(self,CYB,CRG):
        ot = math.fabs(math.atan2(CRG,CYB))
        t = self._t(ot)
        a = ot - t
        if CRG > 0:
            a = - a
        return a

    def _ot(self,t):
        if t == 0:
            ot = 0
        elif t < math.pi / 3:
            ot = (3.0/2.0) * t
        else:
            ot = (math.pi / 2) + (3.0/4.0) * (t - math.pi/3)
        return ot

    def _t(self,ot):
        if ot == 0:
            t = 0
        elif ot < math.pi / 2:
            t = (2.0/3.0) * ot
        else:
            t = (math.pi / 3) + (4.0/3.0) * (ot - math.pi/2)
        return t

    def _rotationMatrix(self, a):
        return numpy.matrix([[math.cos(a), -math.sin(a)],
            [math.sin(a), math.cos(a)]])

_converter = _Converter()

def sRGB_to_RGB(sR,sG,sB):
    """ Convert sRGB color into RGB color.

    Parameterss
    -----------
    sR : float
        R component of the color as a float inside interval [0-1]
    sG : float
        G component of the color as a float inside interval [0-1]
    sB : float
        B component of the color as a float inside interval [0-1]        

    Returns
    -------
    list : [R, G, B]
        A list with three elements, wich represents a color in RGB format.
        Elements are float values inside interval [0-1].
    """
    return _converter.sRGB_to_RGB(sR,sG,sB)

def RGB_to_sRGB(R,G,B):
    """ Convert RGB color into sRGB color.

    Parameterss
    -----------
    R : float
        R component of the color as a float inside interval [0-1]
    G : float
        G component of the color as a float inside interval [0-1]
    B : float
        B component of the color as a float inside interval [0-1]        

    Returns
    -------
    list : [sR, sG, sB]
        A list with three elements, wich represents a color in standard RGB format.
        Elements are float values inside interval [0-1].
    """
    _converter.RGB_to_sRGB(R,G,B)

def RGB_to_oRGB(R,G,B):
    """ Convert RGB color into oRGB color.

    Parameterss
    -----------
    R : float
        R component of the color as a float inside interval [0-1]
    G : float
        G component of the color as a float inside interval [0-1]
    B : float
        B component of the color as a float inside interval [0-1]        

    Returns
    -------
    list : [oR, oG, oB]
        A list with three elements, wich represents a color in oRGB format.
        Elements are float values inside interval [0-1].
    """
    return _converter.RGB_to_oRGB(R,G,B)

def oRGB_to_RGB(oR,oG,oB):
    """ Convert oRGB color into RGB color.

    Parameterss
    -----------
    oR : float
        R component of the color as a float inside interval [0-1]
    oG : float
        G component of the color as a float inside interval [0-1]
    oB : float
        B component of the color as a float inside interval [0-1]        

    Returns
    -------
    list : [R, G, B]
        A list with three elements, wich represents a color in oRGB format.
        Elements are float values inside interval [0-1].
    """
    return _converter.oRGB_to_RGB(oR,oG,oB)

def sRGB_to_oRGB(sR,sG,sB):
    """ Convert sRGB color into oRGB color.

    Parameterss
    -----------
    sR : float
        R component of the color as a float inside interval [0-1]
    sG : float
        G component of the color as a float inside interval [0-1]
    sB : float
        B component of the color as a float inside interval [0-1]        

    Returns
    -------
    list : [oR, oG, oB]
        A list with three elements, wich represents a color in oRGB format.
        Elements are float values inside interval [0-1].
    """
    return _converter.sRGB_to_oRGB(sR,sG,sB)

def oRGB_to_sRGB(oR,oG,oB):
    """ Convert oRGB color into sRGB color.

    Parameterss
    -----------
    oR : float
        R component of the color as a float inside interval [0-1]
    oG : float
        G component of the color as a float inside interval [0-1]
    oB : float
        B component of the color as a float inside interval [0-1]        

    Returns
    -------
    list : [sR, sG, sB]
        A list with three elements, wich represents a color in sRGB format.
        Elements are float values inside interval [0-1].
    """
    return _converter.oRGB_to_sRGB(oR,oG,oB)

def randcolor_RGB():
    """ Generate a random color in RGB color space.

    Returns
    -------
    list : [R, G, B]
        A list with three elements, wich represents a color in RGB format.
        Elements are float values inside interval [0-1].
    """
    import random
    R = random.random()
    G = random.random()
    B = random.random()
    return[R,G,B]

def randcolor_oRGB():
    """ Generate a random color in oRGB color space.

    Returns
    -------
    list : [oR, oG, oB]
        A list with three elements, wich represents a color in RGB format.
        Elements are float values inside interval [0-1].
    """
    R, G, B = randcolor_RGB()
    return RGB_to_oRGB(R,G,B)
