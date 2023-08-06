# -*- coding:utf-8 -*-

import six
from matplotlib import colors as mpl_colors
import tinkt.cmap_utils


class ColorMap(object):
    def __init__(self, name,
                 type='Normal',
                 base_cmap_name=None,
                 clip_min=None, clip_max=None,
                 N=None,
                 sample_points=None,
                 colors=None,
                 bad=None, over=None, under=None
                 ):
        self.name = name
        self.type = type
        if self.type == 'Normal':
            self.base_cmap = tinkt.cmap_utils.get_cmap(base_cmap_name,
                                                       clip_min=clip_min, clip_max=clip_max,
                                                       N=N,
                                                       sample_points=sample_points,
                                                       bad=bad, over=over, under=under)
        elif self.type == 'Listed':
            if colors:
                self.base_cmap = mpl_colors.ListedColormap(colors, name=self.name, N=N)
            else:
                raise NotImplementedError()

    def generate(self, *args):
        if self.type == 'Normal':
            return self._gen_normal(*args)
        elif self.type == 'Listed':
            return self._gen_listed(*args)

    def _gen_normal(self, clip_min=None, clip_max=None, N=None, *args, **kwargs):
        return tinkt.cmap_utils.get_cmap(self.base_cmap, clip_min=clip_min, clip_max=clip_max, N=N)

    def _gen_listed(self, *args):
        # TODO: implement
        return self.base_cmap

