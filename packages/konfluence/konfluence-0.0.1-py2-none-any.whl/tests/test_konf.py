#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys
from matplotlib import cm as mpl_cm
from metlib.color import cmap_utils
from metlib.shell.fileutil import *

from konfluence import Konfluence


CM_FAMILIES = {
    "mpl": mpl_cm
}


class ColorMap(object):
    def __init__(self, name, type='normal', base_cmap_name='jet', clip_min=0.0, clip_max=1.0):
        self.name = name
        self.type = type
        self.base_cmap_name = base_cmap_name

        self.base_cmap = cmap_utils.get_cmap((getattr(mpl_cm, self.base_cmap_name), (clip_min, clip_max)))

    def vary(self, clip_min=0.0, clip_max=1.0):
        clip_min = float(clip_min)
        clip_max = float(clip_max)
        return cmap_utils.get_cmap((self.base_cmap, (clip_min, clip_max)))


kfl = Konfluence()
kfl.register('colormap', klass=ColorMap, generator='vary')

jet = mpl_cm.jet
print jet(0.0), jet(1.0)

cmap1 = kfl.get('colormap/jester')
print cmap1(0.0), cmap1(1.0)

cmap2 = kfl.get('colormap/test:0.4:0.6')
print cmap2(0.0), cmap2(1.0)
