# -*- coding:utf-8 -*-

import six
import numpy as np
from numpy import ma
from matplotlib import colors as mpl_colors


class DecreasableBoundaryNorm(mpl_colors.BoundaryNorm):
    """
    Generate a colormap index based on discrete intervals.

    Unlike :class:`Normalize` or :class:`LogNorm`,
    :class:`BoundaryNorm` maps values to integers instead of to the
    interval 0-1.

    Mapping to the 0-1 interval could have been done via
    piece-wise linear interpolation, but using integers seems
    simpler, and reduces the number of conversions back and forth
    between integer and floating point.
    """
    def __init__(self, boundaries, ncolors, clip=False):
        """
        *boundaries*
            a monotonically increasing/decreasing sequence
        *ncolors*
            number of colors in the colormap to be used

        If::

            b[i] <= v < b[i+1]

        then v is mapped to color j;
        as i varies from 0 to len(boundaries)-2,
        j goes from 0 to ncolors-1.

        Out-of-range values are mapped
        to -1 if low and ncolors if high; these are converted
        to valid indices by
        :meth:`Colormap.__call__` .
        If clip == True, out-of-range values
        are mapped to 0 if low and ncolors-1 if high.
        """
        self.clip = clip
        if boundaries[0] <= boundaries[-1]:
            self.increasing = True
            self.vmin = boundaries[0]
            self.vmax = boundaries[-1]
        else:
            self.increasing = False
            self.vmin = boundaries[-1]
            self.vmax = boundaries[0]

        self.boundaries = np.asarray(boundaries)
        self.N = len(self.boundaries)
        self.Ncmap = ncolors
        if self.N - 1 == self.Ncmap:
            self._interp = False
        else:
            self._interp = True

    def __call__(self, value, clip=None):
        if clip is None:
            clip = self.clip

        xx, is_scalar = self.process_value(value)
        mask = ma.getmaskarray(xx)
        xx = np.atleast_1d(xx.filled(self.vmax + 1))
        if clip:
            np.clip(xx, self.vmin, self.vmax, out=xx)
            max_col = self.Ncmap - 1
        else:
            max_col = self.Ncmap
        iret = np.zeros(xx.shape, dtype=np.int16)
        for i, b in enumerate(self.boundaries):
            if self.increasing:
                iret[xx >= b] = i
            else:
                iret[xx <= b] = i
        if self._interp:
            scalefac = float(self.Ncmap - 1) / (self.N - 2)
            iret = (iret * scalefac).astype(np.int16)
        if self.increasing:
            iret[xx < self.vmin] = -1
            iret[xx >= self.vmax] = max_col
        else:
            iret[xx > self.vmax] = -1
            iret[xx <= self.vmin] = max_col
        ret = ma.array(iret, mask=mask)
        if is_scalar:
            ret = int(ret[0])  # assume python scalar
        return ret


class ColorNorm(object):
    def __init__(self, name,
                 type, para):
        self.name = name
        self.type = type

        self.norm = None
        if self.type == 'BoundaryNorm':
            if isinstance(para, (list, tuple, np.ndarray)):
                self.norm = DecreasableBoundaryNorm(para, len(para)-1)
            elif isinstance(para, dict):
                self.norm = DecreasableBoundaryNorm(**para)
            else:
                raise ValueError("Bad para for BoundaryNorm: {}".format(para))

    def generate(self, *args):
        return self.norm