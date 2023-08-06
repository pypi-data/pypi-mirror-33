import os
from dplus.Amplitudes import Amplitude
from dplus.State import State
from dplus.CalculationRunner import LocalRunner
from dplus.CalculationInput import GenerateInput
import math

class SymmetricSlab:
    def __init__(self):
        self.scale=1
        self.background=0
        self.xDomain=10
        self.yDomain=10
        self.ED=[333, 280]
        self.width=[0,1]
    @property
    def nLayers(self):
        return len(self.ED)

    def calculate(self, q, theta, phi):
        def closeToZero(x):
            return (math.fabs(x) < 100.0 * 2.2204460492503131E-16)
        from dplus.Amplitudes import sph2cart
        from math import sin, cos
        from numpy import sinc
        import numpy as np
        qx, qy, qz = sph2cart(q, theta, phi)
        res= 0+0j
        im= 0+1j

        if(closeToZero(qz)):
            for i in range(self.nLayers):
                res += (self.ED[i] - self.ED[0]) * 2. * (self.width[i] - self.width[i - 1])
            return res * 4. * sinc(qx * self.xDomain) * self.xDomain * sinc(qy * self.yDomain) * self.yDomain

        prevSin = 0.0
        currSin=0.0
        for i in range(1, self.nLayers):
            currSin = sin(self.width[i] * qz)
            res += (self.ED[i] - self.ED[0]) * 2. * (currSin - prevSin) / qz
            prevSin = currSin
        res *= 4. * sinc(qx * self.xDomain) * self.xDomain * sinc(qy * self.yDomain) * self.yDomain
        return res * self.scale + self.background #Multiply by scale and add background

sphere = SymmetricSlab()
a = Amplitude(5, 50)
a.create_grid(sphere.calculate)
new_file_path = os.path.join(r"C:\Users\devora\Sources\temp", 'slab.amp')
a.save(new_file_path)
s = State()
amp_model = s.add_amplitude(a)
amp_model.centered = True
input = GenerateInput(s)
runner = LocalRunner()
result = runner.generate(input)
