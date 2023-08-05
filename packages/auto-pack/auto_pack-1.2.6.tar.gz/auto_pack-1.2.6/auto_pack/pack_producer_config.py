#!/usr/bin/env python
# -*- coding: utf-8 -*-
from producer import FlavorApkProducer

FILE_FLAVORS_UPG = 'flavors-upg.txt'
LAIFENQIAPP = 'laifenqiApp'

OUTPUT_BASE_DIR = '/Volumes/MwpExtVolume/qudian'
OUTPUT_BASE_DIR = ''


def getGuanWangProduer():
    return FlavorApkProducer().fromFile(FILE_FLAVORS_UPG).setOutputBaseDir(OUTPUT_BASE_DIR)
