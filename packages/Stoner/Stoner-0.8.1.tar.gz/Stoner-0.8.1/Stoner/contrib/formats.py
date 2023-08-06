# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 19:08:02 2017

@author: phygbu
"""

import numpy as _np_

from Stoner.Core import DataFile,StonerLoadError

class LakeShoreVSM(DataFile):
    """Lakeshore VSM File Format loader controubted by Vince West <dvincentwest@gmail.com>"""
    priority = 32
    patterns = ["*.txt"]  # Recognised filename patterns

    @classmethod
    def from_file(cls, filename):
        data = _np_.loadtxt(filename, skiprows=12)
        return cls(data, column_headers=["Field (G)", "moment (emu)"], setas="xy")

    def _load(self, filename, *args):
        try:
            self.data = _np_.loadtxt(filename, skiprows=12)
            self.column_headers = ["Field (G)", "moment (emu)"]
            self.setas = "xy"
        except Exception:
            raise StonerLoadError

        return self

