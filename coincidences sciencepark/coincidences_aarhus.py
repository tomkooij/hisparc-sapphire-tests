# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 13:42:55 2014

@author: Tom
"""

import tables
import datetime
import sapphire.esd

data = tables.open_file('data_coincidences.h5', 'w')
sapphire.esd.download_coincidences(data, cluster='Aarhus',
            start=datetime.datetime(2014, 9, 1),
            end=datetime.datetime(2014, 9, 2), n=3)
data.close()
