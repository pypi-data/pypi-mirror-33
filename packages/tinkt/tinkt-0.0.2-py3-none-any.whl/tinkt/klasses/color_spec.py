# -*- coding:utf-8 -*-

import six
from konfluence import Konfluence
import numpy as np
from matplotlib import colors as mpl_colors
from matplotlib import pyplot as plt


class ColorSpec(object):
    konf = Konfluence()

    def __init__(self, name, cmap, norm=None, categories=None, label=None):
        self.name = name
        try:
            if isinstance(cmap, mpl_colors.Colormap):
                self.cmap = cmap
            elif isinstance(cmap, six.string_types):
                self.cmap = self.konf.get(cmap, 'default')
            elif isinstance(cmap, (list, tuple, np.ndarray)):
                self.cmap = mpl_colors.ListedColormap(cmap)
            else:
                raise ValueError
        except Exception as e:
            raise ValueError(u'Cannot parse cmap: {}'.format(cmap))

        try:
            if norm is None or isinstance(norm, mpl_colors.Normalize):
                self.norm = norm
            elif isinstance(norm, six.string_types):
                self.norm = self.konf['norm']
            elif isinstance(norm, (list, tuple, np.ndarray)):
                self.norm = mpl_colors.BoundaryNorm(norm, len(norm)-1, clip=False)
            else:
                raise ValueError
        except Exception as e:
            raise ValueError(u'Cannot parse norm: {}'.format(norm))

        self.categories = categories

        self.label = label

    def colorbar(self, **kwargs):
        kwargs.update({})
        clb = plt.colorbar(**kwargs)
        if self.label:
            clb.set_label(self.label)
        return clb
