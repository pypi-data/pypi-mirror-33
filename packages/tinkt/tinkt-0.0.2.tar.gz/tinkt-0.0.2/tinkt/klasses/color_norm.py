# -*- coding:utf-8 -*-

import six
import numpy as np
from matplotlib import colors as mpl_colors


class ColorNorm(object):
    def __init__(self, name,
                 type, para):
        self.name = name
        self.type = type

        self.norm = None
        if self.type == 'BoundaryNorm':
            if isinstance(para, (list, tuple, np.ndarray)):
                self.norm = mpl_colors.BoundaryNorm(para, len(para)-1)
            elif isinstance(para, dict):
                self.norm = mpl_colors.BoundaryNorm(**para)
            else:
                raise ValueError("Bad para for BoundaryNorm: {}".format(para))

    def generate(self, *args):
        return self.norm